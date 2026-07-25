import { DurableObject } from 'cloudflare:workers';
import { MemoryEntry, MemoryQuery, MemoryResult, LayerConfig } from '../types';

interface Env {
  DB: D1Database;
  SESSIONS: KVNamespace;
  ARTIFACTS: R2Bucket;
  MEMORY: VectorizeIndex;
  AI: Ai;
}

export class MemoryRouter extends DurableObject {
  private state: DurableObjectState;
  private env: Env;
  private layers: Map<string, MemoryEntry[]> = new Map();

  constructor(state: DurableObjectState, env: Env) {
    super(state, env);
    this.state = state;
    this.env = env;
  }

  async initialize(): Promise<void> {
    const stored = await this.state.storage.get<Map<string, MemoryEntry[]>>('layers');
    if (stored) {
      this.layers = stored;
    } else {
      // Initialize empty layers
      const layerNames = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'];
      for (const layer of layerNames) {
        this.layers.set(layer, []);
      }
    }
  }

  async remember(entry: Omit<MemoryEntry, 'id' | 'createdAt' | 'accessedAt' | 'accessCount'>): Promise<string> {
    const id = crypto.randomUUID();
    const now = Date.now();
    
    const entry: MemoryEntry = {
      ...entry,
      id,
      createdAt: Date.now(),
      accessedAt: now,
      accessCount: 0
    };

    const layerEntries = this.layers.get(entry.layer) || [];
    layerEntries.push(entry);
    this.layers.set(entry.layer, layerEntries);

    // Generate embedding if needed
    if (entry.layer === 'L3' || entry.layer === 'L2') {
      entry.embedding = await this.generateEmbedding(entry.content);
    }

    await this.persist();
    return id;
  }

  async recall(query: MemoryQuery): Promise<MemoryResult[]> {
    const layers = query.layers || ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'];
    let results: any[] = [];

    for (const layer of layers) {
      const entries = this.layers.get(layer) || [];
      let layerResults: any[] = [];

      if ((layer === 'L2' || layer === 'L3') && entries.length > 0) {
        // Vector search for L2, L3
        const queryEmbedding = await this.generateEmbedding(query.query);
        layerResults = entries
          .filter(e => e.embedding)
          .map(e => ({
            ...e,
            similarity: this.cosineSimilarity(queryEmbedding, e.embedding!)
          }))
          .sort((a, b) => (b.similarity || 0) - (a.similarity || 0));
      } else {
        // Text search for other layers
        layerResults = entries
          .filter(e => e.content.toLowerCase().includes(query.query.toLowerCase()))
          .sort((a, b) => b.accessedAt - a.accessedAt);
      }

      if (query.minConfidence) {
        layerResults = layerResults.filter(e => e.metadata.confidence >= (query.minConfidence || 0));
      }

      if (query.tags?.length) {
        layerResults = layerResults.filter(e => 
          query.tags!.some(t => e.metadata.tags.includes(t))
        );
      }

      results.push(...layerResults.slice(0, query.limit || 10));
    }

    // Update access stats
    for (const result of results) {
      result.accessedAt = Date.now();
      result.accessCount++;
    }

    await this.persist();
    return results.slice(0, query.limit || 10);
  }

  async promote(entryId: string, fromLayer: string, toLayer: string): Promise<void> {
    const fromEntries = this.layers.get(fromLayer) || [];
    const entryIndex = fromEntries.findIndex(e => e.id === entryId);
    
    if (entryIndex === -1) throw new Error('Entry not found');

    const [entry] = fromEntries.splice(entryIndex, 1);
    entry.layer = toLayer as any;
    
    const toEntries = this.layers.get(toLayer) || [];
    toEntries.push(entry);
    
    await this.persist();
  }

  async archive(entryId: string): Promise<void> {
    // Move to L7 (cold archive)
    for (const [layer, entries] of this.layers) {
      const index = entries.findIndex(e => e.id === entryId);
      if (index !== -1) {
        const [entry] = entries.splice(index, 1);
        entry.layer = 'L7';
        const l7 = this.layers.get('L7') || [];
        l7.push(entry);
        await this.persist();
        return;
      }
    }
  }

  private async persist(): Promise<void> {
    await this.state.storage.put('layers', this.layers);
  }

  private async generateEmbedding(text: string): Promise<number[]> {
    const result = await this.env.AI.run('@cf/baai/bge-base-en-v1.5', {
      text: [text]
    });
    return result.data[0];
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    let dot = 0, normA = 0, normB = 0;
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}