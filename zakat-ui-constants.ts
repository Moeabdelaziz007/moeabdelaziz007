'use client';

'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Decimal } from 'decimal.js';

// Types
interface AssetInput {
  cash?: { amount: number; currency: string };
  gold?: { grams: number; purity: number };
  silver?: { grams: number; purity: number };
  crypto?: Array<{ symbol: string; amount: number; price: number; currency: string }>;
  stocks?: Array<{ symbol: string; shares: number; price: number; currency: string }>;
  business_inventory?: { value: number; currency: string };
  receivables?: { amount: number; currency: string };
}

interface LiabilityInput {
  debts?: number;
  immediate_expenses?: number;
}

interface ZakatSettings {
  madhhab: 'hanafi' | 'shafii' | 'maliki' | 'hanbali';
  nisab_basis: 'gold' | 'silver';
  gold_price_per_gram: number;
  silver_price_per_gram: number;
  hijri_year: number;
  scholar_review_required?: boolean;
}

interface ZakatResult {
  zakat_due: number;
  currency: string;
  breakdown: {
    cash: number;
    gold: number;
    silver: number;
    crypto: number;
    stocks: number;
    business_inventory: number;
    receivables: number;
  };
  nisab_threshold: number;
  total_assets: number;
  total_liabilities: number;
  net_zakatable: number;
  hijri_due_date: string;
  gregorian_due_date: string;
  hijri_year: number;
  calculation_timestamp: string;
  madhhab: string;
  nisab_used: string;
  gold_price_per_gram: number;
  silver_price_per_gram: number;
  scholar_review_required: boolean;
}

interface NisabThresholds {
  gold_grams: number;
  silver_grams: number;
}

const NISAB_THRESHOLDS = {
  hanafi: { gold_grams: 85, silver_grams: 595 },
  shafii: { gold_grams: 85, silver_grams: 595 },
  maliki: { gold_grams: 85, silver_grams: 595 },
  hanbali: { gold_grams: 85, silver_grams: 595 },
};

const MADHAB_NISAB_BASIS: Record<string, 'gold' | 'silver'> = {
  hanafi: 'gold',
  shafii: 'silver',
  maliki: 'silver',
  hanbali: 'silver',
};

const ZAKAT_RATE = 0.025;
const CURRENCY_SYMBOLS: Record<string, string> = {
  SAR: 'ر.س',
  AED: 'د.إ',
  EGP: 'ج.م',
  USD: '$',
  EUR: '€',
  QAR: 'ر.ق',
  KWD: 'د.ك',
  BHD: 'د.ب',
  OMR: 'ر.ع.',
  JOD: 'د.أ',
};

const CURRENCY_SYMBOLS_AR: Record<string, string> = {
  SAR: 'ر.س',
  AED: 'د.إ',
  EGP: 'ج.م',
  USD: '$',
  EUR: '€',
  QAR: 'ر.ق',
  KWD: 'د.ك',
  BHD: 'د.ب',
  OMR: 'ر.ع.',
  JOD: 'د.أ',
};

const CURRENCY_NAMES_AR: Record<string, string> = {
  SAR: 'ريال سعودي',
  AED: 'درهم إماراتي',
  EGP: 'جنيه مصري',
  USD: 'دولار أمريكي',
  EUR: 'يورو',
  QAR: 'ريال قطري',
  KWD: 'دينار كويتي',
  BHD: 'دينار بحريني',
  OMR: 'ريال عماني',
  JOD: 'دينار أردني',
};

const MADHHABS = [
  { value: 'hanafi', label: 'الحنفي', labelEn: 'Hanafi' },
  { value: 'shafii', label: 'الشافعي', labelEn: 'Shafii' },
  { value: 'maliki', label: 'المالكي', labelEn: 'Maliki' },
  { value: 'hanbali', label: 'الحنبلي', labelEn: 'Hanbali' },
];

const NISSAB_BASIS_OPTIONS = [
  { value: 'gold', label: 'الذهب (85 جرام)', labelEn: 'Gold (85g)' },
  { value: 'silver', label: 'الفضة (595 جرام)', labelEn: 'Silver (595g)' },
];

const CURRENCIES = [
  { code: 'SAR', symbol: 'ر.س', name: 'SAR' },
  { code: 'AED', symbol: 'د.إ', name: 'AED' },
  { code: 'EGP', symbol: 'ج.م', name: 'EGP' },
  { code: 'USD', symbol: '$', name: 'USD' },
  { code: 'EUR', symbol: '€', name: 'EUR' },
  { code: 'QAR', symbol: 'ر.ق', name: 'QAR' },
  { code: 'KWD', symbol: 'د.ك', name: 'KWD' },
  { code: 'BHD', symbol: 'د.ب', name: 'BHD' },
  { code: 'OMR', symbol: 'ر.ع', name: 'OMR' },
  { code: 'JOD', symbol: 'د.أ', name: 'JOD' },
];

const ASSET_TYPES = [
  { key: 'cash', label: 'النقد والبنوك', icon: '💵' },
  { key: 'gold', label: 'الذهب', icon: '🥇' },
  { key: 'silver', label: 'الفضة', icon: '🥈' },
  { key: 'crypto', label: 'العملات الرقمية', icon: '₿' },
  { key: 'stocks', label: 'الأسهم', icon: '📈' },
  { key: 'business_inventory', label: 'بضاعة تجارية', icon: '📦' },
  { key: 'receivables', label: 'ديون مستحقة لك', icon: '📋' },
];

const LIABILITY_TYPES = [
  { key: 'debts', label: 'الديون المستحقة', icon: '💳' },
  { key: 'immediate_expenses', label: 'مصاريف فورية', icon: '💸' },
];

