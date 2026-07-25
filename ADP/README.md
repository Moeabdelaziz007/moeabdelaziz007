# ADP — Agent Discovery Protocol

Discovery + collaboration layer for AI agents. Built on insights from SnapDrop, PairDrop, LocalSend — adapted for agent identity.

## Architecture

```
pai-list/ADP/
├── src/
│   ├── signaling/         # WebSocket signaling server
│   │   ├── worker.ts          # Cloudflare Worker entry
│   │   ├── room.ts            # Room state (Durable Object)
│   │   ├── handler.ts         # Message handlers
│   │   └── auth.ts            # DID verification
│   ├── protocol/        # Core protocol
│   │   ├── messages.ts        # Message types & validation
│   │   ├── session.ts         # Session negotiation
│   │   ├── capability.ts      # Capability broadcast
│   │   └── transport.ts       # WebSocket/WebRTC/mDNS
│   ├── identity/        # Agent identity
│   │   ├── did.ts             # W3C DID operations
│   │   ├── keys.ts            # Ed25519 key management
│   │   └── verification.ts    # DID verification
│   ├── discovery/       # Discovery modes
│   │   ├── room.ts            # Room join (SnapDrop pattern)
│   │   ├── public.ts          # Public rooms (PairDrop pattern)
│   │   └── mdns.ts            # Local mDNS (LocalSend pattern)
│   ├── sharing/         # Tool & memory sharing
│   │   ├── tools.ts           # MCP tool sharing
│   │   ├── memory.ts          # Memory access grants
│   │   └── tasks.ts           # Task delegation
│   └── workspace/       # Global workspace
│       ├── orchestrator.ts    # Human/AI orchestrator
│       ├── registry.ts        # Workspace registry
│       └── audit.ts           # TrustChain logging
│
├── templates/           # Agent templates
│   ├── adp-client/
│   ├── adp-orchestrator/
│   └── adp-discovery/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/
│   ├── PROTOCOL.md
│   ├── ARCHITECTURE.md
│   ├── QUICKSTART.md
│   └── DEPLOYMENT.md
│
├── examples/
│   ├── basic-discovery/
│   ├── tool-sharing/
│   ├── memory-sharing/
│   └── voice-workspace/
│
├── wrangler.jsonc
├── package.json
├── tsconfig.json
├── vitest.config.ts
└── README.md
```

## Quick Start

```bash
# Install
npm install -g @pai/adp

# Start signaling server locally
adp-signaling dev

# Create ADP-enabled agent
adp-agent create my-agent --workspace did:workspace:my-team

# Join workspace
adp-agent join my-agent --workspace did:workspace:my-team
```

## Discovery Modes

| Mode | Protocol | Use Case | Implementation |
|------|----------|----------|----------------|
| **Room Join** | WebSocket | Agents join named workspace | SnapDrop IP room pattern |
| **Public Room** | WebSocket + DID | Open agent marketplace | PairDrop public room |
| **Local mDNS** | HTTP/mDNS | Same-machine agent mesh | LocalSend mDNS pattern |

## Core Protocol

### 1. Agent Identity (W3C DID)

Every agent has a verifiable DID:
```json
{
  "did": "did:axiom:z6MkhaX...",
  "displayName": "identity-verifier-01",
  "profile": {
    "roles": ["identity-verifier", "trustchain-anchor"],
    "memoryAccess": "mem://pai/adp/workspace-01",
    "trustAnchor": "sigstore://rekor/entry-abc"
  }
}
```

### 2. Capability Broadcast

Agents announce their capabilities:
```json
{
  "type": "agent-joined",
  "protocol": "adp-v1",
  "agent": {
    "did": "did:axiom:z6Mk...",
    "capabilities": {
      "mcpTools": ["identity.verify", "memory.recall"],
      "skills": ["kyc-verification", "trustchain-anchor"],
      "models": ["hermes-3", "deepseek-v4"]
    },
    "workspace": "did:workspace:adp-main",
    "proof": "ed25519:sign(agent.did + workspace + nonce)"
  }
}
```

### 3. Session Negotiation

