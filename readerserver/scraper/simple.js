const request = require('request');
const JSDOM = require('jsdom').JSDOM;
const { Readability } = require('readability');

const { headers } = require('../constants');

const options = url => ({
	url,
	headers,
});

const extract = (url, body) => {
	const doc = new JSDOM(body, { url: url });
	const reader = new Readability(doc.window.document);
	return reader.parse();
};


module.exports.scrape = (req, res) => request(options(req.body.url), (error, response, body) => {
	if (error || response.statusCode != 200) {
		console.log('Response error:', error ? error.toString() : response.statusCode);
		return res.sendStatus(response ? response.statusCode : 404);
	}
	const article = extract(req.body.url, body);
	if (article && article.content) {
		return res.send(article.content);
	}
	return res.sendStatus(404);
});

module.exports.details = (req, res) => request(options(req.body.url), (error, response, body) => {
	if (error || response.statusCode != 200) {
		console.log('Response error:', error ? error.toString() : response.statusCode);
		return res.sendStatus(response ? response.statusCode : 404);
	}
	const article = extract(req.body.url, body);
	if (article) {
		return res.send(article);
	}
	return res.sendStatus(404);
});