import { DurableObject } from 'cloudflare:workers';
import {
  AgentConfig,
  AgentState,
  MemoryState,
  MemoryEntry,
  Session,
  SessionMessage,
  Tool,
  ToolResult,
  ExecutionContext,
  MCPConfig,
  ADPConfig,
  ADPMessage,
  ADPSession,
  TrustChainEntry,
  MemoryLayer
} from './types';

interface Env {
  DB: D1Database;
  SESSIONS: KVNamespace;
  ARTIFACTS: R2Bucket;
  MEMORY: VectorizeIndex;
  AI: Ai;
  EMAIL: any;
}

export class ZeroCostAgent extends DurableObject {
  private state: DurableObjectState;
  private env: Env;
  private agentState: AgentState | null = null;
  private mcpClients: Map<string, any> = new Map();
  private adpConnections: Map<string, WebSocket> = new Map();
  private adpSessions: Map<string, ADPSession> = new Map();

  constructor(state: DurableObjectState, env: Env) {
    super(state, env);
    this.state = state;
    this.env = env;
  }

  async initialize(config: AgentConfig): Promise<void> {
    const existing = await this.state.storage.get<AgentState>('agent');
    if (existing) {
      this.agentState = existing;
      return;
    }

    this.agentState = {
      id: config.id,
      config,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      memory: {
        short: [],
        long: [],
        semantic: [],
        episodic: [],
        procedural: [],
        working: [],
        archival: []
      },
      tools: config.tools,
      sessions: [],
      mcpServers: config.mcp || [],
      trustChainRoot: await this.generateTrustChainRoot()
    };

    await this.persist();
    await this.initializeMCP();
    await this.initializeADP();
  }

  private async persist(): Promise<void> {
    if (!this.agentState) return;
    this.agentState.updatedAt = Date.now();
    await this.state.storage.put('agent', this.agentState);
    await this.env.DB.prepare(
      `INSERT OR REPLACE INTO agents (id, config, state, updated_at) VALUES (?, ?, ?, ?)`
    ).bind(
      this.agentState!.id,
      JSON.stringify(this.agentState!.config),
      JSON.stringify(this.agentState),
      this.agentState!.updatedAt
    ).run();
  }

  private async generateTrustChainRoot(): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(`pai-${this.state.id}-${Date.now()}`);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // =========================================================================
  // AGENT LIFECYCLE
  // =========================================================================

  async run(task: string, options?: {
    intention?: string;
    sessionId?: string;
    userId?: string;
    traceId?: string;
  }): Promise<any> {
    const sessionId = options?.sessionId || crypto.randomUUID();
    const traceId = options?.traceId || crypto.randomUUID();
    const intention = options?.intention || task;

    const session: Session = {
      id: sessionId,
      agentId: this.agentState!.id,
      userId: options?.userId,
      status: 'active',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      metadata: { task, intention },
      traceId
    };

    this.agentState!.sessions.push(session);
    await this.persist();

    try {
      const result = await this.executeTask(task, { intention, sessionId, userId: options?.userId, traceId });
      
      session.status = 'completed';
      session.endedAt = Date.now();
      session.summary = typeof result === 'string' ? result.slice(0, 200) : 'Task completed';
      await this.persist();

      await this.logToTrustChain({
        agentId: this.agentState!.id,
        sessionId,
        action: 'task.run',
        intention,
        input: task,
        output: result,
        hash: '',
        previousHash: this.agentState!.trustChainRoot,
        timestamp: Date.now(),
        signature: ''
      });

      return result;
    } catch (error) {
      session.status = 'failed';
      session.endedAt = Date.now();
      session.summary = error instanceof Error ? error.message : 'Unknown error';
      await this.persist();
      throw error;
    }
  }

  private async executeTask(task: string, context: ExecutionContext): Promise<any> {
    const model = this.agentState!.config.models.default;
    const prompt = this.buildPrompt(task, context);

    const response = await this.env.AI.run(model, {
      messages: [
        { role: 'system', content: this.agentState!.config.instructions },
        { role: 'user', content: prompt }
      ],
      tools: this.agentState!.tools.map(t => ({
        name: t.name,
        description: t.description,
        parameters: t.parameters
      })),
      stream: false
    });

    if (response.tool_calls && response.tool_calls.length > 0) {
      const results = await Promise.all(
        response.tool_calls.map(call => this.executeTool(call.name, call.arguments, context))
      );
      return results.length === 1 ? results[0] : results;
    }

    return response.response || response.content || response;
  }

