import fetch from 'isomorphic-fetch';

import { purify, purifyArray } from './_purify';
import { samesite } from './_samesite';

const API_URL = process.env.API_URL || 'http://localhost:33842';

export async function get(req, res) {
	const response = await fetch(`${API_URL}/api/${req.params.id}`);
	res.writeHead(response.status, { 'Content-Type': response.headers.get('Content-Type') });
	if (!response.ok) {
		return res.end(await response.text());
	}
	const data = await response.json();
	data.story = purify(data.story);
	data.story = samesite(data.story, data.links);
	data.related = purifyArray(data.related);
	res.end(JSON.stringify(data));
}
