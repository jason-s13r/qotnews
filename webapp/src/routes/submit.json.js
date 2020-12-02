import FormData from 'form-data';
import fetch from 'isomorphic-fetch';

const API_URL = process.env.API_URL || 'http://localhost:33842';

export async function post(req, res) {
	const data = new FormData();
	data.append('url', req.body.url);
	const response = await fetch(`${API_URL}/api/submit`, { method: "POST", body: data });
	res.writeHead(response.status, { 'Content-Type': 'application/json' });
	res.end(await response.text());
}