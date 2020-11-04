const port = 33843;
const express = require('express');
const app = express();
const simple = require('./simple');

app.use(express.urlencoded({ extended: true }));
app.get('/', (req, res) => res.send(simple.FORM));
app.post('/', (req, res) => simple.scrape(req, res));
app.post('/details', (req, res) => simple.details(req, res));
// app.post('/browser', (req, res) => browser.scrape(req, res));
// app.post('/browser/details', (req, res) => browser.details(req, res));

app.listen(port, () => {
	console.log(`Example app listening on port ${port}!`);
});
