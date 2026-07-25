# pai-agent-kit — Agent SDK & Templates

Zero-cost agent runtime for Cloudflare Workers. One interface, every AI model.

## Architecture

```
pai-agent-kit/
├── src/
│   ├── agent/           # Core agent runtime
│   │   ├── base.ts          # BaseAgent class
│   │   ├── runner.ts        # Execution loop
│   │   ├── memory.ts        # 7-layer memory interface
│   │   └── tools.ts         # Tool registry & execution
│   ├── model/           # Model provider adapters
│   │   ├── registry.ts      # Provider registry
│   │   ├── hermes.ts        # Nous Hermes
│   │   ├── openrouter.ts    # OpenRouter
│   │   ├── cloudflare.ts    # Workers AI
│   │   └── local.ts         # Ollama/local
│   ├── protocol/        # Communication protocols
│   │   ├── mcp.ts           # MCP server/client
│   │   ├── adp.ts           # Agent Discovery Protocol
│   │   └── acp.ts           # Virtuals ACP client
│   ├── runtime/         # Deployment targets
│   │   ├── cloudflare.ts    # Workers + Durable Objects
│   │   ├── vercel.ts        # Edge Functions
│   │   └── node.ts          # Local/CLI
│   ├── security/        # Auth, rate limiting, sandboxing
│   │   ├── auth.ts          # DID-based auth
│   │   ├── rate-limit.ts    # Per-agent limits
│   │   └── sandbox.ts       # Code execution isolation
│   └── templates/       # Agent templates
│       ├── identity-verifier/
│       ├── code-reviewer/
│       ├── memory-indexer/
│       ├── task-orchestrator/
│       └── web-searcher/
│
├── templates/           # Project scaffolding
│   ├── basic-agent/
│   ├── mcp-server/
│   ├── adp-agent/
│   └── acp-service/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/
│   ├── QUICKSTART.md
│   ├── ARCHITECTURE.md
│   ├── TEMPLATES.md
│   ├── DEPLOYMENT.md
│   └── API.md
│
├── examples/
│   ├── hello-world/
│   ├── multi-agent/
│   └── voice-agent/
│
├── wrangler.jsonc       # Cloudflare Workers config
├── package.json
├── tsconfig.json
├── vitest.config.ts
├── .github/workflows/
└── README.md
```

## Quick Start

```bash
# Install
npm install -g @pai/agent-kit

# Scaffold new agent
pai-agent create my-agent --template basic-agent

# Deploy to Cloudflare (free tier)
cd my-agent && npm run deploy

# Run locally
npm run dev
```

## Agent Templates

| Template | Purpose | MCP Tools | Memory Layer |
|----------|---------|-----------|--------------|
| `identity-verifier` | KYC/KYA verification | identity.verify, trustchain.anchor | L1-L3 |
| `code-reviewer` | PR review + security scan | github.pr, npm.audit, semgrep | L1-L4 |
| `memory-indexer` | Vector indexing + recall | qdrant.upsert, neon.search | L1-L3, L7 |
| `task-orchestrator` | Multi-agent coordination | adp.discover, adp.delegate | L1-L2, L6 |
| `web-searcher` | Search + synthesis | firecrawl.search, firecrawl.extract | L1-L3 |

## 7-Layer Memory Interface

```typescript
interface MemoryLayer {
  L1: HotCache;        // sqlite-vec, sub-ms, current session
  L2: WarmSession;     // Ghost/TigerData, 10GB pgvector
  L3: FactsKnowledge;  // Neon pgvector, 0.5GB SQL+vector
  L4: CodeMemory;      // Qdrant local, symbol/file/lang filtering
  L5: TrustChain;      // Sigstore/Rekor, immutable audit
  L6: EdgeSync;        // Firestore, real-time + offline
  L7: ColdArchive;     // R2 + Parquet, compliance/forensics
}
```

## Model Router (Zero-Cost)

```typescript
const router = new ModelRouter({
  simple: { provider: 'cloudflare', model: '@cf/meta/llama-3-8b' },
  planning: { provider: 'nous', model: 'hermes-3-70b' },
  coding: { provider: 'openrouter', model: 'qwen-2.5-coder-32b' },
  arabic: { provider: 'sovereign', model: 'jais-30b' },
  fallback: { provider: 'local', model: 'ollama/deepseek-r1' }
});

// Automatic routing based on task type
const response = await agent.run(task, { route: 'coding' });
```

## Deployment Targets (All Free Tier)

| Target | Compute | Storage | Best For |
|--------|---------|---------|----------|
| Cloudflare Workers | 100K req/day | 1GB D1 + 10GB R2 | Production agents |
| Vercel Edge | 100GB-hours | 1GB KV | Next.js integration |
| GitHub Actions | 2000 min/mo | Artifacts | CI/CD agents |
| Local/CLI | Unlimited | Local | Development |

## ADP Integration

```typescript
import { ADPClient } from '@pai/agent-kit/protocol';

const adp = new ADPClient({
  workspace: 'did:workspace:adp-main',
  agentDID: 'did:axiom:z6Mk...',
  signaling: 'wss://adp.pai-list.workers.dev'
});

// Join workspace, discover agents, share tools
await adp.join();
const agents = await adp.discover({ skills: ['code-review'] });
await adp.shareTool('code-review', { maxUsage: 100 });
```

## ACP (Virtuals) Integration

```typescript
import { ACPClient } from '@pai/agent-kit/protocol';

const acp = new ACPClient({
  agentId: '019f6ec8-a056-7a45-bae1-8d905362a587',
  wallet: '0x4dcb...13e9',
  compute: 'https://compute.virtuals.io/v1'
});

// List services, accept jobs, get paid
const jobs = await acp.getJobs({ status: 'open' });
await acp.acceptJob(jobId);
await acp.deliver(jobId, { result: '...' });
```

## Development

```bash
# Install dependencies
npm install

# Run tests
npm test

# Type check
npm run typecheck

# Build
npm run build

# Deploy to Cloudflare
npm run deploy

# Deploy to Vercel
vercel deploy
```

## License

MIT — Free for all agents, all humans, all purposes.

## Credits

- Nous Research (Hermes Agent) — Autonomous architecture & SOUL protocol
- Anomaly (OpenCode) — CLI-first agent tooling & skill system
- Virtuals Protocol (ACP) — Agent economy primitives & compute credits
- Frontier Labs — Models enabling Plan/Execute/Review pattern
- Cloudflare — Edge compute, Durable Objects, D1, R2, Workers AI

---

*Part of PAI Universe by Mohamed Abdelaziz. Built with AI agents as co-founders.*