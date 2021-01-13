import FormData from 'form-data';
import fetch from 'isomorphic-fetch';
import redirect from '@polka/redirect';

import sources from '../sources.json';

const key = Object.keys(sources).find(k => sources[k].enabled && sources[k].primary);

export async function post(req, res) {
	const body = new FormData();
	body.append('url', req.body.url);
	const response = await fetch(`${sources[key].url}/api/submit`, { method: "POST", body });
	if (req.body.redirect) {
		const { nid } = await response.json();
		return redirect(res, 302, `/${key}-${nid}`);
	}
	res.writeHead(response.status, { 'Content-Type': response.headers.get('Content-Type') });
	res.end(await response.text());
}