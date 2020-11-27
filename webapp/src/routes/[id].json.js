import fetch from 'node-fetch';

export async function get(req, res) {
	const response = await fetch(`http://localhost:33842/api/${req.params.id}`);
	res.writeHead(200, {
		'Content-Type': 'application/json'
	});
	res.end(await response.text());
}