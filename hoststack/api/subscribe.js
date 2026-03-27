// Vercel serverless function — api/subscribe.js
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { email, product, tags } = req.body;
  if (!email) return res.status(400).json({ error: 'Email required' });

  const BEEHIIV_KEY = process.env.BEEHIIV_API_KEY;
  const PUB_ID = process.env.BEEHIIV_PUB_ID;

  const response = await fetch(`https://api.beehiiv.com/v2/publications/${PUB_ID}/subscriptions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${BEEHIIV_KEY}` },
    body: JSON.stringify({
      email,
      reactivate_existing: true,
      send_welcome_email: true,
      tags: tags || [product, 'waitlist'],
      custom_fields: [{ id: process.env.BEEHIIV_PRODUCT_FIELD_ID, value: product }],
      utm_source: product?.toLowerCase().replace(/ /g, '-'),
      utm_medium: 'waitlist',
      utm_campaign: 'coming-soon'
    })
  });

  const data = await response.json();
  if (response.ok) {
    return res.status(200).json({ success: true });
  } else {
    return res.status(400).json({ error: data });
  }
}
