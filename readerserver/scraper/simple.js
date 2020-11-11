const fetch = require('node-fetch');
const { JSDOM } = require('jsdom');
const { Readability } = require('@mozilla/readability');

const { getUserAgent } = require('../utils/user-agent');

const extract = (url, body) => {
	const doc = new JSDOM(body, { url: url });
	const reader = new Readability(doc.window.document);
	return reader.parse();
};

module.exports.scrape = async (req, res) => {
	try {
		const { userAgent, headers } = getUserAgent(req.body.url);
		const response = await fetch(req.body.url, {
			headers: {
				...headers,
				'User-Agent': userAgent
			}
		});
		if (!response.ok) {
			return res.sendStatus(response.statusCode);
		}
		const html = await response.text();
		const article = await extract(req.body.url, html);
		if (article && article.content) {
			return res.send(article.content);
		}
		return res.sendStatus(404);
	} catch (e) {
		console.error(e);
		return res.sendStatus(500);
	}
};

module.exports.details = async (req, res) => {
	try {
		const { userAgent, headers } = getUserAgent(req.body.url);
		const response = await fetch(req.body.url, {
			headers: {
				...headers,
				'User-Agent': userAgent
			}
		});
		if (!response.ok) {
			return res.sendStatus(response.statusCode);
		}
		const html = await response.text();
		const article = await extract(req.body.url, html);
		if (article) {
			return res.send(article);
		}
		return res.sendStatus(404);
	} catch (e) {
		console.error(e);
		return res.sendStatus(500);
	}
};