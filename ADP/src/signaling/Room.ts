import { DurableObject } from 'cloudflare:workers';
import { WebSocket } from 'ws';

interface AgentInfo {
  did: string;
  displayName: string;
  capabilities: {
    mcpTools: string[];
    skills: string[];
    models: string[];
  };
  workspace: string;
  proof: string;
  joinedAt: number;
  ws: WebSocket;
}

interface Session {
  sessionId: string;
  initiator: string;
  responder: string;
  sharedSecret: string;
  toolsGranted: string[];
  memoryGranted: string[];
  status: 'pending' | 'active' | 'completed' | 'revoked';
  createdAt: number;
  expiresAt: number;
}

interface Env {
  ADP_ROOM: DurableObjectNamespace;
  DB: D1Database;
  SESSIONS: KVNamespace;
  AI: Ai;
}

export class Room extends DurableObject<Env> {
  private state: DurableObjectState;
  private agents: Map<string, AgentInfo> = new Map();
  private sessions: Map<string, Session> = new Map();
  private messageQueue: Map<string, any[]> = new Map();

  constructor(state: DurableObjectState, env: Env) {
    super(state, env);
    this.state = state;
    this.state.blockConcurrencyWhile(async () => {
      const stored = await this.state.storage.get<{ agents: any; sessions: any }>('room-state');
      if (stored) {
        this.agents = new Map(Object.entries(stored.agents));
        this.sessions = new Map(Object.entries(stored.sessions));
      }
    });
  }

