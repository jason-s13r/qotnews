import fetch from 'isomorphic-fetch';

import { purifyArray } from './_purify';

const API_URL = process.env.API_URL || 'http://localhost:33842';

export async function get(req, res) {
	const { skip, limit } = {
		skip: req.query.skip || 0,
		limit: req.query.limit || 20,
	};
	const response = await fetch(`${API_URL}/api/search?q=${req.query.q}&skip=${skip}&limit=${limit}`);
	res.writeHead(response.status, { 'Content-Type': response.headers.get('Content-Type') });
	if (!response.ok) {
		return res.end(await response.text());
	}
	const data = await response.json();
	data.results = purifyArray(data.results);
	res.end(JSON.stringify(data));
}