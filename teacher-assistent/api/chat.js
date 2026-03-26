const https = require('https');

module.exports = function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { apiKey, ...payload } = req.body;

  if (!apiKey) {
    res.status(400).json({ error: 'Missing apiKey' });
    return;
  }

  const postData = JSON.stringify(payload);

  const options = {
    hostname: 'api.anthropic.com',
    path: '/v1/messages',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(postData),
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
  };

  const proxyReq = https.request(options, proxyRes => {
    let data = '';
    proxyRes.on('data', chunk => { data += chunk; });
    proxyRes.on('end', () => {
      res.status(proxyRes.statusCode).json(JSON.parse(data));
    });
  });

  proxyReq.on('error', err => {
    res.status(502).json({ error: err.message });
  });

  proxyReq.write(postData);
  proxyReq.end();
};
