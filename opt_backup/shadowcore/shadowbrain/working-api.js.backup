const express = require('express');
const http = require('http');

const app = express();
const port = 8001;

app.use(express.json());

// Simple health endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'ShadowBrain Working API',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        integrations: {
            shadowsearch: 'http://localhost:8005',
            status: 'connected'
        }
    });
});

// Process endpoint that works with ShadowSearch
app.post('/api/process', async (req, res) => {
    try {
        const { type, value, metadata = {} } = req.body;
        
        if (!type || !value) {
            return res.status(400).json({ error: 'Type and value are required' });
        }
        
        console.log(`Processing ${type}: ${value}`);
        
        // Call ShadowSearch for intelligence
        let shadowsearchData = {};
        try {
            const response = await new Promise((resolve, reject) => {
                const options = {
                    hostname: 'localhost',
                    port: 8005,
                    path: '/intelligence/analyze',
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                };
                
                const req = http.request(options, (res) => {
                    let data = '';
                    res.on('data', (chunk) => data += chunk);
                    res.on('end', () => resolve(JSON.parse(data)));
                });
                
                req.on('error', reject);
                req.write(JSON.stringify({
                    content: `${type}: ${value}`,
                    context: { 
                        entity_type: type,
                        source: 'shadowbrain',
                        metadata: metadata
                    }
                }));
                req.end();
            });
            
            shadowsearchData = response;
        } catch (error) {
            console.log('ShadowSearch integration error:', error.message);
            shadowsearchData = { error: error.message };
        }
        
        // Create response
        const result = {
            id: `entity_${Date.now()}`,
            type: type,
            value: value,
            confidence: 0.8,
            metadata: {
                ...metadata,
                processed_at: new Date().toISOString(),
                source: 'shadowbrain-api'
            },
            intelligence: shadowsearchData,
            integrations: {
                shadowsearch: shadowsearchData.error ? 'failed' : 'success',
                timestamp: new Date().toISOString()
            },
            vectorId: `vec_${Date.now()}`,
            graphId: `node_${Date.now()}`
        };
        
        res.json({
            success: true,
            message: 'Entity processed successfully',
            entity: result
        });
        
    } catch (error) {
        console.error('API error:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

// Start server
app.listen(port, '127.0.0.1', '127.0.0.1', () => {
    console.log('='.repeat(60));
    console.log(`🚀 ShadowBrain Working API on port ${port}`);
    console.log('='.repeat(60));
    console.log('\n📋 Endpoints:');
    console.log(`  • Health:  http://localhost:${port}/health`);
    console.log(`  • Process: POST http://localhost:${port}/api/process`);
    console.log('\n🔗 Connected to:');
    console.log(`  • ShadowSearch: http://localhost:8005`);
    console.log('='.repeat(60));
});

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down ShadowBrain API...');
    process.exit(0);
});
