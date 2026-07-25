# PAI-Memory — 7-Layer Agent Memory

Persistent. Verifiable. Shared. The memory layer for the PAI ecosystem.

## Architecture

```
pai-list/PAI-Memory/
├── src/
│   ├── layers/            # 7 memory layers
│   │   ├── L1-hot-cache.ts        # sqlite-vec, sub-ms, current session
│   │   ├── L2-warm-session.ts     # Ghost/TigerData, 10GB pgvector
│   │   ├── L3-facts-knowledge.ts  # Neon pgvector, 0.5GB SQL+vector
│   │   ├── L4-code-memory.ts      # Qdrant local, symbol/file filtering
│   │   ├── L5-trust-chain.ts      # Sigstore/Rekor, immutable audit
│   │   ├── L6-edge-sync.ts        # Firestore, real-time + offline
│   │   └── L7-cold-archive.ts     # R2 + Parquet, compliance/forensics
│   ├── core/              # Core memory system
│   │   ├── memory-router.ts       # Layer routing & promotion
│   │   ├── embedding.ts           # Embedding generation & search
│   │   ├── promotion.ts           # Cross-layer promotion rules
│   │   ├── retrieval.ts           # Multi-layer retrieval
│   │   └── serialization.ts       # Parquet/Arrow serialization
│   ├── integration/       # System integrations
│   │   ├── adp.ts                 # ADP agent discovery → memory
│   │   ├── axiomid.ts             # AxiomID TrustChain anchoring
│   │   ├── workspace.ts           # Global workspace memory pool
│   │   └── mcp.ts                 # MCP tool memory
│   └── utils/             # Utilities
│       ├── hashing.ts
│       ├── compression.ts
│       └── validation.ts
│
├── templates/           # Memory configurations
│   ├── agent-personal/
│   ├── workspace-shared/
│   ├── compliance-archive/
│   └── code-repository/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── LAYERS.md
│   ├── INTEGRATION.md
│   └── DEPLOYMENT.md
│
├── examples/
│   ├── personal-agent/
│   ├── workspace-team/
│   ├── codebase-indexing/
│   └── compliance-audit/
│
├── wrangler.jsonc
├── package.json
├── tsconfig.json
├── vitest.config.ts
└── README.md
```

## The 7 Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    PAI-MEMORY 7-LAYER STACK                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  L1  Hot Cache      sqlite-vec        sub-ms, current session   │
│  ──────────────────────────────────────────────────────────────  │
│  L2  Warm Session   Ghost/TigerData   10GB pgvector, no pause   │
│  ──────────────────────────────────────────────────────────────  │
│  L3  Facts/Knowl.   Neon pgvector     0.5GB SQL + vector        │
│  ──────────────────────────────────────────────────────────────  │
│  L4  Code Memory    Qdrant local       symbol/file/lang filter   │
│  ──────────────────────────────────────────────────────────────  │
│  L5  Trust Chain    Sigstore/Rekor    immutable audit trail      │
│  ──────────────────────────────────────────────────────────────  │
│  L6  Edge Sync      Firestore         real-time + offline        │
│  ──────────────────────────────────────────────────────────────  │
│  L7  Cold Archive   R2 + Parquet      compliance, forensics      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Details

### L1 — Hot Cache (sqlite-vec)
- **Purpose**: Sub-millisecond recall for current session
- **Storage**: sqlite-vec in Durable Object memory
- **Capacity**: ~10K vectors, 100MB
- **TTL**: Session lifetime
- **Use case**: Current conversation, working context, tool results

### L2 — Warm Session (Ghost/TigerData pgvector)
- **Purpose**: Recent sessions, no cold-start penalty
- **Storage**: pgvector on Ghost/TigerData
- **Capacity**: 10GB, ~1M vectors
- **TTL**: 30 days
- **Use case**: Session history, user preferences, learned patterns

### L3 — Facts & Knowledge (Neon pgvector)
- **Purpose**: Persistent facts, learned knowledge
- **Storage**: Neon pgvector (PostgreSQL)
- **Capacity**: 0.5GB, ~500K vectors
- **TTL**: Permanent
- **Use case**: Facts, procedures, domain knowledge, user info

### L4 — Code Memory (Qdrant local)
- **Purpose**: Codebase understanding, symbol navigation
- **Storage**: Qdrant local (Docker)
- **Capacity**: Project-dependent
- **Features**: Symbol/file/lang/type filtering, AST-aware chunking
- **Use case**: Code search, refactoring, architecture understanding

### L5 — Trust Chain (Sigstore/Rekor)
- **Purpose**: Immutable audit trail for every memory write
- **Storage**: Sigstore/Rekor transparency log
- **Features**: Cryptographic proof, tamper-evident, verifiable
- **Use case**: Compliance, forensics, agent accountability

### L6 — Edge Sync (Firestore)
- **Purpose**: Real-time sync across devices/agents
- **Storage**: Cloudflare Firestore (or Firebase)
- **Features**: Offline-first, conflict resolution, presence
- **Use case**: Multi-device agents, workspace collaboration

### L7 — Cold Archive (R2 + Parquet)
- **Purpose**: Long-term compliance, forensics, analytics
- **Storage**: R2 + Apache Parquet
- **Capacity**: Unlimited, cost-optimized
- **Features**: Partitioned by time/agent/type, columnar queries
- **Use case**: Regulatory compliance, historical analysis, training data

## Memory Router

```
Query → Router → Layer Selection → Parallel Search → Merge & Rank → Results
              │
              ├── L1 (hot) ──→ sub-ms, if recent
              ├── L2 (warm) ──→ if session-related
              ├── L3 (facts) ──→ if factual query
              ├── L4 (code) ──→ if code-related
              ├── L5 (audit) ──→ if compliance query
              ├── L6 (sync) ──→ if multi-device
              └── L7 (archive) ──→ if historical/compliance
```

## Integration

| System | What It Gets |
|--------|--------------|
| **ADP** | Agent sees other agents' shared memory |
| **AxiomID** | TrustChain anchors every memory write |
| **Global Workspace** | Pooled memory across agent team |
| **ACP** | Memory as sellable service on Virtuals |

## Quick Start

```bash
# Install
npm install -g @pai/memory

# Initialize memory for agent
pai-memory init --agent my-agent --layers L1,L2,L3

# Store memory
pai-memory remember "User prefers dark mode" --layer L1 --tags preference,ui

# Recall
pai-memory recall "dark mode" --layers L1,L2

# Search code
pai-memory code-search "authentication" --lang typescript
```

## Deployment (Free Tier)

| Layer | Service | Free Tier |
|-------|---------|-----------|
| L1 | Durable Object memory | Workers free |
| L2 | Ghost pgvector | 10GB free |
| L3 | Neon pgvector | 0.5GB free |
| L4 | Qdrant local | Docker on Workers |
| L5 | Sigstore | Free public |
| L6 | Firestore | 1GB free |
| L7 | R2 + Parquet | 10GB free |

## License

MIT — Free for all agents, all humans, all purposes.

---

*PAI-Memory by Mohamed Abdelaziz. Part of the PAI ecosystem.*