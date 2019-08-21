const express = require('express');
const app = express();
const port = 3000;

const request = require('request');
const JSDOM = require('jsdom').JSDOM;
const createDOMPurify = require('dompurify');
const Readability = require('readability');

app.use(express.urlencoded());

app.get('/', (req, res) => {
	res.send('POST a URL to urlencoded \'url\' to parse.');
});

const requestCallback = (url, res) => (error, response, body) => {
	if (!error && response.statusCode == 200) {
		console.log('Response OK.');

		const doc = new JSDOM('', {url: url});
		const DOMPurify = createDOMPurify(doc.window);
		const clean = DOMPurify.sanitize(body);
		const cleanDoc = new JSDOM(clean, {url: url});
		const reader = new Readability(cleanDoc.window.document);
		const article = reader.parse();

		res.send(article);
	} else {
		console.log('Response error:', error ? error.toString() : response.statusCode);
		res.sendStatus(response ? response.statusCode : 404);
	}
};

app.post('/', (req, res) => {
	const url = req.body.url;
	const requestOptions = {
		url: url,
		headers: {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'},
	};

	console.log('Parse request for:', url);

	request(requestOptions, requestCallback(url, res));
});

app.listen(port, () => {
	console.log(`Example app listening on port ${port}!`);
});
