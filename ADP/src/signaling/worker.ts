// ADP Signaling Worker - Cloudflare Worker entry point
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { websocket } from 'hono/websocket';
import { Room } from './Room';

const app = new Hono<{ Bindings: Env }>();

app.use('*', cors());

// Health check
app.get('/health', (c) => c.json({ status: 'ok', service: 'adp-signaling', version: '0.1.0' }));

// WebSocket endpoint for ADP signaling
app.get('/ws', websocket(), async (c) => {
  const ws = c.get('websocket');
  const roomId = c.req.query('room') || 'default';
  const agentDID = c.req.query('did');
  
  if (!agentDID) {
    ws.close(4001, 'DID required');
    return;
  }

  const room = c.env.ADP_ROOM.idFromName(roomId);
  const stub = c.env.ADP_ROOM.get(room);
  
  await stub.join(agentDID, ws);
});

export default app;
export { Room } from './Room';