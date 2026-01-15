const express = require('express');
const app = express();
const port = 8002;

app.use(express.json());

// Health endpoint
app.get('/health', (req, res) => {
    console.log('ShadowSearch: Health endpoint');
    res.json({
        status: 'healthy',
        service: 'ShadowSearch',
        port: port,
        endpoint: 'health',
        timestamp: new Date().toISOString()
    });
});

// AI Search endpoint
app.get('/api/ai/search', (req, res) => {
    console.log('ShadowSearch: AI Search endpoint');
    const query = req.query.q || '';
    res.json({
        status: 'searching',
        service: 'ShadowSearch AI',
        endpoint: '/api/ai/search',
        query: query,
        version: '2.0.0',
        model: 'semantic-search-v3',
        timestamp: new Date().toISOString(),
        results: query ? [
            { id: 1, relevance: 0.95, title: `Result for: ${query}` }
        ] : [],
        note: 'This is the AI Search endpoint'
    });
});

// Search endpoint
app.post('/search', (req, res) => {
    console.log('ShadowSearch: Search endpoint', req.body);
    res.json({
        status: 'search_complete',
        endpoint: '/search',
        data: req.body,
        timestamp: new Date().toISOString(),
        note: 'This is the Search endpoint'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not found',
        url: req.url,
        service: 'ShadowSearch'
    });
});

app.listen(port, '127.0.0.1', '127.0.0.1', '0.0.0.0', () => {
    console.log(`ShadowSearch Express server on port ${port}`);
});
