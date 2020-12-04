import FormData from 'form-data';
import fetch from 'isomorphic-fetch';
import redirect from '@polka/redirect';

const API_URL = process.env.API_URL || 'http://localhost:33842';

export async function post(req, res) {
	const body = new FormData();
	body.append('url', req.body.url);
	const response = await fetch(`${API_URL}/api/submit`, { method: "POST", body });
	if (req.body.redirect) {
		const { nid } = await response.json();
		return redirect(res, 302, `/${nid}`);
	}
	res.writeHead(response.status, { 'Content-Type': response.headers.get('Content-Type') });
	res.end(await response.text());
}