const { googleBot } = require('./constants');
const { matchUrlDomain, useGoogleBotSites } = require("./sites");

module.exports.getUserAgent = (url) => {
	const useGoogleBot = useGoogleBotSites.some(function (item) {
		return typeof item === "string" && matchUrlDomain(item, url);
	});

	if (!useGoogleBot) {
		return {};
	}
	return {
		userAgent: googleBot.userAgent,
		headers: {
			"X-Forwarded-For": googleBot.ip
		}
	}
};