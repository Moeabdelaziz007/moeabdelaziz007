import { EventEmitter } from 'events';
import { WebClient } from '@slack/web-api';
import { App } from '@slack/bolt';
import Database from 'better-sqlite3';
import { z } from 'zod';
import pino from 'pino';

const logger = pino({ level: 'info' });

const MessageSchema = z.object({
  ts: z.string(),
  channel: z.string(),
  user: z.string(),
  text: z.string(),
  type: z.enum(['message', 'file', 'file_share', 'bot_message', 'system']),
  subtype: z.string().optional(),
  files: z.array(z.any()).optional(),
  reactions: z.array(z.any()).optional(),
  reply_count: z.number().optional(),
  reply_users: z.array(z.string()).optional(),
  reply_users_count: z.number().optional(),
  thread_ts: z.string().optional(),
  parent_user_id: z.string().optional(),
  arabic_tokens: z.array(z.string()).optional(),
  arabic_entities: z.array(z.object({ type: z.string(), value: z.string() })).optional(),
  hijri_date: z.string().optional(),
});

const ChannelSchema = z.object({
  id: z.string(),
  name: z.string(),
  is_channel: z.boolean(),
  is_group: z.boolean(),
  is_im: z.boolean(),
  is_mpim: z.boolean(),
  is_private: z.boolean(),
  is_archived: z.boolean(),
  is_general: z.boolean(),
  name_normalized: z.string().optional(),
  arabic_name: z.string().optional(),
  purpose: z.object({ value: z.string() }).optional(),
  topic: z.object({ value: z.string() }).optional(),
});

export class SlacCrawl extends EventEmitter {
  private app: App;
  private web: WebClient;
  private db: Database.Database;
  private config: any;
  private isRunning: boolean = false;
  private syncInterval: NodeJS.Timeout | null = null;
  private messageQueue: any[] = [];

  constructor(config: {
    dbPath: string;
    botToken: string;
    appToken: string;
    signingSecret: string;
    language: string;
    hijriCalendar: boolean;
    jaisEmbeddings: boolean;
    apiKey: string;
  }) {
    super();
    this.config = config;
    this.db = new Database(config.dbPath);
    this.initDatabase();
    this.initSlack();
  }

