import { EventEmitter } from 'events';
import { ArabicTokenizer } from './arabic-tokenizer';
import { createClient } from 'whatsapp-web.js';

export interface CrawlConfig {
  sessionName: string;
  dbPath: string;
  headless?: boolean;
  languages?: string[];
}

export interface MessageData {
  id: string;
  from: string;
  to: string;
  body: string;
  timestamp: number;
  type: 'text' | 'image' | 'document' | 'audio' | 'video' | 'location' | 'contact';
  metadata?: Record<string, any>;
  arabicTokens?: string[];
  arabicEntities?: { type: string; value: string }[];
  hijriDate?: string;
}

export class WhatsCrawl extends EventEmitter {
  private client: any;
  private tokenizer: ArabicTokenizer;
  private config: CrawlConfig;
  private isRunning: boolean = false;
  private messageQueue: MessageData[] = [];
  private flushInterval: NodeJS.Timeout | null = null;

  constructor(config: CrawlConfig) {
    super();
    this.config = config;
    this.tokenizer = new ArabicTokenizer();
    this.client = createClient({
      authStrategy: 'local',
      sessionName: config.sessionName,
      headless: config.headless ?? true,
      puppeteer: {
        headless: config.headless ?? true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      }
    });

    this.setupClient();
  }

  private setupClient(): void {
    this.client.on('qr', (qr: string) => {
      this.emit('qr', qr);
    });

    this.client.on('ready', () => {
      this.emit('ready', this.client.info);
      this.startPeriodicFlush();
    });

    this.client.on('message', async (msg: any) => {
      await this.processMessage(msg);
    });

    this.client.on('disconnected', (reason: string) => {
      this.emit('disconnected', reason);
      this.handleReconnect();
    });
  }

  async start(): Promise<void> {
    this.isRunning = true;
    await this.client.initialize();
  }

  async stop(): Promise<void> {
    this.isRunning = false;
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
      this.flushInterval = null;
    }
    await this.flushQueue();
    await this.client.destroy();
  }

  private async processMessage(msg: any): Promise<void> {
    try {
      const messageData: MessageData = {
        id: msg.id._serialized,
        from: msg.from,
        to: msg.to,
        body: msg.body || '',
        timestamp: msg.timestamp * 1000,
        type: this.getMessageType(msg),
        metadata: {
          fromMe: msg.fromMe,
          isGroup: msg.from.includes('@g.us'),
          author: msg.author,
          quotedMsg: msg.quotedMsg ? {
            id: msg.quotedMsg.id._serialized,
            body: msg.quotedMsg.body
          } : undefined
        }
      };

      // Arabic processing
      if (messageData.body) {
        messageData.arabicTokens = this.tokenizer.tokenize(messageData.body);
        messageData.arabicEntities = this.extractArabicEntities(messageData.body);
        messageData.hijriDate = this.extractHijriDate(messageData.body);
      }

      // Add to queue
      this.messageQueue.push(messageData);
      this.emit('message', messageData);

      // Flush if queue is large
      if (this.messageQueue.length >= 100) {
        await this.flushQueue();
      }
    } catch (error) {
      this.emit('error', { error, message: msg.id._serialized });
    }
  }

  private getMessageType(msg: any): MessageData['type'] {
    if (msg.type === 'image') return 'image';
    if (msg.type === 'document') return 'document';
    if (msg.type === 'audio') return 'audio';
    if (msg.type === 'video') return 'video';
    if (msg.type === 'location') return 'location';
    if (msg.type === 'vcard') return 'contact';
    return 'text';
  }

  private extractArabicEntities(text: string): { type: string; value: string }[] {
    // Simple entity extraction - in real implementation, use the ArabicTokenizer
    const entities: { type: string; value: string }[] = [];
    
    // Hijri dates
    const hijriRegex = /\b(\d{1,2})\s*(محرم|صفر|ربيع الأول|ربيع الثاني|جمادى الأولى|جمادى الآخرة|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*(\d{4})?\b/g;
    let match;
    while ((match = text.match(/(\d{1,2})\s*(محرم|صفر|ربيع الأول|ربيع الثاني|جمادى الأولى|جمادى الآخرة|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*(\d{4})?/))) {
      entities.push({ type: 'hijri_date', value: match[0] });
      text = text.replace(match[0], '');
    }
    
    return entities;
  }

  private extractHijriDate(text: string): string | undefined {
    const match = text.match(/\b(\d{1,2})\s*(محرم|صفر|ربيع الأول|ربيع الثاني|جمادى الأولى|جمادى الآخرة|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*(\d{4})?\b/);
    return match ? match[0] : undefined;
  }

  private startPeriodicFlush(): void {
    this.flushInterval = setInterval(() => {
      this.flushQueue().catch(err => this.emit('error', err));
    }, 30000); // Flush every 30 seconds
  }

  private async flushQueue(): Promise<void> {
    if (this.messageQueue.length === 0) return;
    
    const messages = this.messageQueue.splice(0, this.messageQueue.length);
    this.emit('batch', messages);
    // In real implementation, persist to database here
  }

  private async handleReconnect(): Promise<void> {
    this.emit('reconnecting');
    setTimeout(() => {
      if (this.isRunning) {
        this.client.initialize().catch(err => {
          this.emit('error', err);
          setTimeout(() => this.handleReconnect(), 30000);
        });
      }
    }, 5000);
  }

  // Public API
  async getChats(): Promise<any[]> {
    return this.client.getChats();
  }

  async getContacts(): Promise<any[]> {
    return this.client.getContacts();
  }

  async sendMessage(to: string, content: string, options?: any): Promise<any> {
    return this.client.sendMessage(to, content, options);
  }

  async getMessages(chatId: string, options?: { limit?: number; before?: string }): Promise<any[]> {
    const chat = await this.client.getChatById(chatId);
    return chat.fetchMessages(options);
  }

  getStats(): { queued: number; running: boolean } {
    return {
      queued: this.messageQueue.length,
      running: this.isRunning
    };
  }
}

export { WhatsCrawl, MessageData, CrawlConfig };