  async join(did: string, ws: WebSocket, agentInfo?: Partial<AgentInfo>): Promise<void> {
    const info: AgentInfo = {
      did,
      displayName: agentInfo?.displayName || `agent-${did.slice(-8)}`,
      capabilities: agentInfo?.capabilities || { mcpTools: [], skills: [], models: [] },
      workspace: agentInfo?.workspace || 'default',
      proof: agentInfo?.proof || '',
      joinedAt: Date.now(),
      ws
    };

    this.agents.set(did, info);
    await this.persist();

    // Broadcast to all other agents
    this.broadcast({
      type: 'agent-joined',
      protocol: 'adp-v1',
      agent: {
        did: info.did,
        displayName: info.displayName,
        capabilities: info.capabilities,
        workspace: info.workspace,
        proof: info.proof
      }
    }, did);

    // Send current agent list to new joiner
    const agentList = Array.from(this.agents.entries())
      .filter(([d]) => d !== did)
      .map(([d, a]) => ({
        did: a.did,
        displayName: a.displayName,
        capabilities: a.capabilities,
        workspace: a.workspace,
        proof: a.proof
      }));

    ws.send(JSON.stringify({
      type: 'room-state',
      protocol: 'adp-v1',
      agents: agentList,
      yourDID: did
    }));

    // Handle incoming messages
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(did, message);
      } catch (error) {
        console.error('Message parse error:', error);
      }
    };

    ws.onclose = () => {
      this.leave(did);
    };
  }

  private handleMessage(senderDID: string, message: any): void {
    switch (message.type) {
      case 'discover':
        this.handleDiscover(senderDID, message);
        break;
      case 'capability':
        this.handleCapability(senderDID, message);
        break;
      case 'session-request':
        this.handleSessionRequest(senderDID, message);
        break;
      case 'session-accept':
        this.handleSessionAccept(senderDID, message);
        break;
      case 'session-confirm':
        this.handleSessionConfirm(senderDID, message);
        break;
      case 'tool-share':
        this.handleToolShare(senderDID, message);
        break;
      case 'memory-grant':
        this.handleMemoryGrant(senderDID, message);
        break;
      case 'leave':
        this.leave(senderDID);
        break;
      default:
        console.warn('Unknown message type:', message.type);
    }
  }

  private handleDiscover(senderDID: string, message: any): void {
    // Send current agent list to requester
    const sender = this.agents.get(senderDID);
    if (sender) {
      this.sendToAgent(senderDID, {
        type: 'discovery-result',
        protocol: 'adp-v1',
        agents: Array.from(this.agents.entries())
          .filter(([d]) => d !== senderDID)
          .map(([d, a]) => ({
            did: a.did,
            displayName: a.displayName,
            capabilities: a.capabilities,
            workspace: a.workspace,
            proof: a.proof
          }))
      });
    }
  }

  private handleCapability(senderDID: string, message: any): void {
    const sender = this.agents.get(senderDID);
    if (sender) {
      sender.capabilities = message.payload?.capabilities || sender.capabilities;
      this.persist();
    }
  }

  private handleSessionRequest(senderDID: string, message: any): void {
    const targetDID = message.target || message.payload?.responder;
    const target = this.agents.get(targetDID);
    
    if (!target) {
      this.sendToAgent(senderDID, {
        type: 'session-reject',
        protocol: 'adp-v1',
        reason: 'Target agent not found in workspace'
      });
      return;
    }

    const sessionId = crypto.randomUUID();
    const session: Session = {
      sessionId,
      initiator: senderDID,
      responder: targetDID,
      sharedSecret: this.generateSharedSecret(),
      toolsGranted: message.payload?.tools || [],
      memoryGranted: message.payload?.memory || [],
      status: 'pending',
      createdAt: Date.now(),
      expiresAt: Date.now() + 3600000
    };

    this.sessions.set(sessionId, session);
    this.persist();

    // Forward to target
    this.sendToAgent(targetDID, {
      type: 'session-request',
      protocol: 'adp-v1',
      from: senderDID,
      sessionId,
      payload: {
        tools_needed: message.payload?.tools || [],
        memory_needed: message.payload?.memory || []
      }
    });
  }

  private handleSessionAccept(senderDID: string, message: any): void {
    const sessionId = message.sessionId;
    const session = this.sessions.get(sessionId);
    
    if (!session || session.responder !== senderDID) {
      return;
    }

    session.status = 'active';
    this.persist();

    // Notify initiator
    this.sendToAgent(session.initiator, {
      type: 'session-accept',
      protocol: 'adp-v1',
      sessionId,
      payload: {
        sharedSecret: session.sharedSecret,
        tools_offered: message.payload?.tools || session.toolsGranted
      }
    });
  }

  private handleSessionConfirm(senderDID: string, message: any): void {
    const sessionId = message.sessionId;
    const session = this.sessions.get(sessionId);
    
    if (session && session.initiator === senderDID) {
      session.status = 'active';
      this.persist();

      // Notify responder
      this.sendToAgent(session.responder, {
        type: 'session-confirm',
        protocol: 'adp-v1',
        sessionId
      });
    }
  }

  private handleToolShare(senderDID: string, message: any): void {
    // Forward tool grant to target agent
    const targetDID = message.target;
    this.sendToAgent(targetDID, {
      type: 'tool-grant',
      protocol: 'adp-v1',
      from: senderDID,
      payload: message.payload
    });
  }

  private handleMemoryGrant(senderDID: string, message: any): void {
    const targetDID = message.target;
    this.sendToAgent(targetDID, {
      type: 'memory-grant',
      protocol: 'adp-v1',
      from: senderDID,
      payload: message.payload
    });
  }

  private leave(did: string): void {
    const agent = this.agents.get(did);
    if (agent) {
      this.agents.delete(did);
      this.broadcast({
        type: 'agent-left',
        protocol: 'adp-v1',
        agent: { did, displayName: agent.displayName }
      }, did);
      
      // Clean up sessions involving this agent
      for (const [sessionId, session] of this.sessions) {
        if (session.initiator === did || session.responder === did) {
          session.status = 'revoked';
        }
      }
      this.persist();
    }
  }

  private sendToAgent(did: string, message: any): void {
    const agent = this.agents.get(did);
    if (agent && agent.ws.readyState === WebSocket.OPEN) {
      agent.ws.send(JSON.stringify(message));
    } else {
      // Queue for when agent reconnects
      const queue = this.messageQueue.get(did) || [];
      queue.push(message);
      this.messageQueue.set(did, queue);
    }
  }

  private broadcast(message: any, excludeDID?: string): void {
    for (const [did, agent] of this.agents) {
      if (did !== excludeDID && agent.ws.readyState === WebSocket.OPEN) {
        agent.ws.send(JSON.stringify(message));
      }
    }
  }

  private async persist(): Promise<void> {
    await this.state.storage.put('room-state', {
      agents: Object.fromEntries(this.agents),
      sessions: Object.fromEntries(this.sessions)
    });
  }

  private generateSharedSecret(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array).map(b => b.toString(16).padStart(2, '0')).join('');
  }
}