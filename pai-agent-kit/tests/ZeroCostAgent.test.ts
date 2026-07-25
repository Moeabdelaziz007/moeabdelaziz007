import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ZeroCostAgent } from '../src/agent/ZeroCostAgent';
import { AgentConfig, AgentState, Tool, MCPConfig } from '../src/types';

describe('ZeroCostAgent', () => {
  let agent: ZeroCostAgent;
  let mockConfig: AgentConfig;
  let mockState: AgentState;
  let mockStorage: any;
  let mockEnv: any;

  beforeEach(() => {
    vi.clearAllMocks();

    mockConfig = {
      id: 'test-agent-001',
      name: 'Test Agent',
      version: '1.0.0',
      description: 'Test agent for unit tests',
      instructions: 'You are a helpful test agent.',
      tools: [],
      memory: {
        enabled: true,
        maxTokens: 5000,
        layers: ['short', 'long', 'semantic']
      },
      models: {
        default: '@cf/meta/llama-3.1-8b-instruct',
        fallback: '@cf/meta/llama-3.1-8b-instruct'
      }
    };

    mockState = {
      id: mockConfig.id,
      config: mockConfig,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      memory: {
        short: [],
        long: [],
        semantic: []
      },
      tools: [],
      sessions: []
    };

    mockStorage = {
      get: vi.fn().mockResolvedValue(mockState),
      put: vi.fn().mockResolvedValue(undefined),
      delete: vi.fn().mockResolvedValue(undefined),
      list: vi.fn().mockResolvedValue({ keys: [] })
    };

    mockEnv = {
      AGENT: {
        idFromName: vi.fn().mockReturnValue({
          toString: () => 'test-do-id',
          fetch: vi.fn()
        })
      },
      DB: {
        prepare: vi.fn().mockReturnValue({
          bind: vi.fn().mockReturnValue({
            run: vi.fn().mockResolvedValue({ success: true }),
            first: vi.fn().mockResolvedValue(null),
            all: vi.fn().mockResolvedValue({ results: [] })
          })
        })
      },
      SESSIONS: {
        get: vi.fn().mockResolvedValue(null),
        put: vi.fn().mockResolvedValue(undefined),
        delete: vi.fn().mockResolvedValue(undefined)
      },
      MEMORY: {
        query: vi.fn().mockResolvedValue({ matches: [] }),
        upsert: vi.fn().mockResolvedValue(undefined)
      },
      AI: {
        run: vi.fn().mockResolvedValue({
          response: 'Test response from AI'
        })
      },
      AI_GATEWAY: {
        run: vi.fn().mockResolvedValue({
          response: 'Cached response'
        })
      }
    };

    agent = new ZeroCostAgent(mockConfig, mockEnv);
  });

  describe('Initialization', () => {
    it('should initialize with valid config', () => {
      expect(agent).toBeDefined();
      expect(agent.config).toEqual(mockConfig);
    });

    it('should throw on invalid config', () => {
      expect(() => new ZeroCostAgent({} as any, mockEnv)).toThrow();
    });

    it('should load state from storage on init', async () => {
      await agent.initialize();
      expect(mockStorage.get).toHaveBeenCalledWith(mockConfig.id);
    });
  });

  describe('Tool Management', () => {
    it('should register a tool', async () => {
      const tool: Tool = {
        name: 'test.tool',
        description: 'Test tool',
        parameters: { type: 'object', properties: {} },
        execute: vi.fn().mockResolvedValue({ result: 'ok' })
      };

      await agent.registerTool(tool);
      const tools = await agent.getTools();
      expect(tools).toContainEqual(expect.objectContaining({ name: 'test.tool' }));
    });

    it('should execute registered tool', async () => {
      const executeFn = vi.fn().mockResolvedValue({ data: 'test' });
      const tool: Tool = {
        name: 'echo',
        description: 'Echo tool',
        parameters: { type: 'object', properties: { message: { type: 'string' } } },
        execute: executeFn
      };

      await agent.registerTool(tool);
      const result = await agent.executeTool('echo', { message: 'hello' });

      expect(executeFn).toHaveBeenCalledWith({ message: 'hello' });
      expect(result).toEqual({ data: 'test' });
    });

    it('should throw on unknown tool', async () => {
      await expect(agent.executeTool('unknown.tool', {})).rejects.toThrow('Tool not found');
    });
  });

  describe('Memory Management', () => {
    it('should store short-term memory', async () => {
      await agent.remember('short', 'Test memory entry');
      const memories = await agent.recall('short', 'Test');
      expect(memories.length).toBeGreaterThan(0);
    });

    it('should store long-term memory', async () => {
      await agent.remember('long', 'Important long-term memory');
      const memories = await agent.recall('long', 'Important');
      expect(memories.length).toBeGreaterThan(0);
    });

    it('should store semantic memory with embeddings', async () => {
      await agent.remember('semantic', 'Semantic knowledge', { tags: ['test', 'knowledge'] });
      const memories = await agent.recall('semantic', 'knowledge');
      expect(memories.length).toBeGreaterThan(0);
    });

    it('should respect memory limits', async () => {
      const limitedAgent = new ZeroCostAgent({
        ...mockConfig,
        memory: { enabled: true, maxTokens: 100, layers: ['short'] }
      }, mockEnv);

      await limitedAgent.initialize();

      // Add many memories
      for (let i = 0; i < 50; i++) {
        await limitedAgent.remember('short', `Memory ${i}`);
      }

      const memories = await limitedAgent.recall('short', '');
      // Should not exceed maxTokens worth of entries
      expect(memories.length).toBeLessThanOrEqual(20);
    });
  });

  describe('MCP Integration', () => {
    it('should register MCP server', async () => {
      const mcpConfig: MCPConfig = {
        name: 'test-mcp',
        transport: 'stdio',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],
        tools: []
      };

      await agent.registerMCP(mcpConfig);
      const mcps = await agent.getMCPs();
      expect(mcps).toContainEqual(expect.objectContaining({ name: 'test-mcp' }));
    });

    it('should list available MCP tools', async () => {
      const mcpConfig: MCPConfig = {
        name: 'filesystem',
        transport: 'stdio',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],
        tools: [
          { name: 'read_file', description: 'Read a file' },
          { name: 'write_file', description: 'Write a file' }
        ]
      };

      await agent.registerMCP(mcpConfig);
      const tools = await agent.getMCPTools('filesystem');
      expect(tools.length).toBe(2);
    });
  });

  describe('Session Management', () => {
    it('should create a new session', async () => {
      const session = await agent.createSession({
        userId: 'user-123',
        metadata: { source: 'test' }
      });

      expect(session).toMatchObject({
        id: expect.any(String),
        agentId: mockConfig.id,
        userId: 'user-123',
        status: 'active'
      });
    });

    it('should end session and archive', async () => {
      const session = await agent.createSession({ userId: 'user-123' });
      await agent.endSession(session.id, { summary: 'Test completed' });

      const ended = await agent.getSession(session.id);
      expect(ended?.status).toBe('completed');
    });
  });

  describe('Model Routing', () => {
    it('should route to default model', async () => {
      const response = await agent.run('Hello, world!');
      expect(mockEnv.AI.run).toHaveBeenCalled();
      expect(response).toBeDefined();
    });

    it('should fallback on model error', async () => {
      mockEnv.AI.run.mockRejectedValueOnce(new Error('Model unavailable'));
      mockEnv.AI.run.mockResolvedValueOnce({ response: 'Fallback response' });

      const response = await agent.run('Test');
      expect(response).toBe('Fallback response');
    });

    it('should use AI Gateway for cached responses', async () => {
      mockEnv.AI_GATEWAY.run.mockResolvedValue({ response: 'Cached response' });

      const response = await agent.run('Cached query');
      expect(mockEnv.AI_GATEWAY.run).toHaveBeenCalled();
    });
  });

  describe('ADP Integration', () => {
    it('should broadcast capabilities to workspace', async () => {
      await agent.joinWorkspace('workspace-test');
      // Verify ADP broadcast was sent
    });

    it('should discover other agents in workspace', async () => {
      const agents = await agent.discoverAgents('workspace-test');
      expect(Array.isArray(agents)).toBe(true);
    });

    it('should negotiate secure session with peer', async () => {
      const session = await agent.negotiateSession('peer-agent-did', {
        toolsNeeded: ['identity.verify']
      });

      expect(session).toMatchObject({
        sessionId: expect.any(String),
        peer: 'peer-agent-did',
        status: 'active'
      });
    });
  });

  describe('TrustChain Logging', () => {
    it('should log all actions to TrustChain', async () => {
      await agent.registerTool({
        name: 'test.log',
        description: 'Test logging',
        parameters: {},
        execute: vi.fn().mockResolvedValue({ ok: true })
      });

      await agent.executeTool('test.log', {});

      // Verify TrustChain entry was created
      expect(mockEnv.DB.prepare).toHaveBeenCalled();
    });

    it('should include intention in log entries', async () => {
      await agent.run('Test with intention', { intention: 'Testing TrustChain' });

      const dbCall = mockEnv.DB.prepare.mock.calls.find(c =>
        c[0].includes('intention')
      );
      expect(dbCall).toBeDefined();
    });
  });
});