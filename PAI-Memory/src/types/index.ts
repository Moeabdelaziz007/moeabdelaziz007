export interface MemoryLayerConfig {
  L1: { type: 'sqlite-vec'; capacity: '10K vectors'; ttl: 'session' };
  L2: { type: 'pgvector'; capacity: '10GB'; ttl: '30 days' };
  L3: { type: 'pgvector'; capacity: '0.5GB'; ttl: 'permanent' };
  L4: { type: 'qdrant'; capacity: 'project-dependent'; ttl: 'permanent' };
  L5: { type: 'sigstore'; capacity: 'unlimited'; ttl: 'permanent' };
  L6: { type: 'firestore'; capacity: '1GB'; ttl: 'real-time' };
  L7: { type: 'r2-parquet'; capacity: 'unlimited'; ttl: 'permanent' };
}

export interface MemoryEntry {
  id: string;
  layer: 'L1' | 'L2' | 'L3' | 'L4' | 'L5' | 'L6' | 'L7';
  content: string;
  embedding?: number[];
  metadata: {
    tags: string[];
    source: string;
    intention?: string;
    sessionId?: string;
    confidence: number;
    ttl?: number;
  };
  createdAt: number;
  accessedAt: number;
  accessCount: number;
}

export interface MemoryQuery {
  query: string;
  layers?: ('L1' | 'L2' | 'L3' | 'L4' | 'L5' | 'L6' | 'L7')[];
  limit?: number;
  minConfidence?: number;
  tags?: string[];
}

export interface MemoryResult extends MemoryEntry {
  similarity?: number;
}

export interface MemoryRouter {
  route(query: MemoryQuery): Promise<MemoryResult[]>;
  promote(entryId: string, fromLayer: string, toLayer: string): Promise<void>;
  archive(entryId: string): Promise<void>;
}

export interface LayerConfig {
  name: string;
  capacity: number;
  ttl: number;
  embeddingModel?: string;
  searchMethod: 'vector' | 'text' | 'hybrid' | 'audit' | 'sync' | 'archive';
}