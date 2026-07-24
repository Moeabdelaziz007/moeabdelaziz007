import { EventEmitter } from 'events';

export class ArabicTokenizer {
  constructor() {
    // Initialize tokenizer
  }

  tokenize(text: string): string[] {
    if (!text || typeof text !== 'string') return [];
    
    const normalized = this.normalize(text);
    
    return normalized
      .split(/[\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+/)
      .filter(token => token.length > 0);
  }

  normalize(text: string): string {
    return text
      .replace(/[\u064B-\u065F\u0670]/g, '') // Remove diacritics
      .replace(/[إأآا]/g, 'ا') // Normalize alef
      .replace(/[ة]/g, 'ه') // Normalize ta marbuta
      .replace(/[ى]/g, 'ي') // Normalize alef maksura
      .replace(/[ؤئ]/g, 'ء') // Normalize hamza
      .trim();
  }

  extractKeywords(text: string, maxKeywords = 10): string[] {
    const tokens = this.tokenize(text);
    const stopWords = new Set([
      'في', 'من', 'على', 'إلى', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك',
      'و', 'أو', 'لكن', 'إذا', 'أن', 'إن', 'كان', 'كانت', 'يكون', 'تكون',
      'ال', 'إلى', 'من', 'في', 'على', 'عن', 'مع', 'هو', 'هي', 'هم', 'هن',
      'أنا', 'أنت', 'أنتم', 'نحن', 'هذا', 'ذلك', 'التي', 'الذي', 'الذين'
    ]);
    
    return tokens
      .filter(t => t.length > 2 && !stopWords.has(t))
      .slice(0, maxKeywords);
  }

  extractArabicEntities(text: string): { type: string; value: string }[] {
    const entities: { type: string; value: string }[] = [];
    
    // Hijri dates
    const hijriRegex = /\b(\d{1,2})\s*(محرم|صفر|ربيع الأول|ربيع الثاني|جمادى الأولى|جمادى الآخرة|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*(\d{4})?\b/g;
    let match;
    while ((match = hijriRegex.exec(text)) !== null) {
      entities.push({ type: 'hijri_date', value: match[0] });
    }
    
    // Gregorian dates
    const gregorianRegex = /\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})\b/g;
    while ((match = gregorianRegex.exec(text)) !== null) {
      entities.push({ type: 'gregorian_date', value: match[0] });
    }
    
    // Phone numbers (MENA format)
    const phoneRegex = /(?:\+?966|0)?5\d{8}\b/g;
    while ((match = phoneRegex.exec(text)) !== null) {
      entities.push({ type: 'phone_sa', value: match[0] });
    }
    
    // Email
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
    while ((match = emailRegex.exec(text)) !== null) {
      entities.push({ type: 'email', value: match[0] });
    }
    
    // Currency (SAR, AED, EGP, etc.)
    const currencyRegex = /\b(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(ر\.س|ريال|درهم|جنيه|دولار|SAR|AED|EGP|USD)\b/gi;
    while ((match = currencyRegex.exec(text)) !== null) {
      entities.push({ type: 'currency', value: match[0] });
    }
    
    return entities;
  }
}

export { ArabicTokenizer };