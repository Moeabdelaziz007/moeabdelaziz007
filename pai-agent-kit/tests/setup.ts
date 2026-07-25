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
globalThis.caches = {
  default: {
    match: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
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