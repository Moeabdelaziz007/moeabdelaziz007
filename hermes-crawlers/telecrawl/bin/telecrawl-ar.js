#!/usr/bin/env node
import { TeleCrawl } from '../src/index.js';

const crawler = new TeleCrawl({
  dbPath: process.env.DB_PATH || './data/telecrawl.db',
  apiId: process.env.TELEGRAM_API_ID,
  apiHash: process.env.TELEGRAM_API_HASH,
  botToken: process.env.TELEGRAM_BOT_TOKEN,
  language: 'ar',
  hijriCalendar: true,
  jaisEmbeddings: true,
  apiKey: process.env.JAIS_API_KEY,
});

await crawler.initialize();

console.log('🦞 TeleCrawl-AR initialized');
console.log('📱 Telegram API:', process.env.TELEGRAM_API_ID ? 'SET' : 'NOT SET');
console.log('🇸🇦 Arabic mode: ON');
console.log('🗓️  Hijri calendar: ON');
console.log('🤖 Jais embeddings:', process.env.JAIS_API_KEY ? 'ON' : 'OFF (using fallback)');

if (process.argv.includes('--daemon')) {
  await crawler.startDaemon();
} else if (process.argv.includes('--sync')) {
  await crawler.syncOnce();
} else {
  console.log('Usage: telecrawl-ar [--daemon|--sync]');
  process.exit(1);
}