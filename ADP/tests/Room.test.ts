import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Room } from '../src/signaling/Room';

describe('ADP Room', () => {
  let room: Room;
  let mockState: any;
  let mockEnv: any;
  let mockStorage: any;

  beforeEach(() => {
    vi.clearAllMocks();

    mockStorage = {
      get: vi.fn().mockResolvedValue(null),
      put: vi.fn().mockResolvedValue(undefined),
      delete: vi.fn().mockResolvedValue(undefined),
    };

    mockState = {
      storage: mockStorage,
      blockConcurrencyWhile: vi.fn((fn) => fn()),
      id: { toString: () => 'test-room-id' },
    };

    mockEnv = {
      ADP_ROOM: {
        idFromName: vi.fn().mockReturnValue({ toString: () => 'do-id' }),
        get: vi.fn().mockReturnValue({
          join: vi.fn(),
        }),
      },
      DB: {
        prepare: vi.fn().mockReturnValue({
          bind: vi.fn().mockReturnValue({
            run: vi.fn().mockResolvedValue({ success: true }),
            first: vi.fn().mockResolvedValue(null),
            all: vi.fn().mockResolvedValue({ results: [] }),
          }),
        }),
      },
      SESSIONS: {
        get: vi.fn().mockResolvedValue(null),
        put: vi.fn().mockResolvedValue(undefined),
        delete: vi.fn().mockResolvedValue(undefined),
      },
      AI: {
        run: vi.fn().mockResolvedValue({ data: [[0.1, 0.2, 0.3]] }),
      },
    };

    room = new Room(mockState, mockEnv);
  });

  describe('Agent Join', () => {
    it('should allow agent to join room', async () => {
      const mockWs = {
        send: vi.fn(),
        close: vi.fn(),
        readyState: 1,
        onmessage: null,
        onclose: null,
      };

      await room.join('did:axiom:z6Mk...', mockWs, {
        displayName: 'test-agent',
        capabilities: { mcpTools: ['test'], skills: ['test-skill'], models: ['hermes-3'] },
        workspace: 'test-workspace'
      });

      expect(room['agents'].has('did:axiom:z6Mk...')).toBe(true);
      expect(mockWs.send).toHaveBeenCalled();
    });

    it('should broadcast agent-joined to other agents', async () => {
      const mockWs1 = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };
      const mockWs2 = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };

      await room.join('did:axiom:agent1', mockWs1);
      await room.join('did:axiom:agent2', mockWs2);

      // agent2 should receive agent1's join notification
      expect(mockWs2.send).toHaveBeenCalledWith(expect.stringContaining('agent-joined'));
    });
  });

  describe('Agent Leave', () => {
    it('should remove agent and broadcast leave', async () => {
      const mockWs = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };

      await room.join('did:axiom:test', mockWs);
      room.leave('did:axiom:test');

      expect(room['agents'].has('did:axiom:test')).toBe(false);
    });
  });

  describe('Session Negotiation', () => {
    it('should create session request', async () => {
      const mockWs1 = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };
      const mockWs2 = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };

      await room.join('did:axiom:initiator', mockWs1);
      await room.join('did:axiom:responder', mockWs2);

      // Simulate session request from initiator
      const sessionRequest = {
        type: 'session-request',
        target: 'did:axiom:responder',
        payload: { tools: ['identity.verify'] }
      };

      // Get the onmessage handler for agent1
      const handler1 = mockWs1.onmessage;
      await handler1({ data: JSON.stringify(sessionRequest) });

      // Responder should receive session request
      expect(mockWs2.send).toHaveBeenCalledWith(expect.stringContaining('session-request'));
    });

    it('should complete session handshake', async () => {
      const mockWs1 = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };
      const mockWs2 = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };

      await room.join('did:axiom:initiator', mockWs1);
      await room.join('did:axiom:responder', mockWs2);

      const sessionRequest = {
        type: 'session-request',
        target: 'did:axiom:responder',
        payload: { tools: ['identity.verify'] }
      };

      const handler1 = mockWs1.onmessage;
      await handler1({ data: JSON.stringify(sessionRequest) });

      const handler2 = mockWs2.onmessage;
      // Find the session request call
      const sessionCall = mockWs2.send.mock.calls.find(call => 
        call[0].includes('session-request')
      );
      const sessionId = JSON.parse(sessionCall[0]).sessionId;

      // Responder accepts
      const acceptMsg = { type: 'session-accept', sessionId };
      await handler2({ data: JSON.stringify(acceptMsg) });

      // Initiator should receive accept
      expect(mockWs1.send).toHaveBeenCalledWith(expect.stringContaining('session-accept'));
    });
  });

  describe('Capability Broadcast', () => {
    it('should broadcast capabilities on join', async () => {
      const mockWs = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };

      await room.join('did:axiom:test', mockWs, {
        capabilities: { mcpTools: ['tool1'], skills: ['skill1'], models: ['model1'] }
      });

      // Should have sent capability broadcast
      expect(mockWs.send).toHaveBeenCalled();
    });
  });

  describe('Message Routing', () => {
    it('should route direct messages to target agent', async () => {
      const mockWs1 = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };
      const mockWs2 = { send: vi.fn(), readyState: 1, onmessage: null, onclose: null, close: vi.fn() };

      await room.join('did:axiom:agent1', mockWs1);
      await room.join('did:axiom:agent2', mockWs2);

      // Simulate tool-share from agent1 to agent2
      const toolShare = {
        type: 'tool-share',
        target: 'did:axiom:agent2',
        payload: { tool: 'test.tool', auth: 'token' }
      };

      const handler1 = mockWs1.onmessage;
      await handler1({ data: JSON.stringify(toolShare) });

      expect(mockWs2.send).toHaveBeenCalledWith(expect.stringContaining('tool-grant'));
    });
  });
});