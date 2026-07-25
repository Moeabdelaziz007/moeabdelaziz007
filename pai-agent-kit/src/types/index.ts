export interface AgentConfig {
  id: string;
  name: string;
  version: string;
  description: string;
  instructions: string;
  tools: Tool[];
  memory: MemoryConfig;
  models: ModelConfig;
  mcp?: MCPConfig[];
  adp?: ADPConfig;
}

export interface MemoryConfig {
  enabled: boolean;
  maxTokens: number;
  layers: MemoryLayer[];
}

export type MemoryLayer = 'short' | 'long' | 'semantic' | 'episodic' | 'procedural' | 'working' | 'archival';

export interface ModelConfig {
  default: string;
  fallback: string;
  reasoning?: string;
  coding?: string;
  vision?: string;
}

export interface Tool {
  name: string;
  description: string;
  parameters: JSONSchema;
  execute: (args: any, context: ExecutionContext) => Promise<ToolResult>;
}

export interface JSONSchema {
  type: 'object';
  properties: Record<string, JSONSchemaProperty>;
  required?: string[];
  additionalProperties?: boolean;
}

export interface JSONSchemaProperty {
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  description?: string;
  enum?: string[];
  items?: JSONSchemaProperty;
  properties?: Record<string, JSONSchemaProperty>;
}

export interface ToolResult {
  success: boolean;
  data?: any;
  error?: string;
  metadata?: Record<string, any>;
}

export interface ExecutionContext {
  agentId: string;
  sessionId?: string;
  userId?: string;
  intention?: string;
  traceId?: string;
}

export interface MCPConfig {
  name: string;
  transport: 'stdio' | 'http' | 'sse' | 'websocket';
  command?: string;
  args?: string[];
  url?: string;
  headers?: Record<string, string>;
  tools: MCPTool[];
}

export interface MCPTool {
  name: string;
  description: string;
  parameters: JSONSchema;
}

export interface ADPConfig {
  workspaceDID: string;
  signalingServer: string;
  enableMDNS: boolean;
  capabilities: string[];
}

export interface AgentState {
  id: string;
  config: AgentConfig;
  createdAt: number;
  updatedAt: number;
  memory: MemoryState;
  tools: Tool[];
  sessions: Session[];
  mcpServers: MCPConfig[];
  trustChainRoot: string;
}

export interface MemoryState {
  short: MemoryEntry[];
  long: MemoryEntry[];
  semantic: MemoryEntry[];
  episodic: MemoryEntry[];
  procedural: MemoryEntry[];
  working: MemoryEntry[];
  archival: MemoryEntry[];
}

export interface MemoryEntry {
  id: string;
  layer: MemoryLayer;
  content: string;
  embedding?: number[];
  metadata: MemoryMetadata;
  createdAt: number;
  accessedAt: number;
  accessCount: number;
}

export interface MemoryMetadata {
  tags: string[];
  source: string;
  intention?: string;
  sessionId?: string;
  confidence: number;
  ttl?: number;
}

export interface Session {
  id: string;
  agentId: string;
  userId?: string;
  status: 'active' | 'completed' | 'failed' | 'archived';
  createdAt: number;
  updatedAt: number;
  endedAt?: number;
  summary?: string;
  metadata: Record<string, any>;
  traceId: string;
}

export interface SessionMessage {
  id: string;
  sessionId: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  toolCalls?: ToolCall[];
  toolResult?: ToolResult;
  timestamp: number;
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: any;
}

export interface TrustChainEntry {
  id: string;
  agentId: string;
  sessionId?: string;
  action: string;
  intention?: string;
  input: any;
  output: any;
  hash: string;
  previousHash: string;
  timestamp: number;
  signature: string;
}

export interface ADPMessage {
  type: 'join' | 'leave' | 'discover' | 'capability' | 'session-request' | 'session-accept' | 'tool-share' | 'memory-grant';
  protocol: 'adp-v1';
  agent: {
    did: string;
    displayName: string;
    capabilities: {
      mcpTools: string[];
      skills: string[];
      models: string[];
    };
    workspace: string;
    proof: string;
  };
  payload?: any;
}

export interface ADPSession {
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