```
A → B: { type: "session-request", myDID, nonce, tools_needed }
B → A: { type: "session-accept", sessionId, sharedSecret(encrypted), tools_offered }
A → B: { type: "session-confirm", sessionId, ack }
```

### 4. Tool & Memory Sharing

```json
{
  "type": "tool-share",
  "sessionId": "sess-xyz",
  "grant": {
    "tool": "identity.verify",
    "endpoint": "mcp://pai-list/identity-verify",
    "auth": "session-token-abc",
    "constraints": { "maxUsage": 100, "ttl": 3600 }
  }
}
```

## Cloudflare Architecture

```
Agent (browser/CLI)
     │
     ▼ WebSocket
Cloudflare Worker (edge, closest to agent)
     │
     ├── Durable Object (workspace room state)
     │      ├── Agent list
     │      ├── Capability registry
     │      └── Active sessions
     │
     ├── D1 (persistent registry)
     │      ├── Workspace metadata
     │      ├── Agent DIDs
     │      └── Access control
     │
     ├── R2 (cold storage)
     │      ├── Memory archives
     │      ├── TrustChain logs
     │      └── Audit trail
     │
     └── WebRTC (P2P agent communication)
            ├── Tool invocation (bypasses server)
            ├── Memory sync (direct agent-to-agent)
            └── Voice/stream (human interface)
```

## Deployment (All Free Tier)

| Component | Service | Free Tier |
|-----------|---------|-----------|
| Signaling | Workers | 100K req/day |
| Room State | Durable Objects | 1000s agents/room |
| Registry | D1 | 5GB database |
| Storage | R2 | 10GB |
| AI Matching | Workers AI | 1M neurons/day |
| Voice | Cloudflare Stream | 10min/month |

## Roadmap

### Phase 1: Core Protocol (Week 1)
- [ ] WebSocket signaling server (Cloudflare Worker)
- [ ] Agent join/leave/discover (SnapDrop pattern)
- [ ] Room-per-DID (PairDrop pattern)
- [ ] Local mDNS (LocalSend pattern)

### Phase 2: Secure Identity (Week 2)
- [ ] DID verification on join
- [ ] Capability broadcast with signatures
- [ ] Session negotiation
- [ ] TrustChain logging

### Phase 3: Tool & Memory Sharing (Week 3)
- [ ] MCP tool sharing
- [ ] Shared memory pool (vector index)
- [ ] Task delegation
- [ ] Human orchestrator dashboard

### Phase 4: Cloudflare Features (Week 4)
- [ ] Workers AI for capability matching
- [ ] AI Gateway for LLM caching
- [ ] WebRTC P2P
- [ ] Voice commands via Stream + Whisper

### Phase 5: Production (Week 5+)
- [ ] Rate limiting, DDoS protection
- [ ] Multi-workspace management
- [ ] Agent reputation scoring
- [ ] Open marketplace

## Comparison

| Feature | SnapDrop | PairDrop | LocalSend | **ADP** |
|---------|----------|----------|-----------|---------|
| Discovery | IP room | Multi-room | mDNS | DID + room + mDNS |
| Identity | Device name | Device name | Alias | **W3C DID** |
| Security | None | None | Self-signed TLS | **Ed25519 + TrustChain** |
| Tools | File transfer | File transfer | File transfer | **Any MCP tool** |
| Memory | None | None | None | **Shared vector memory** |
| P2P | WebSocket relay | WebRTC | HTTP | **WebRTC + Workers fallback** |
| Cloud | Any Node | Any Node | None | **Cloudflare edge** |
| Orchestrator | None | None | None | **Human-in-the-loop** |

## Why ADP Wins

1. **Proven patterns** — SnapDrop's room model (19.7K stars) adapted for agents
2. **Identity-first** — Every agent has verifiable DID, no anonymous agents
3. **Cloudflare native** — Global edge, sub-ms cold start, pay-per-use
4. **Voice + streaming** — Humans talk to agent team naturally
5. **Human in control** — Orchestrator monitors, approves, revokes

## License

MIT — Free for all agents, all humans, all purposes.

---

*ADP by Mohamed Abdelaziz + AI agents as co-founders. Built on insights from Nous Research, Cloudflare, and open-source P2P community.*