import { vi } from 'vitest';

// Global test setup
vi.setConfig({
  testTimeout: 10000,
  hookTimeout: 5000
});

// Mock Cloudflare Workers environment
globalThis.Request = globalThis.Request || class Request {};
globalThis.Response = globalThis.Response || class Response {};
globalThis.Headers = globalThis.Headers || class Headers {};
globalThis.fetch = vi.fn();
globalThis.crypto = globalThis.crypto || {
  getRandomValues: (arr: Uint8Array) => {
    for (let i = 0; i < arr.length; i++) {
      arr[i] = Math.floor(Math.random() * 256);
    }
    return arr;
  },
  subtle: {
    digest: vi.fn(),
    sign: vi.fn(),
    importKey: vi.fn(),
  }
};
globalThis.WebSocket = globalThis.WebSocket || class WebSocket {
  readyState = 1;
  send = vi.fn();
  close = vi.fn();
  onmessage = null;
  onclose = null;
  onopen = null;
};

// Console suppression for clean test output
const originalConsole = { ...console };
beforeAll(() => {
  console.log = vi.fn();
  console.warn = vi.fn();
  console.error = vi.fn();
});
afterAll(() => {
  Object.assign(console, originalConsole);
});

// Clean up mocks between tests
afterEach(() => {
  vi.clearAllMocks();
});