import fetch from 'isomorphic-fetch';

import { keyStories, keyStory } from '../_key';
import { purify, purifyArray } from '../_purify';
import { samesite } from '../_samesite';

import sources from '../../sources.json';

export async function get(req, res) {
	const key = req.params.key;
	const id = req.params.id;
	const source = sources[key];
	if (!source) {
		res.writeHead(404);
		return res.end();
	}
	const response = await fetch(`${source.url}/api/${id}`);
	console.log(response.status, response.statusText, `${source.url}/api/${id}`);
	res.writeHead(response.status, { 'Content-Type': response.headers.get('Content-Type') });
	if (!response.ok) {
		return res.end(await response.text());
	}
	const data = await response.json();
	data.story = keyStory(data.story, key);
	data.related = keyStories(data.related, key);
	data.links = keyStories(data.links, key);
	data.story = purify(data.story);
	data.story = samesite(data.story, data.links);
	data.related = purifyArray(data.related);
	res.end(JSON.stringify(data));
}