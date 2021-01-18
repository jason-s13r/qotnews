import fetch from 'isomorphic-fetch';

import { purifyArray } from './_purify';
import { keyStories, keyStory } from './_key';
import sources from '../sources.json';

export async function get(req, res) {
	const { skip, limit } = {
		skip: req.query.skip || 0,
		limit: req.query.limit || 20,
	};
	let results = [];
	for (const key in sources) {
		const source = sources[key];
		if (!source.enabled) {
			continue;
		}
		const response = await fetch(`${source.url}/api/search?q=${req.query.q}&skip=${skip}&limit=${limit}`);
		if (!response.ok) {
			continue;
		}

		const data = await response.json();
		data.results.sort((a, b) => b.date - a.date);
		if (!source.paging) {
			data.results = data.results.slice(skip, limit);
		}
		results = results.concat(keyStories(data.results, key));
	}

	results.sort((a, b) => b.date - a.date);
	results = purifyArray(results);
	res.writeHead(200, { 'Content-Type': 'application/json' });
	res.end(JSON.stringify({ results }));
}

// export async function get(req, res) {
// 	const { skip, limit } = {
// 		skip: req.query.skip || 0,
// 		limit: req.query.limit || 20,
// 	};
// 	const response = await fetch(`${API_URL}/api/search?q=${req.query.q}&skip=${skip}&limit=${limit}`);
// 	res.writeHead(response.status, { 'Content-Type': response.headers.get('Content-Type') });
// 	if (!response.ok) {
// 		return res.end(await response.text());
// 	}
// 	const data = await response.json();
// 	data.results = purifyArray(data.results);
// 	res.end(JSON.stringify(data));
// }