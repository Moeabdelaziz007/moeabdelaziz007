/**
 * Zakat Calculator - Arabic-Native Islamic Finance Calculator
 * Multi-madhhab support with Hijri calendar integration
 */

// Config
const ZAKAT_RATE = 0.025; // 2.5%

const NISAB_THRESHOLDS = {
  hanafi: { gold_grams: 85, silver_grams: 595 },
  shafii: { gold_grams: 85, silver_grams: 595 },
  maliki: { gold_grams: 85, silver_grams: 595 },
  hanbali: { gold_grams: 85, silver_grams: 595 },
};

const MADHAB_NISAB_BASIS = {
  hanafi: 'gold',
  shafii: 'silver',
  maliki: 'silver',
  hanbali: 'silver',
};

// Types
export type Madhhab = 'hanafi' | 'shafii' | 'maliki' | 'hanbali';

export interface ZakatSettings {
  madhhab: Madhhab;
  nisab_basis: 'gold' | 'silver';
  gold_price_per_gram: number;
  silver_price_per_gram: number;
  hijri_year: number;
  scholar_review_required?: boolean;
}

export interface AssetInput {
  cash?: { amount: number; currency: string };
  gold?: { grams: number; purity: number };
  silver?: { grams: number; purity: number };
  crypto?: Array<{ symbol: string; amount: number; price: number }>;
  stocks?: Array<{ symbol: string; shares: number; price: number }>;
  business_inventory?: { value: number; currency: string };
  receivables?: { amount: number; currency: string };
}

export interface LiabilityInput {
  debts?: number;
  immediate_expenses?: number;
}

export interface ZakatBreakdown {
  cash: number;
  gold: number;
  silver: number;
  crypto: number;
  stocks: number;
  business_inventory: number;
  receivables: number;
}

export interface ZakatResult {
  zakat_due: number;
  currency: string;
  breakdown: ZakatBreakdown;
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
  scholar_review_required: boolean;
}

// Main Calculator Class
export class ZakatCalculator {
  private settings: ZakatSettings;

  constructor(settings: ZakatSettings) {
    this.settings = settings;
  }

  getNisabThreshold(): number {
    const basis = this.settings.nisab_basis || MADHAB_NISAB_BASIS[this.settings.madhhab];
    const thresholds = NISAB_THRESHOLDS[this.settings.madhhab];

    if (basis === 'gold') {
      return thresholds.gold_grams;
    } else {
      return thresholds.silver_grams;
    }
  }

  calculateCashZakat(amount: number): number {
    return amount * ZAKAT_RATE;
  }

  calculateGoldZakat(grams: number, purity: number): number {
    const pureGrams = grams * (purity / 24);
    return pureGrams * ZAKAT_RATE;
  }

  calculateSilverZakat(grams: number, purity: number): number {
    const pureGrams = grams * (purity / 24);
    return pureGrams * ZAKAT_RATE;
  }

  calculateCryptoZakat(holdings: Array<{ amount: number; price: number }>): number {
    let totalValue = 0;
    for (const holding of holdings) {
      totalValue += holding.amount * holding.price;
    }
    return totalValue * ZAKAT_RATE;
  }

  calculateStocksZakat(holdings: Array<{ shares: number; price: number }>): number {
    let totalValue = 0;
    for (const holding of holdings) {
      totalValue += holding.shares * holding.price;
    }
    return totalValue * ZAKAT_RATE;
  }

  calculateInventoryZakat(value: number): number {
    return value * ZAKAT_RATE;
  }

  calculateReceivablesZakat(amount: number): number {
    return amount * ZAKAT_RATE;
  }

