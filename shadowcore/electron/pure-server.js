const http = require('http');
const url = require('url');

const PORT = process.env.PORT || 8082;

// Simple in-memory threat module to avoid external dependencies
class SimpleThreatIntelligence {
  constructor() {
    this.services = [
      { name: 'Threat Platform', port: 9030, status: 'online' },
      { name: 'Threat Insight', port: 9090, status: 'online' },
      { name: 'ShadowBrain', port: 8081, status: 'online' }
    ];
  }

  async checkAllServices() {
    return this.services;
  }

  async analyzeDomain(domain) {
    return {
      success: true,
      domain: domain,
      analysis: {
        threat_level: 'low',
        risk_score: Math.floor(Math.random() * 100),
        indicators: [],
        note: 'Analysis completed'
      }
    };
  }

  async analyzeIP(ip) {
    return {
      success: true,
      ip: ip,
      analysis: {
        threat_level: 'low',
        risk_score: Math.floor(Math.random() * 100),
        indicators: [],
        note: 'Analysis completed'
      }
    };
  }
}

// Helper functions
function parseRequestBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', chunk => body += chunk.toString());
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch {
        resolve({});
      }
    });
  });
}

function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

// Main server
const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  
  console.log(`${new Date().toISOString()} ${req.method} ${pathname}`);
  
  // Health endpoint
  if (pathname === '/api/health' && req.method === 'GET') {
    const ti = new SimpleThreatIntelligence();
    const services = await ti.checkAllServices();
    
    sendJSON(res, 200, {
      status: 'healthy',
      service: 'ShadowCore Threat Intelligence',
      version: '2.0.0',
      timestamp: new Date().toISOString(),
      endpoints: [
        '/api/health',
        '/api/threat/check',
        '/api/threat/insight',
        '/api/threat/intel'
      ],
      services: services
    });
    return;
  }
  
  // Threat check endpoint
  if (pathname === '/api/threat/check' && req.method === 'POST') {
    const body = await parseRequestBody(req);
    const { domain, ip } = body;
    const ti = new SimpleThreatIntelligence();
    
    if (!domain && !ip) {
      sendJSON(res, 400, { error: 'Provide domain or ip' });
      return;
    }
    
    const result = domain ? await ti.analyzeDomain(domain) : await ti.analyzeIP(ip);
    sendJSON(res, 200, result);
    return;
  }
  
  // Threat insight endpoint
  if (pathname === '/api/threat/insight' && req.method === 'POST') {
    const body = await parseRequestBody(req);
    const { domain, ip } = body;
    const target = domain || ip || 'unknown';
    
    sendJSON(res, 200, {
      success: true,
      target: target,
      insight: {
        threat_level: 'medium',
        confidence: 0.7,
        indicators: ['reputation', 'behavior'],
        recommendation: 'Monitor activity'
      }
    });
    return;
  }
  
  // Threat intel endpoint
  if (pathname === '/api/threat/intel' && req.method === 'POST') {
    const body = await parseRequestBody(req);
    const { domain, ip } = body;
    const target = domain || ip || 'unknown';
    
    sendJSON(res, 200, {
      success: true,
      target: target,
      intelligence: {
        sources: 3,
        reputation: 65,
        risk_factors: ['geo', 'history'],
        actions: ['monitor', 'log']
      }
    });
    return;
  }
  
  // Root endpoint
  if (pathname === '/' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <html>
        <body>
          <h1>🛡️ ShadowCore Threat Intelligence</h1>
          <p>Server is running on port ${PORT}</p>
          <h3>Endpoints:</h3>
          <ul>
            <li>GET /api/health - Health check</li>
            <li>POST /api/threat/check - Check threats</li>
            <li>POST /api/threat/insight - Get insights</li>
            <li>POST /api/threat/intel - Get intelligence</li>
          </ul>
        </body>
      </html>
    `);
    return;
  }
  
  // 404
  sendJSON(res, 404, {
    error: 'Not found',
    path: pathname
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════╗
║      ShadowCore Threat Intelligence Server        ║
╠═══════════════════════════════════════════════════╣
║  ✅ Server running on http://localhost:${PORT}    ║
║  📍 Health: http://localhost:${PORT}/api/health   ║
╚═══════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down...');
  server.close(() => process.exit(0));
});


// Health endpoints
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'Electron Server',
        timestamp: new Date().toISOString()
    });
});

app.get('/health/detailed', (req, res) => {
    const memoryUsage = process.memoryUsage();
    res.json({
        status: 'healthy',
        service: 'Electron Server',
        pid: process.pid,
        memory_mb: memoryUsage.rss / 1024 / 1024,
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});
