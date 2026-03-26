#!/usr/bin/env node
// Simple local proxy server - serves the HTML and forwards API calls to Anthropic
// Run with: node server.js
// Then open: http://localhost:3000

const http  = require('http');
const https = require('https');
const fs    = require('fs');
const path  = require('path');

const PORT = 3000;

const MIME = {
  '.html': 'text/html',
  '.css':  'text/css',
  '.js':   'application/javascript',
  '.json': 'application/json',
};

const server = http.createServer((req, res) => {

  // ---- Proxy: POST /api/chat -> Anthropic API ----
  if (req.method === 'POST' && req.url === '/api/chat') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      let parsed;
      try { parsed = JSON.parse(body); } catch {
        res.writeHead(400); res.end('Bad JSON'); return;
      }

      const { apiKey, ...payload } = parsed;
      if (!apiKey) {
        res.writeHead(400); res.end(JSON.stringify({ error: 'Missing apiKey' })); return;
      }

      const postData = JSON.stringify(payload);
      const options = {
        hostname: 'api.anthropic.com',
        path:     '/v1/messages',
        method:   'POST',
        headers: {
          'Content-Type':      'application/json',
          'Content-Length':    Buffer.byteLength(postData),
          'x-api-key':         apiKey,
          'anthropic-version': '2023-06-01',
        }
      };

      const proxyReq = https.request(options, proxyRes => {
        let data = '';
        proxyRes.on('data', c => { data += c; });
        proxyRes.on('end', () => {
          res.writeHead(proxyRes.statusCode, { 'Content-Type': 'application/json' });
          res.end(data);
        });
      });

      proxyReq.on('error', err => {
        res.writeHead(502); res.end(JSON.stringify({ error: err.message }));
      });

      proxyReq.write(postData);
      proxyReq.end();
    });
    return;
  }

  // ---- Static file serving ----
  let filePath = req.url === '/' ? '/index.html' : req.url;
  filePath = path.join(__dirname, filePath);

  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    const ext  = path.extname(filePath);
    const type = MIME[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': type });
    res.end(data);
  });
});

server.listen(PORT, () => {
  console.log('Teacher Assistant running at http://localhost:' + PORT);
});
