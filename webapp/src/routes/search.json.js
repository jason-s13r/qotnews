import fetch from 'isomorphic-fetch';

import { purifyArray } from './_purify';
import { keyStories } from './_key';
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