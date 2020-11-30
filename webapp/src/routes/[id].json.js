import fetch from 'isomorphic-fetch';

// const API_URL = process.env.API_URL || 'http://news.1j.nz';
const API_URL = process.env.API_URL || 'http://localhost:33842';

export async function get(req, res) {
	const response = await fetch(`${API_URL}/api/${req.params.id}`);
	res.writeHead(response.status, { 'Content-Type': 'application/json' });
	res.end(await response.text());
}