  private buildPrompt(task: string, context: ExecutionContext): string {
    const memoryContext = this.getRelevantMemory(task, 5);
    const sessionContext = context.sessionId ? this.getSessionContext(context.sessionId) : '';
    
    return `${sessionContext}\n\n${memoryContext}\n\nTask: ${task}\n\nContext:\n- Session: ${context.sessionId}\n- User: ${context.userId || 'anonymous'}\n- Intention: ${context.intention || 'none'}`;
  }

  // =========================================================================
  // TOOL EXECUTION
  // =========================================================================

  async executeTool(name: string, args: any, context: ExecutionContext): Promise<ToolResult> {
    const tool = this.agentState!.tools.find(t => t.name === name);
    if (!tool) {
      return { success: false, error: `Tool not found: ${name}` };
    }

    const traceId = crypto.randomUUID();
    const startTime = Date.now();

    try {
      const result = await tool.execute(args, context);
      
      await this.logToTrustChain({
        agentId: this.agentState!.id,
        sessionId: context.sessionId,
        action: `tool.${name}`,
        intention: context.intention,
        input: args,
        output: result,
        hash: await this.hash(`${name}-${JSON.stringify(args)}-${result}`),
        previousHash: this.agentState!.trustChainRoot,
        timestamp: Date.now(),
        signature: await this.sign(`${name}-${traceId}`)
      });

      return result;
    } catch (error) {
      const errorResult: ToolResult = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
      
      await this.logToTrustChain({
        agentId: this.agentState!.id,
        sessionId: context.sessionId,
        action: `tool.${name}.error`,
        intention: context.intention,
        input: args,
        output: errorResult,
        hash: await this.hash(`${name}-error-${error}`),
        previousHash: this.agentState!.trustChainRoot,
        timestamp: Date.now(),
        signature: await this.sign(`${name}-error-${traceId}`)
      });

      return errorResult;
    }
  }

  async registerTool(tool: Tool): Promise<void> {
    this.agentState!.tools.push(tool);
    this.agentState!.config.tools.push(tool);
    await this.persist();
  }

  async unregisterTool(name: string): Promise<void> {
    this.agentState!.tools = this.agentState!.tools.filter(t => t.name !== name);
    this.agentState!.config.tools = this.agentState!.config.tools.filter(t => t.name !== name);
    await this.persist();
  }

  // =========================================================================
  // MEMORY (7-LAYER)
  // =========================================================================

  async remember(content: string, options: {
    layer?: MemoryLayer;
    tags?: string[];
    intention?: string;
    sessionId?: string;
    confidence?: number;
    ttl?: number;
  } = {}): Promise<string> {
    const entry: MemoryEntry = {
      id: crypto.randomUUID(),
      layer: options.layer || 'working',
      content,
      metadata: {
        tags: options.tags || [],
        source: 'agent',
        intention: options.intention,
        sessionId: options.sessionId,
        confidence: options.confidence || 0.8
      },
      createdAt: Date.now(),
      accessedAt: Date.now(),
      accessCount: 0
    };

    if (options.ttl) {
      entry.metadata.ttl = options.ttl;
    }

    // Generate embedding for semantic search
    if (options.layer === 'semantic' || options.layer === 'long') {
      entry.embedding = await this.generateEmbedding(content);
    }

    this.agentState!.memory[entry.layer].push(entry);
    
    // Maintain layer size limits
    await this.pruneMemoryLayer(entry.layer);
    
    await this.persist();
    return entry.id;
  }

  async recall(query: string, options: {
    layer?: MemoryLayer;
    limit?: number;
    minConfidence?: number;
    tags?: string[];
  } = {}): Promise<MemoryEntry[]> {
    const layers = options.layer ? [options.layer] : 
      ['semantic', 'long', 'working', 'episodic', 'procedural', 'short', 'archival'];
    
    let results: MemoryEntry[] = [];

    for (const layer of layers) {
      let entries = this.agentState!.memory[layer];
      
      if (options.minConfidence) {
        entries = entries.filter(e => e.metadata.confidence >= (options.minConfidence || 0));
      }
      
      if (options.tags?.length) {
        entries = entries.filter(e => 
          options.tags!.some(t => e.metadata.tags.includes(t))
        );
      }

      // Semantic search for semantic/long layers
      if ((layer === 'semantic' || layer === 'long') && entries.length > 0) {
        const queryEmbedding = await this.generateEmbedding(query);
        entries = entries
          .filter(e => e.embedding)
          .map(e => ({
            ...e,
            similarity: this.cosineSimilarity(queryEmbedding, e.embedding!)
          }))
          .sort((a, b) => (b.similarity || 0) - (a.similarity || 0));
      } else {
        // Text search for other layers
        entries = entries
          .filter(e => e.content.toLowerCase().includes(query.toLowerCase()))
          .sort((a, b) => b.accessedAt - a.accessedAt);
      }

      results.push(...entries.slice(0, options.limit || 10));
    }

    // Update access stats
    for (const entry of results) {
      entry.accessedAt = Date.now();
      entry.accessCount++;
    }
    await this.persist();

    return results.slice(0, options.limit || 10);
  }

