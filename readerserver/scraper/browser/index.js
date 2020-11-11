const { getDetails } = require('./_browser');
const { getComments } = require('./_comments');

module.exports.scrape = async (req, res) => {
	try {
		const article = await getDetails(req.body.url);
		if (!article || !article.content) {
			throw new Error('failed to get details.');
		}
		return res.send(article.content);
	} catch (e) {
		return res.sendStatus(500);
	}
};

module.exports.details = async (req, res) => {
	try {
		const article = await getDetails(req.body.url);
		if (!article) {
			throw new Error('failed to get details.');
		}
		return res.send(article);
	} catch (e) {
		console.log(e);
		return res.sendStatus(500);
	}
};

module.exports.comments = async (req, res) => {
	try {
		const comments = await getComments(req.body.url);
		if (!comments) {
			throw new Error('failed to get comments.');
		}
		return res.send(comments);
	} catch (e) {
		console.log(e);
		return res.sendStatus(500);
	}
};