  private initDatabase() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        ts TEXT PRIMARY KEY,
        channel_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        text TEXT,
        type TEXT NOT NULL,
        subtype TEXT,
        files TEXT,
        reactions TEXT,
        reply_count INTEGER DEFAULT 0,
        reply_users TEXT,
        reply_users_count INTEGER DEFAULT 0,
        thread_ts TEXT,
        parent_user_id TEXT,
        arabic_tokens TEXT,
        arabic_entities TEXT,
        hijri_date TEXT,
        created_at INTEGER DEFAULT (strftime('%s', 'now'))
      );

      CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel_id);
      CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(ts);
      CREATE INDEX IF NOT EXISTS idx_messages_hijri ON messages(hijri_date);

      CREATE TABLE IF NOT EXISTS channels (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        is_channel INTEGER DEFAULT 0,
        is_group INTEGER DEFAULT 0,
        is_im INTEGER DEFAULT 0,
        is_mpim INTEGER DEFAULT 0,
        is_private INTEGER DEFAULT 0,
        is_archived INTEGER DEFAULT 0,
        is_general INTEGER DEFAULT 0,
        name_normalized TEXT,
        arabic_name TEXT,
        purpose TEXT,
        topic TEXT,
        created_at INTEGER DEFAULT (strftime('%s', 'now'))
      );

      CREATE TABLE IF NOT EXISTS crawl_state (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at INTEGER DEFAULT (strftime('%s', 'now'))
      );
    `);

    this.db.pragma('journal_mode = WAL');
  }

  private initSlack() {
    this.app = new App({
      token: this.config.botToken,
      signingSecret: this.config.signingSecret,
      appToken: this.config.appToken,
    });

    this.web = new WebClient(this.config.botToken);
  }

  async initialize(): Promise<void> {
    logger.info('Initializing SlacCrawl-AR...');
    logger.info('SlacCrawl-AR initialized');
  }

  async syncOnce(): Promise<{ messages: number; channels: number }> {
    logger.info('Starting Slack sync...');
    const stats = { messages: 0, channels: 0 };
    
    try {
      const channels = await this.web.conversations.list({ exclude_archived: true, limit: 200 });
      for (const channel of channels.channels || []) {
        await this.syncChannel(channel);
        stats.channels++;
      }
      
      this.setCrawlState('last_sync', new Date().toISOString());
      logger.info({ ...stats }, 'Sync complete');
    } catch (error) {
      logger.error({ error }, 'Sync failed');
    }
    
    return stats;
  }

  private async syncChannel(channel: any): Promise<void> {
    try {
      const history = await this.web.conversations.history({
        channel: channel.id,
        limit: 100
      });

      for (const msg of history.messages || []) {
        await this.processMessage(msg, channel.id);
      }
    } catch (error) {
      logger.warn({ channel: channel.id, error }, 'Failed to sync channel');
    }
  }

  private async processMessage(msg: any, channelId: string): Promise<void> {
    try {
      const messageData = {
        ts: msg.ts,
        channel_id: channelId,
        user_id: msg.user || msg.bot_id || 'unknown',
        text: msg.text || '',
        type: msg.type || 'message',
        subtype: msg.subtype,
        files: JSON.stringify(msg.files || []),
        reactions: JSON.stringify(msg.reactions || []),
        reply_count: msg.reply_count || 0,
        reply_users: JSON.stringify(msg.reply_users || []),
        reply_users_count: msg.reply_users_count || 0,
        thread_ts: msg.thread_ts,
        parent_user_id: msg.parent_user_id,
        arabic_tokens: JSON.stringify([]),
        arabic_entities: JSON.stringify([]),
        hijri_date: null,
      };

      // Arabic processing
      if (msg.text) {
        // Arabic tokenization would go here
        messageData.arabic_tokens = JSON.stringify([]);
        messageData.arabic_entities = JSON.stringify([]);
      }

      const stmt = this.db.prepare(`
        INSERT OR REPLACE INTO messages 
        (ts, channel_id, user_id, text, type, subtype, files, reactions, reply_count, reply_users, reply_users_count, thread_ts, parent_user_id, arabic_tokens, arabic_entities, hijri_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);
      
      stmt.run(
        messageData.ts,
        messageData.channel_id,
        messageData.user_id,
        messageData.text,
        messageData.type,
        messageData.subtype,
        messageData.files,
        messageData.reactions,
        messageData.reply_count,
        messageData.reply_users,
        messageData.reply_users_count,
        messageData.thread_ts,
        messageData.parent_user_id,
        messageData.arabic_tokens,
        messageData.arabic_entities,
        messageData.hijri_date
      );
    } catch (error) {
      logger.warn({ msg, error }, 'Failed to process message');
    }
  }

  async syncOnce(): Promise<{ messages: number; channels: number }> {
    logger.info('Starting Slack sync...');
    const stats = { messages: 0, channels: 0 };
    
    try {
      await this.syncOnce();
      logger.info({ ...stats }, 'Sync complete');
    } catch (error) {
      logger.error({ error }, 'Sync failed');
    }
    
    return stats;
  }

  async startDaemon(intervalMs = 300000): Promise<void> {
    this.isRunning = true;
    logger.info({ intervalMs }, 'Starting SlacCrawl daemon');
    
    await this.syncOnce();
    
    this.syncInterval = setInterval(async () => {
      try {
        await this.syncOnce();
      } catch (error) {
        logger.error({ error }, 'Sync failed');
      }
    }, intervalMs);
  }

  stopDaemon(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
    this.isRunning = false;
    logger.info('Daemon stopped');
  }

  private getCrawlState(key: string): string | null {
    const stmt = this.db.prepare('SELECT value FROM crawl_state WHERE key = ?');
    const row = stmt.get(key) as { value: string } | undefined;
    return row?.value || null;
  }

  private setCrawlState(key: string, value: string): void {
    const stmt = this.db.prepare(`
      INSERT INTO crawl_state (key, value, updated_at)
      VALUES (?, ?, strftime('%s', 'now'))
      ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
    `);
    stmt.run(key, value);
  }

  async shutdown(): Promise<void> {
    this.stopDaemon();
    logger.info('SlacCrawl-AR shutdown complete');
  }
}

export { SlacCrawl };