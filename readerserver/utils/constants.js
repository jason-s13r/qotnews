const googleBotUserAgent = 'Googlebot/2.1 (+http://www.google.com/bot.html)';
const googleBotIp = '66.249.66.1';

module.exports.googleBot = {
	userAgent: googleBotUserAgent,
	ip: googleBotIp,
	headers: {
		'User-Agent': googleBotUserAgent,
		'X-Forwarded-For': googleBotIp,
	}
}