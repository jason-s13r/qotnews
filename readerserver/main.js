const express = require('express');
const app = express();
const port = 33843;

const request = require('request');
const JSDOM = require('jsdom').JSDOM;
const { Readability } = require('readability');

app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
	res.send('<form method="POST" accept-charset="UTF-8"><input name="url"><button type="submit">SUBMIT</button></form>');
});

const requestCallback = (url, res) => (error, response, body) => {
	if (!error && response.statusCode == 200) {
		console.log('Response OK.');

		const doc = new JSDOM(body, {url: url});
		const reader = new Readability(doc.window.document);
		const article = reader.parse();

		if (article && article.content) {
			res.send(article.content);
		} else {
			res.sendStatus(404);
		}
	} else {
		console.log('Response error:', error ? error.toString() : response.statusCode);
		res.sendStatus(response ? response.statusCode : 404);
	}
};

app.post('/', (req, res) => {
	const url = req.body.url;
	const requestOptions = {
		url: url,
		//headers: {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'},
		//headers: {'User-Agent': 'Twitterbot/1.0'},
		headers: {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
			'X-Forwarded-For': '66.249.66.1',
		},
	};

	console.log('Parse request for:', url);

	request(requestOptions, requestCallback(url, res));
});

app.listen(port, () => {
	console.log(`Example app listening on port ${port}!`);
});
