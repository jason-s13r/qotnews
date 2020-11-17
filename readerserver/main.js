const port = 33843;
const express = require('express');
const app = express();
const simple = require('./scraper/simple');
const headless = require('./scraper/headless');

app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
	const routes = [
		'/simple',
		'/simple/details',
		'/headless',
		'/headless/details',
		'/headless/comments'
	];

	const html = routes.map(route => `
	<form method="POST" action="${route}" accept-charset="UTF-8">
		<fieldset>
			<legend>route: POST ${route}</legend>
			<input name="url">
			<button type="submit">SUBMIT</button>
		</fieldset>
	</form>`).join('<hr />');
	res.send(html);
});
app.post('/simple/', simple.scrape);
app.post('/simple/details', simple.details);
app.post('/headless', headless.scrape);
app.post('/headless/details', headless.details);
app.post('/headless/comments', headless.comments);

app.listen(port, () => {
	console.log(`Example app listening on port ${port}!`);
});