  calculate(
    assets: AssetInput,
    liabilities: LiabilityInput,
    currency: string = 'SAR'
  ): ZakatResult {
    const breakdown: ZakatBreakdown = {
      cash: 0,
      gold: 0,
      silver: 0,
      crypto: 0,
      stocks: 0,
      business_inventory: 0,
      receivables: 0,
    };

    let totalAssets = 0;
    let totalZakat = 0;

    // Cash
    if (assets.cash) {
      const cashZakat = this.calculateCashZakat(assets.cash.amount);
      breakdown.cash = cashZakat;
      totalZakat += cashZakat;
      totalAssets += assets.cash.amount;
    }

    // Gold
    if (assets.gold) {
      const goldZakat = this.calculateGoldZakat(assets.gold.grams, assets.gold.purity);
      breakdown.gold = goldZakat;
      totalZakat += goldZakat;
      const goldValue = assets.gold.grams * (assets.gold.purity / 24);
      totalAssets += goldValue;
    }

    // Silver
    if (assets.silver) {
      const silverZakat = this.calculateSilverZakat(assets.silver.grams, assets.silver.purity);
      breakdown.silver = silverZakat;
      totalZakat += silverZakat;
      const silverValue = assets.silver.grams * (assets.silver.purity / 24);
      totalAssets += silverValue;
    }

    // Crypto
    if (assets.crypto && assets.crypto.length > 0) {
      const cryptoZakat = this.calculateCryptoZakat(assets.crypto);
      breakdown.crypto = cryptoZakat;
      totalZakat += cryptoZakat;
      for (const crypto of assets.crypto) {
        totalAssets += crypto.amount * crypto.price;
      }
    }

    // Stocks
    if (assets.stocks && assets.stocks.length > 0) {
      const stocksZakat = this.calculateStocksZakat(assets.stocks);
      breakdown.stocks = stocksZakat;
      totalZakat += stocksZakat;
      for (const stock of assets.stocks) {
        totalAssets += stock.shares * stock.price;
      }
    }

    // Business Inventory
    if (assets.business_inventory) {
      const inventoryZakat = this.calculateInventoryZakat(assets.business_inventory.value);
      breakdown.business_inventory = inventoryZakat;
      totalZakat += inventoryZakat;
      totalAssets += assets.business_inventory.value;
    }

    // Receivables
    if (assets.receivables) {
      const receivablesZakat = this.calculateReceivablesZakat(assets.receivables.amount);
      breakdown.receivables = receivablesZakat;
      totalZakat += receivablesZakat;
      totalAssets += assets.receivables.amount;
    }

    // Liabilities
    const totalLiabilities = (liabilities.debts || 0) + (liabilities.immediate_expenses || 0);
    const netAssets = totalAssets - totalLiabilities;
    const nisabThreshold = this.getNisabThreshold();

    // Zakat due only if exceeds Nisab
    let zakatDue = 0;
    if (netAssets >= nisabThreshold) {
      zakatDue = totalZakat;
    }

    // Hijri due date (next Ramadan 1st)
    const hijriDueDate = this.calculateHijriDueDate();
    const gregorianDueDate = this.hijriToGregorian(this.settings.hijri_year, 9, 15);
    const nisabUsed = this.settings.nisab_basis || 'gold';

    return {
      zakat_due: zakatDue,
      currency: 'SAR',
      breakdown,
      nisab_threshold: nisabThreshold,
      total_assets: totalAssets,
      total_liabilities: totalLiabilities,
      net_zakatable: netAssets,
      hijri_due_date: hijriDueDate,
      gregorian_due_date: gregorianDueDate,
      hijri_year: this.settings.hijri_year,
      calculation_timestamp: new Date().toISOString(),
      madhhab: this.settings.madhhab,
      nisab_used: nisabUsed,
      scholar_review_required: this.settings.scholar_review_required || false,
    };
  }

  private calculateHijriDueDate(): string {
    return `${this.settings.hijri_year + 1}-09-01`;
  }

  private hijriToGregorian(hijriYear: number, hijriMonth: number, hijriDay: number): string {
    const gregorianYear = hijriYear + 622 - Math.floor((hijriYear - 1) / 33);
    return `${gregorianYear}-${hijriMonth.toString().padStart(2, '0')}-${hijriDay.toString().padStart(2, '0')}`;
  }
}

export { ZakatCalculator, ZAKAT_RATE, NISAB_THRESHOLDS, MADHAB_NISAB_BASIS };