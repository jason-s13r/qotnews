import FormData from 'form-data';
import fetch from 'isomorphic-fetch';
import redirect from '@polka/redirect';

import sources from '../sources.json';

const key = Object.keys(sources).find(k => sources[k].enabled && sources[k].primary);

async function submit(opts, res) {
	const body = new FormData();
	body.append('url', opts.url);
	const response = await fetch(`${sources[key].url}/api/submit`, { method: "POST", body });
	if (opts.redirect) {
		const { nid } = await response.json();
		return redirect(res, 302, `/${key}/${nid}`);
	}
	res.writeHead(response.status, { 'Content-Type': response.headers.get('Content-Type') });
	res.end(await response.text());
}

export const get = async (req, res) => await submit(req.query, res);
export const post = async (req, res) => await submit(req.body, res);