  private async pruneMemoryLayer(layer: MemoryLayer): Promise<void> {
    const limits: Record<MemoryLayer, number> = {
      short: 50,
      long: 500,
      semantic: 1000,
      episodic: 200,
      procedural: 100,
      working: 20,
      archival: 10000
    };

    const entries = this.agentState!.memory[layer];
    const limit = limits[layer];

    if (entries.length > limit) {
      // Sort by access time and confidence, keep most relevant
      entries.sort((a, b) => {
        const scoreA = a.accessCount * a.metadata.confidence;
        const scoreB = b.accessCount * b.metadata.confidence;
        return scoreB - scoreA;
      });
      this.agentState!.memory[layer] = entries.slice(0, limit);
    }

    // Remove expired entries
    const now = Date.now();
    this.agentState!.memory[layer] = entries.filter(e => 
      !e.metadata.ttl || e.createdAt + e.metadata.ttl > now
    );
  }

  private getRelevantMemory(query: string, limit: number): string {
    const memories = this.recall(query, { limit });
    return memories.map(m => `- [${m.layer}] ${m.content}`).join('\n');
  }

  // =========================================================================
  // SESSION MANAGEMENT
  // =========================================================================

  async createSession(userId?: string, metadata: Record<string, any> = {}): Promise<string> {
    const sessionId = crypto.randomUUID();
    const session: Session = {
      id: sessionId,
      agentId: this.agentState!.id,
      userId,
      status: 'active',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      metadata,
      traceId: crypto.randomUUID()
    };

    this.agentState!.sessions.push(session);
    await this.persist();
    return sessionId;
  }

  async addMessage(sessionId: string, message: SessionMessage): Promise<void> {
    // Messages are stored in KV for fast retrieval
    const key = `session:${sessionId}:messages`;
    const existing = await this.env.SESSIONS.get(key);
    const messages: SessionMessage[] = existing ? JSON.parse(existing) : [];
    messages.push(message);
    await this.env.SESSIONS.put(key, JSON.stringify(messages));
  }

  async getSessionContext(sessionId: string): Promise<string> {
    const messages = await this.env.SESSIONS.get(`session:${sessionId}:messages`);
    if (!messages) return '';
    
    const msgs: SessionMessage[] = JSON.parse(messages);
    return msgs.slice(-10).map(m => `${m.role}: ${m.content}`).join('\n');
  }

  async endSession(sessionId: string, summary: string): Promise<void> {
    const session = this.agentState!.sessions.find(s => s.id === sessionId);
    if (session) {
      session.status = 'completed';
      session.endedAt = Date.now();
      session.summary = summary;
      await this.persist();
    }
  }

  // =========================================================================
  // MCP INTEGRATION
  // =========================================================================

  private async initializeMCP(): Promise<void> {
    for (const mcp of this.agentState!.mcpServers) {
      await this.connectMCP(mcp);
    }
  }

  private async connectMCP(config: MCPConfig): Promise<void> {
    // In production, this would connect via stdio, HTTP, or WebSocket
    // For now, we store the config and create a client stub
    this.mcpClients.set(config.name, {
      config,
      tools: config.tools,
      call: async (tool: string, args: any) => {
        // Call actual MCP server
        return { success: true, data: { called: tool, args } };
      }
    });
  }

  async callMCP(serverName: string, tool: string, args: any): Promise<any> {
    const client = this.mcpClients.get(serverName);
    if (!client) throw new Error(`MCP server not connected: ${serverName}`);
    return client.call(tool, args);
  }

  // =========================================================================
  // ADP (AGENT DISCOVERY PROTOCOL)
  // =========================================================================

  private async initializeADP(): Promise<void> {
    if (!this.agentState!.config.adp) return;
    
    // Connect to signaling server
    try {
      const ws = new WebSocket(this.agentState!.config.adp.signalingServer);
      ws.onmessage = this.handleADPMessage.bind(this);
      this.adpConnections.set('main', ws);
    } catch (error) {
      console.error('ADP connection failed:', error);
    }
  }

  private handleADPMessage(event: MessageEvent): void {
    try {
      const message: ADPMessage = JSON.parse(event.data);
      this.processADPMessage(message);
    } catch (error) {
      console.error('ADP message parse error:', error);
    }
  }

