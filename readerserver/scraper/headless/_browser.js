const { firefox } = require("playwright");
const { JSDOM } = require("jsdom");
const { Readability } = require("@mozilla/readability");

const { getUserAgent } = require('../../utils/user-agent');
const { blockedRegexes, matchUrlDomain } = require("../../utils/sites");

module.exports.getDetails = async (url) => {
	const { userAgent, headers } = getUserAgent(url);

	const browser = await firefox.launch({ args: [], headless: true });
	const tab = await browser.newPage({
		extraHTTPHeaders: headers,
		userAgent,
		viewport: { width: 2000, height: 10000 },
	});

	try {
		await tab.route(/.*/, (route) => {
			const routeUrl = route.request().url();
			const blockedDomains = Object.keys(blockedRegexes);
			const domain = matchUrlDomain(blockedDomains, routeUrl);
			if (domain && routeUrl.match(blockedRegexes[domain])) {
				return route.abort();
			}
			return route.continue();
		});
		await tab.addInitScript({ path: "scraper/headless/scripts/bypass-paywalls-chrome/src/js/contentScript.js" });
		await tab.addInitScript({ path: "scraper/headless/scripts/cosmetic-filters.js" });
		await tab.addInitScript({ path: "scraper/headless/scripts/fix-relative-links.js" });
		await tab.goto(url, { timeout: 60000, waitUntil: "domcontentloaded" });
		await tab.waitForTimeout(2000);

		const body = await tab.content();
		const doc = new JSDOM(body, { url });
		const reader = new Readability(doc.window.document);
		const article = reader.parse();
		return article;
	} catch (e) {
		throw e;
	} finally {
		await tab.close();
		await browser.close();
	}
};
