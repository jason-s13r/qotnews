import fetch from 'isomorphic-fetch';

import { purifyArray } from './_purify';
import { keyStories } from './_key';
import sources from '../sources.json';

export async function get(req, res) {
	const { skip, limit } = {
		skip: req.query.skip || 0,
		limit: req.query.limit || 20,
	};
	let stories = [];
	for (const key in sources) {
		const source = sources[key];
		if (!source.enabled) {
			continue;
		}
		const response = await fetch(`${source.url}/api?skip=${skip}&limit=${limit}`);
		if (!response.ok) {
			continue;
		}

		const data = await response.json();
		data.stories.sort((a, b) => b.date - a.date);
		if (!source.paging) {
			data.stories = data.stories.slice(skip, limit);
		}
		stories = stories.concat(keyStories(data.stories, key));
	}

	stories.sort((a, b) => b.date - a.date);
	stories = purifyArray(stories);
	res.writeHead(200, { 'Content-Type': 'application/json' });
	res.end(JSON.stringify({ stories }));
}

// export async function get(req, res) {
// 	const { skip, limit } = {
// 		skip: req.query.skip || 0,
// 		limit: req.query.limit || 20,
// 	};
// 	const response = await fetch(`${API_URL}/api?skip=${skip}&limit=${limit}`);
// 	res.writeHead(response.status, { 'Content-Type': response.headers.get('Content-Type') });
// 	if (!response.ok) {
// 		return res.end(await response.text());
// 	}
// 	const data = await response.json();
// 	data.stories = purifyArray(data.stories);
// 	res.end(JSON.stringify(data));
// }