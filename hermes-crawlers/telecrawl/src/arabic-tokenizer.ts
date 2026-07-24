import { tokenize } from 'arabic-tokenizer';
import { normalize } from 'arabic-persian-reshaper';

export class ArabicTokenizer {
  private reshaper: any;

  constructor() {
    try {
      this.reshaper = require('arabic-persian-reshaper');
    } catch {
      this.reshaper = null;
    }
  }

  tokenize(text: string): string[] {
    if (!text || typeof text !== 'string') return [];
    
    try {
      const normalized = this.reshaper ? this.reshaper.normalize(text) : text;
      return tokenize(normalized) || [];
    } catch {
      return text.split(/\s+/).filter(t => t.length > 0);
    }
  }

  extractEntities(text: string): { type: string; value: string }[] {
    const entities: { type: string; value: string }[] = [];
    
    if (!text) return entities;

    // Hijri dates: 15 رمضان 1445 / 15 رمضان 1445 هـ
    const hijriRegex = /\b(\d{1,2})\s*(محرم|صفر|ربيع الأول|ربيع الثاني|جمادى الأولى|جمادى الآخرة|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*(\d{4})?\s*هـ?\b/gi;
    let match;
    while ((match = hijriRegex.exec(text)) !== null) {
      entities.push({ type: 'hijri_date', value: match[0] });
    }

    // Gregorian dates with Arabic numerals
    const gregorianRegex = /(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})/g;
    let match;
    while ((match = /(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})/g.exec(text)) !== null) {
      entities.push({ type: 'gregorian_date', value: match[0] });
    }

    // Currency with Arabic indicators
    const currencyRegex = /(\d+(?:,\d{3})*(?:\.\d+)?)\s*(ريال|دولار|درهم|جنيه|دينار|يورو|دولارات|ريالات|دنانير|جنيهات|دراهم)/gi;
    let match;
    while ((match = /(\d+(?:,\d{3})*(?:\.\d+)?)\s*(ريال|دولار|درهم|جنيه|دينار|يورو|دولارات|ريالات|دنانير|جنيهات|دراهم)/gi.exec(text)) !== null) {
      entities.push({ type: 'currency', value: match[0] });
    }

    // Phone numbers with country codes
    const phoneRegex = /(?:\+?(\d{1,3})[-.\s]?)?(\(?\d{1,3}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}/g;
    let match;
    while ((match = phoneRegex.exec(text)) !== null) {
      entities.push({ type: 'phone', value: match[0] });
    }

    // Email addresses
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
    while ((match = emailRegex.exec(text)) !== null) {
      entities.push({ type: 'email', value: match[0] });
    }

    // URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    while ((match = urlRegex.exec(text)) !== null) {
      entities.push({ type: 'url', value: match[0] });
    }

    // Hashtags (Arabic and English)
    const hashtagRegex = /#[\u0600-\u06FF\w]+/g;
    while ((match = hashtagRegex.exec(text)) !== null) {
      entities.push({ type: 'hashtag', value: match[0] });
    }

    // Mentions
    const mentionRegex = /@[\w\u0600-\u06FF]+/g;
    while ((match = mentionRegex.exec(text)) !== null) {
      entities.push({ type: 'mention', value: match[0] });
    }

    return entities;
  }

  extractHijriDate(text: string): string | null {
    const hijriRegex = /\b(\d{1,2})\s*(محرم|صفر|ربيع الأول|ربيع الثاني|جمادى الأولى|جمادى الآخرة|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*(\d{4})?\s*هـ?\b/i;
    const match = text.match(hijriRegex);
    return match ? match[0] : null;
  }

  tokenizeAndExtract(text: string): { tokens: string[]; entities: { type: string; value: string }[]; hijriDate: string | null } {
    return {
      tokens: this.tokenize(text),
      entities: this.extractEntities(text),
      hijriDate: this.extractHijriDate(text)
    };
  }

  // Convert Arabic-Indic numerals to Western
  toWesternNumerals(text: string): string {
    const arabicNumerals = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    const persianNumerals = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    let result = text;
    for (let i = 0; i < 10; i++) {
      result = result.replace(new RegExp(arabicNumerals[i], 'g'), i.toString());
      result = result.replace(new RegExp(persianNumerals[i], 'g'), i.toString());
    }
    return result;
  }

  // Convert Western numerals to Arabic-Indic
  toArabicNumerals(text: string): string {
    const arabicNumerals = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    let result = text;
    for (let i = 0; i < 10; i++) {
      result = result.replace(new RegExp(i.toString(), 'g'), arabicNumerals[i]);
    }
    return result;
  }
}

export { ArabicTokenizer };