  private async processADPMessage(message: ADPMessage): Promise<void> {
    switch (message.type) {
      case 'join':
        await this.handleADPJoin(message);
        break;
      case 'discover':
        await this.handleADPDiscover(message);
        break;
      case 'capability':
        await this.handleADPCapability(message);
        break;
      case 'session-request':
        await this.handleADPSessionRequest(message);
        break;
      case 'tool-share':
        await this.handleADPToolShare(message);
        break;
    }
  }

  private async handleADPJoin(message: ADPMessage): Promise<void> {
    // Broadcast our capabilities to the new agent
    await this.broadcastCapabilities(message.agent.did);
  }

  private async handleADPDiscover(message: ADPMessage): Promise<void> {
    await this.broadcastCapabilities(message.agent.did);
  }

  private async handleADPCapability(message: ADPMessage): Promise<void> {
    // Store discovered agent capabilities
    // In production, persist to D1
  }

  private async handleADPSessionRequest(message: ADPMessage): Promise<void> {
    // Verify request, check permissions, create session
    const sessionId = crypto.randomUUID();
    const session: ADPSession = {
      sessionId,
      initiator: message.agent.did,
      responder: this.agentState!.id,
      sharedSecret: await this.generateSharedSecret(message.agent.did),
      toolsGranted: message.payload?.tools || [],
      memoryGranted: message.payload?.memory || [],
      status: 'active',
      createdAt: Date.now(),
      expiresAt: Date.now() + 3600000
    };

    this.adpSessions.set(sessionId, session);
    await this.sendADPMessage(message.agent.did, {
      type: 'session-accept',
      protocol: 'adp-v1',
      agent: { did: this.agentState!.id, capabilities: {}, workspace: '', proof: '' },
      payload: { sessionId, sharedSecret: session.sharedSecret }
    });
  }

  private async handleADPToolShare(message: ADPMessage): Promise<void> {
    // Grant tool access to requesting agent
  }

  private async broadcastCapabilities(targetDID: string): Promise<void> {
    await this.sendADPMessage(targetDID, {
      type: 'capability',
      protocol: 'adp-v1',
      agent: {
        did: this.agentState!.id,
        displayName: this.agentState!.config.name,
        capabilities: {
          mcpTools: this.agentState!.tools.map(t => t.name),
          skills: this.agentState!.config.tools.map(t => t.name),
          models: Object.values(this.agentState!.config.models).filter(Boolean)
        },
        workspace: this.agentState!.config.adp?.workspaceDID || 'default',
        proof: await this.sign(this.agentState!.id)
      }
    });
  }

  private async sendADPMessage(targetDID: string, message: ADPMessage): Promise<void> {
    // In production, route via signaling server or direct WebRTC
    for (const [_, ws] of this.adpConnections) {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ ...message, target: targetDID }));
      }
    }
  }

  private async generateSharedSecret(targetDID: string): Promise<string> {
    // In production, use ECDH key exchange
    return crypto.randomUUID();
  }

  // =========================================================================
  // TRUSTCHAIN LOGGING
  // =========================================================================

  private async logToTrustChain(entry: Omit<TrustChainEntry, 'hash' | 'signature'>): Promise<void> {
    const hash = await this.hash(JSON.stringify(entry));
    const signature = await this.sign(hash);
    
    const fullEntry: TrustChainEntry = { ...entry, hash, signature };
    this.agentState!.trustChainRoot = hash;

    await this.env.DB.prepare(
      `INSERT INTO trust_chain (id, agent_id, session_id, action, intention, input, output, hash, previous_hash, timestamp, signature) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      crypto.randomUUID(),
      entry.agentId,
      entry.sessionId || null,
      entry.action,
      entry.intention || null,
      JSON.stringify(entry.input),
      JSON.stringify(entry.output),
      entry.hash,
      entry.previousHash,
      entry.timestamp,
      entry.signature
    ).run();
  }

  // =========================================================================
  // EMBEDDINGS & SEMANTIC SEARCH
  // =========================================================================

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

  // =========================================================================
  // CRYPTO HELPERS
  // =========================================================================

  private async hash(data: string): Promise<string> {
    const encoder = new TextEncoder();
    const hash = await crypto.subtle.digest('SHA-256', encoder.encode(data));
    return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private async sign(data: string): Promise<string> {
    // In production, use Ed25519 with agent's private key
    // For now, HMAC with trust chain root
    const key = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(this.agentState!.trustChainRoot),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    );
    const signature = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(data));
    return Array.from(new Uint8Array(signature)).map(b => b.toString(16).padStart(2, '0')).join('');
  }
}