const port = 33843;
const express = require('express');
const app = express();
const simple = require('./scraper/simple');

app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
	// const routes = ['/', '/details', '/browser', '/browser/details', '/browser/comments'];
	const routes = ['/', '/details'];

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
app.post('/', simple.scrape);
app.post('/details', simple.details);
// app.post('/browser', browser.scrape);
// app.post('/browser/details', browser.details);
// app.post('/browser/comments', browser.comments);

app.listen(port, () => {
	console.log(`Example app listening on port ${port}!`);
});