const MADHHABS = [
  { value: 'hanafi', label: 'الحنفي', description: 'النصاب بالذهب (85 جم)' },
  { value: 'shafii', label: 'الشافعي', description: 'النصاب بالفضة (595 جم)' },
  { value: 'maliki', label: 'المالكي', description: 'النصاب بالفضة (595 جم)' },
  { value: 'hanbali', label: 'الحنبلي', description: 'النصاب بالفضة (595 جم)' },
];

const NISSAB_OPTIONS = [
  { value: 'gold', label: 'الذهب (85 جرام)', description: 'نصاب الذهب: 85 جرام ذهب خالص' },
  { value: 'silver', label: 'الفضة (595 جرام)', description: 'نصاب الفضة: 595 جرام فضة' },
];

// Validation schemas
const assetSchema = z.object({
  cash: z.object({
    amount: z.number().min(0).default(0),
    currency: z.string().default('SAR'),
  }).optional(),
  gold: z.object({
    grams: z.number().min(0).default(0),
    purity: z.number().min(0).max(24).default(24),
  }).optional(),
  silver: z.object({
    grams: z.number().min(0).default(0),
    purity: z.number().min(0).max(100).default(99.9),
  }).optional(),
  crypto: z.array(z.object({
    symbol: z.string(),
    amount: z.number().min(0),
    price: z.number().min(0),
    currency: z.string(),
  })).optional(),
  stocks: z.array(z.object({
    symbol: z.string(),
    shares: z.number().min(0),
    price: z.number().min(0),
    currency: z.string(),
  })).optional(),
  business_inventory: z.object({
    value: z.number().min(0),
    currency: z.string(),
  }).optional(),
  receivables: z.object({
    amount: z.number().min(0),
    currency: z.string(),
  }).optional(),
});

const liabilitySchema = z.object({
  debts: z.number().min(0).default(0),
  immediate_expenses: z.number().min(0).default(0),
});

const settingsSchema = z.object({
  madhhab: z.enum(['hanafi', 'shafii', 'maliki', 'hanbali']).default('hanafi'),
  nisab_basis: z.enum(['gold', 'silver']).default('gold'),
  gold_price_per_gram: z.number().positive().default(280),
  silver_price_per_gram: z.number().positive().default(3.5),
  hijri_year: z.number().int().min(1400).max(1500).default(1446),
  scholar_review_required: z.boolean().default(false),
});

const assetSchema = z.object({
  cash: z.object({
    amount: z.number().min(0).default(0),
    currency: z.string().default('SAR'),
  }).optional(),
  gold: z.object({
    grams: z.number().min(0).default(0),
    purity: z.number().min(0).max(24).default(24),
  }).optional(),
  silver: z.object({
    grams: z.number().min(0).default(0),
    purity: z.number().min(0).max(100).default(99.9),
  }).optional(),
  crypto: z.array(z.object({
    symbol: z.string(),
    amount: z.number().min(0),
    price: z.number().min(0),
    currency: z.string(),
  })).optional(),
  stocks: z.array(z.object({
    symbol: z.string(),
    shares: z.number().min(0),
    price: z.number().min(0),
    currency: z.string(),
  })).optional(),
  business_inventory: z.object({
    value: z.number().min(0),
    currency: z.string(),
  }).optional(),
  receivables: z.object({
    amount: z.number().min(0),
    currency: z.string(),
  }).optional(),
});

const liabilitySchema = z.object({
  debts: z.number().min(0).default(0),
  immediate_expenses: z.number().min(0).default(0),
});

const settingsSchema = z.object({
  madhhab: z.enum(['hanafi', 'shafii', 'maliki', 'hanbali']).default('hanafi'),
  nisab_basis: z.enum(['gold', 'silver']).default('gold'),
  gold_price_per_gram: z.number().positive().default(280),
  silver_price_per_gram: z.number().positive().default(3.5),
  hijri_year: z.number().int().min(1400).max(1500).default(1446),
  scholar_review_required: z.boolean().default(false),
});

export {
  ASSET_TYPES,
  LIABILITY_TYPES,
  MADHHABS,
  NISSAB_BASIS_OPTIONS,
  CURRENCIES,
  CURRENCY_SYMBOLS,
  CURRENCY_SYMBOLS_AR,
  CURRENCY_NAMES_AR,
  MADHHABS,
  NISSAB_BASIS_OPTIONS,
  CURRENCY_SYMBOLS,
  CURRENCY_SYMBOLS_AR,
  CURRENCY_NAMES_AR,
  MADHHABS,
  NISSAB_OPTIONS,
  CURRENCIES,
  MADHHABS,
  NISSAB_OPTIONS,
  CURRENCIES,
  MADHHABS,
  NISSAB_BASIS_OPTIONS,
  CURRENCIES,
  assetSchema,
  liabilitySchema,
  settingsSchema,
  MADHHABS,
  NISSAB_BASIS_OPTIONS,
  CURRENCIES,
  ASSET_TYPES,
  LIABILITY_TYPES,
  MADHHABS,
  NISSAB_BASIS_OPTIONS,
  CURRENCIES,
  CURRENCY_SYMBOLS,
  CURRENCY_SYMBOLS_AR,
  CURRENCY_NAMES_AR,
  MADHHABS,
  NISSAB_BASIS_OPTIONS,
  CURRENCIES,
  CURRENCY_SYMBOLS,
  CURRENCY_SYMBOLS_AR,
  CURRENCY_NAMES_AR,
  MADHHABS,
  NISSAB_BASIS_OPTIONS,
  CURRENCIES,
};