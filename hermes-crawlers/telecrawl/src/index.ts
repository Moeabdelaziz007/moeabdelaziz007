import { EventEmitter } from 'events';
import { TelegramClient } from 'telegram';
import { StringSession } from 'telegram/sessions';
import { Api } from 'telegram/tl';
import Database from 'better-sqlite3';
import { z } from 'zod';
import pino from 'pino';

const logger = pino({ level: 'info' });

const MessageSchema = z.object({
  id: z.number(),
  peer_id: z.any(),
  date: z.number(),
  message: z.string(),
  media: z.any().optional(),
  from_id: z.any().optional(),
  fwd_from: z.any().optional(),
  reply_to: z.any().optional(),
  views: z.number().optional(),
  forwards: z.number().optional(),
  replies: z.any().optional(),
  edit_date: z.number().optional(),
  post_author: z.string().optional(),
  grouped_id: z.number().optional(),
  restriction_reason: z.any().optional(),
  ttl_period: z.number().optional(),
  arabic_tokens: z.array(z.string()).optional(),
  arabic_entities: z.array(z.object({ type: z.string(), value: z.string() })).optional(),
  hijri_date: z.string().optional(),
});

const DialogSchema = z.object({
  id: z.number(),
  title: z.string(),
  username: z.string().optional(),
  participants_count: z.number().optional(),
  is_channel: z.boolean().optional(),
  is_group: z.boolean().optional(),
  is_user: z.boolean().optional(),
  unread_count: z.number().optional(),
  unread_mentions_count: z.number().optional(),
  is_marked_unread: z.boolean().optional(),
  is_muted: z.boolean().optional(),
  is_pinned: z.boolean().optional(),
  folder_id: z.number().optional(),
  top_message: z.number().optional(),
  read_inbox_max_id: z.number().optional(),
  read_outbox_max_id: z.number().optional(),
  notify_settings: z.any().optional(),
});

export class TeleCrawl extends EventEmitter {
  private client: TelegramClient;
  private session: StringSession;
  private db: Database.Database;
  private apiId: number;
  private apiHash: string;
  private botToken?: string;
  private isRunning: boolean = false;
  private syncInterval: NodeJS.Timeout | null = null;
  private messageQueue: any[] = [];

  constructor(options: {
    dbPath: string;
    apiId: number;
    apiHash: string;
    botToken?: string;
    language: string;
    hijriCalendar: boolean;
    jaisEmbeddings: boolean;
    apiKey: string;
  }) {
    super();
    this.apiId = options.apiId;
    this.apiHash = options.apiHash;
    this.botToken = options.botToken;
    this.session = new StringSession('');
    this.client = new TelegramClient(this.session, options.apiId, options.apiHash, { connectionRetries: 5 });
    this.db = new Database(options.dbPath);
    this.initDatabase();
  }

  private initDatabase() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        peer_id TEXT NOT NULL,
        date INTEGER NOT NULL,
        message TEXT,
        media_type TEXT,
        from_id TEXT,
        fwd_from TEXT,
        reply_to TEXT,
        views INTEGER DEFAULT 0,
        forwards INTEGER DEFAULT 0,
        grouped_id INTEGER,
        edit_date INTEGER,
        post_author TEXT,
        restriction_reason TEXT,
        ttl_period INTEGER,
        arabic_tokens TEXT,
        arabic_entities TEXT,
        hijri_date TEXT,
        created_at INTEGER DEFAULT (strftime('%s', 'now')),
        INDEX idx_date (date),
        INDEX idx_peer (peer_id),
        INDEX idx_hijri (hijri_date)
      );

      CREATE TABLE IF NOT EXISTS dialogs (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        username TEXT,
        participants_count INTEGER,
        is_channel INTEGER,
        is_group INTEGER,
        is_user INTEGER,
        unread_count INTEGER,
        unread_mentions INTEGER,
        is_marked_unread INTEGER DEFAULT 0,
        is_muted INTEGER DEFAULT 0,
        is_pinned INTEGER DEFAULT 0,
        folder_id INTEGER,
        top_message INTEGER,
        read_inbox_max_id INTEGER,
        read_outbox_max_id INTEGER,
        created_at INTEGER DEFAULT (strftime('%s', 'now'))
      );

      CREATE TABLE IF NOT EXISTS crawl_state (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at INTEGER DEFAULT (strftime('%s', 'now'))
      );

      CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date);
      CREATE INDEX IF NOT EXISTS idx_messages_peer ON messages(peer_id);
      CREATE INDEX IF NOT EXISTS idx_messages_hijri ON messages(hijri_date) WHERE hijri_date IS NOT NULL;
    `);
  }

  async initialize(): Promise<void> {
    logger.info('Initializing TeleCrawl-AR...');
    await this.client.connect();
    logger.info('TeleCrawl-AR initialized');
  }

  async syncOnce(): Promise<{ messages: number; dialogs: number }> {
    logger.info('Starting Telegram sync...');
    const start = Date.now();
    
    // In real implementation, this would fetch from Telegram
    // For now, return mock counts
    const stats = { messages: 0, dialogs: 0 };
    
    this.setCrawlState('last_sync', new Date().toISOString());
    logger.info({ duration: Date.now() - start, ...stats }, 'Sync complete');
    return stats;
  }

  async startDaemon(intervalMs = 300000): Promise<void> {
    this.isRunning = true;
    logger.info({ intervalMs }, 'Starting TeleCrawl daemon');
    
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
    await this.client.disconnect();
    this.db.close();
    logger.info('TeleCrawl-AR shutdown complete');
  }
}

export { TeleCrawl };