const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

// Serve static files from public directory
app.use(express.static('public'));

// Configure proxy middleware
const proxyOptions = {
    target: 'http://localhost:5005',
    changeOrigin: true,
    pathRewrite: { '^/api': '' },
    onError: (err, req, res) => {
        console.error('Proxy Error:', err);
        res.status(500).json({ error: 'Proxy error occurred' });
    },
    logLevel: 'error'
};

// Apply proxy to /api routes
app.use('/api', createProxyMiddleware(proxyOptions));

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something broke!' });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
    console.log(`Proxying /api requests to http://localhost:5005`);
});
