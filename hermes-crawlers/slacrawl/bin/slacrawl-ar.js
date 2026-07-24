#!/usr/bin/env node
import { SlacCrawl } from '../src/index.js';

const crawler = new SlacCrawl({
  dbPath: process.env.DB_PATH || './data/slacrawl.db',
  botToken: process.env.SLACK_BOT_TOKEN,
  appToken: process.env.SLACK_APP_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  language: 'ar',
  hijriCalendar: true,
  jaisEmbeddings: true,
  apiKey: process.env.JAIS_API_KEY,
});

await crawler.initialize();

console.log('🦞 SlacCrawl-AR initialized');
console.log('💬 Slack Bot Token:', process.env.SLACK_BOT_TOKEN ? 'SET' : 'NOT SET');
console.log('🇸🇦 Arabic mode: ON');
console.log('🗓️  Hijri calendar: ON');
console.log('🤖 Jais embeddings:', process.env.JAIS_API_KEY ? 'ON' : 'OFF (using fallback)');

if (process.argv.includes('--daemon')) {
  await crawler.startDaemon();
} else if (process.argv.includes('--sync')) {
  await crawler.syncOnce();
} else {
  console.log('Usage: slacrawl-ar [--daemon|--sync]');
  process.exit(1);
}