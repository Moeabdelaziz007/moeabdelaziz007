#!/usr/bin/env node
import { WhatsCrawl } from '../src/index.js';

const crawler = new WhatsCrawl({
  dbPath: process.env.DB_PATH || './data/whatscrawl.db',
  language: 'ar',
  hijriCalendar: true,
  jaisEmbeddings: true,
  apiKey: process.env.JAIS_API_KEY,
  phoneNumber: process.env.WHATSAPP_PHONE,
  sessionPath: process.env.SESSION_PATH || './sessions/whatsapp',
});

await crawler.initialize();

console.log('🦞 WhatsCrawl-AR initialized');
console.log('📱 Phone:', process.env.WHATSAPP_PHONE || 'not set');
console.log('🇸🇦 Arabic mode: ON');
console.log('🗓️  Hijri calendar: ON');
console.log('🤖 Jais embeddings:', process.env.JAIS_API_KEY ? 'ON' : 'OFF (using fallback)');

if (process.argv.includes('--daemon')) {
  await crawler.startDaemon();
} else if (process.argv.includes('--sync')) {
  await crawler.syncOnce();
} else {
  console.log('Usage: whatscrawl-ar [--daemon|--sync]');
  process.exit(1);
}