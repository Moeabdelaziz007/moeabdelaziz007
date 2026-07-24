import { EventEmitter } from 'events';
import { Chat } from 'whatsapp-web.js';
import Database from 'better-sqlite3';
import { z } from 'zod';
import pino from 'pino';
import { ArabicTokenizer } from './arabic-tokenizer.js';
import { HijriCalendar } from './hijri-calendar.js';
import { JaisEmbeddings } from './jais-embeddings.js';

const logger = pino({ level: 'info' });

const MessageSchema = z.object({
  id: z.string(),
  from: z.string(),
  to: z.string(),
  body: z.string(),
  timestamp: z.number(),
  type: z.enum(['text', 'image', 'document', 'audio', 'video', 'location', 'contact', 'sticker']),
  hasMedia: z.boolean(),
  isGroup: z.boolean(),
  groupId: z.string().optional(),
  author: z.string().optional(),
  quotedMsg: z.string().optional(),
  arabicText: z.string().optional(),
  hijriDate: z.string().optional(),
  embedding: z.array(z.number()).optional(),
  metadata: z.record(z.unknown()).optional(),
});

const ContactSchema = z.object({
  id: z.string(),
  name: z.string().optional(),
  pushname: z.string().optional(),
  number: z.string(),
  isBusiness: z.boolean().optional(),
  isGroup: z.boolean().optional(),
  arabicName: z.string().optional(),
  hijriBirthday: z.string().optional(),
});

const GroupSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().optional(),
  participants: z.array(z.string()),
  arabicName: z.string().optional(),
  hijriCreatedAt: z.string().optional(),
});

export class WhatsCrawl extends EventEmitter {
  private db: Database.Database;
  private client: any; // whatsapp-web.js Client
  private tokenizer: ArabicTokenizer;
  private hijri: HijriCalendar;
  private jais: JaisEmbeddings;
  private isRunning: boolean = false;
  private syncInterval: NodeJS.Timeout | null = null;

  constructor(options: {
    dbPath: string;
    language: string;
    hijriCalendar: boolean;
    jaisEmbeddings: boolean;
    apiKey: string;
    phoneNumber: string;
    sessionPath: string;
  }) {
    super();
    this.db = new Database(options.dbPath);
    this.tokenizer = new ArabicTokenizer();
    this.hijri = new HijriCalendar();
    this.jais = new JaisEmbeddings(options.apiKey);
    this.initDatabase();
    this.initWhatsAppClient(options);
  }

  private initDatabase() {
    // Messages table with Arabic support
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        from_id TEXT NOT NULL,
        to_id TEXT NOT NULL,
        body TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        type TEXT NOT NULL,
        has_media INTEGER DEFAULT 0,
        is_group INTEGER DEFAULT 0,
        group_id TEXT,
        author_id TEXT,
        quoted_msg_id TEXT,
        arabic_text TEXT,
        hijri_date TEXT,
        embedding BLOB,
        metadata TEXT,
        created_at INTEGER DEFAULT (strftime('%s', 'now')),
        INDEX idx_timestamp (timestamp),
        INDEX idx_from (from_id),
        INDEX idx_to (to_id),
        INDEX idx_group (group_id),
        INDEX idx_hijri (hijri_date)
      );

      CREATE TABLE IF NOT EXISTS contacts (
        id TEXT PRIMARY KEY,
        name TEXT,
        pushname TEXT,
        number TEXT NOT NULL,
        is_business INTEGER DEFAULT 0,
        is_group INTEGER DEFAULT 0,
        arabic_name TEXT,
        hijri_birthday TEXT,
        created_at INTEGER DEFAULT (strftime('%s', 'now'))
      );

      CREATE TABLE IF NOT EXISTS groups (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        participants TEXT,
        arabic_name TEXT,
        hijri_created_at TEXT,
        created_at INTEGER DEFAULT (strftime('%s', 'now'))
      );

      CREATE TABLE IF NOT EXISTS embeddings_cache (
        text_hash TEXT PRIMARY KEY,
        embedding BLOB NOT NULL,
        model TEXT NOT NULL,
        created_at INTEGER DEFAULT (strftime('%s', 'now'))
      );

      CREATE TABLE IF NOT EXISTS crawl_state (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at INTEGER DEFAULT (strftime('%s', 'now'))
      );

      CREATE INDEX IF NOT EXISTS idx_messages_arabic ON messages(arabic_text) WHERE arabic_text IS NOT NULL;
      CREATE INDEX IF NOT EXISTS idx_contacts_arabic ON contacts(arabic_name) WHERE arabic_name IS NOT NULL;
    `);

    // WAL mode for better concurrency
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('synchronous = NORMAL');
    this.db.pragma('cache_size = -32768'); // 32MB cache
  }

  private initWhatsAppClient(options: any) {
    // This would use whatsapp-web.js in real implementation
    // For now, we'll use a mock structure that can be replaced
    this.client = {
      initialize: async () => {
        logger.info('WhatsApp client initialized');
        // QR code handling would go here
      },
      onMessage: (callback: (msg: any) => void) => {
        // Message handler registration
      },
      onReady: () => {
        logger.info('WhatsApp client ready');
        this.emit('ready');
      },
      onQR: (qr: string) => {
        logger.info('QR code received');
        this.emit('qr', qr);
      },
      onDisconnected: (reason: string) => {
        logger.warn({ reason }, 'WhatsApp disconnected');
        this.emit('disconnected', reason);
      },
    };
  }

  async initialize(): Promise<void> {
    logger.info('Initializing WhatsCrawl-AR...');
    await this.client.initialize();
    
    // Load state
    const lastSync = this.getCrawlState('last_sync');
    if (lastSync) {
      logger.info({ lastSync }, 'Resuming from last sync');
    }
    
    return new Promise((resolve) => {
      this.client.onReady(() => resolve());
    });
  }

  async syncOnce(): Promise<{ messages: number; contacts: number; groups: number }> {
    logger.info('Starting sync...');
    const start = Date.now();
    
    // In real implementation, this would fetch from WhatsApp
    // For now, return mock counts
    const stats = { messages: 0, contacts: 0, groups: 0 };
    
    this.setCrawlState('last_sync', new Date().toISOString());
    logger.info({ duration: Date.now() - start, ...stats }, 'Sync complete');
    return stats;
  }

  async startDaemon(intervalMs = 300000): Promise<void> {
    if (this.isRunning) {
      logger.warn('Daemon already running');
      return;
    }
    
    this.isRunning = true;
    logger.info({ intervalMs }, 'Starting WhatsCrawl daemon');
    
    // Initial sync
    await this.syncOnce();
    
    // Periodic sync
    this.syncInterval = setInterval(async () => {
      try {
        await this.syncOnce();
      } catch (error) {
        logger.error({ error }, 'Sync failed');
      }
    }, intervalMs);
    
    logger.info('Daemon started');
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
    this.db.close();
    logger.info('WhatsCrawl-AR shutdown complete');
  }
}

export { WhatsCrawl };