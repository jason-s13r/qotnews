module.exports.blockedRegexes = {
	"adweek.com": /.+\.lightboxcdn\.com\/.+/,
	"afr.com": /afr\.com\/assets\/vendorsReactRedux_client.+\.js/,
	"businessinsider.com": /(.+\.tinypass\.com\/.+|cdn\.onesignal\.com\/sdks\/.+\.js)/,
	"chicagotribune.com": /.+:\/\/.+\.tribdss\.com\//,
	"economist.com": /(.+\.tinypass\.com\/.+|economist\.com\/engassets\/_next\/static\/chunks\/framework.+\.js)/,
	"editorialedomani.it": /(js\.pelcro\.com\/.+|editorialedomani.it\/pelcro\.js)/,
	"foreignpolicy.com": /.+\.tinypass\.com\/.+/,
	"fortune.com": /.+\.tinypass\.com\/.+/,
	"haaretz.co.il": /haaretz\.co\.il\/htz\/js\/inter\.js/,
	"haaretz.com": /haaretz\.com\/hdc\/web\/js\/minified\/header-scripts-int.js.+/,
	"inquirer.com": /.+\.tinypass\.com\/.+/,
	"lastampa.it": /.+\.repstatic\.it\/minify\/sites\/lastampa\/.+\/config\.cache\.php\?name=social_js/,
	"lrb.co.uk": /.+\.tinypass\.com\/.+/,
	"nzherald.co.nz": /(.+nzherald\.co\.nz\/.+\/subs\/p\.js|.+nzherald\.co\.nz\/.+\/react\.js|.+nzherald\.co\.nz\/.+\/appear\.js|.+nzherald\.co\.nz\/.+\/tracking\/.+|.+nzherald\.co\.nz\/.+\/default\.js|.+\/newsbarscript\.js)/,
	"medscape.com": /.+\.medscapestatic\.com\/.*medscape-library\.js/,
	"interest.co.nz": /(.+\.presspatron\.com.+|.+interest\.co\.nz.+pp-ablock-banner\.js)/,
	"repubblica.it": /scripts\.repubblica\.it\/pw\/pw\.js.+/,
	"spectator.co.uk": /.+\.tinypass\.com\/.+/,
	"spectator.com.au": /.+\.tinypass\.com\/.+/,
	"telegraph.co.uk": /.+telegraph\.co\.uk.+martech.+/,
	"thecourier.com.au": /.+cdn-au\.piano\.io\/api\/tinypass.+\.js/,
	"thenation.com": /thenation\.com\/.+\/paywall-script\.php/,
	"thenational.scot": /(.+\.tinypass\.com\/.+|.+thenational\.scot.+omniture\.js|.+thenational\.scot.+responsive-sync.+)/,
	"thewrap.com": /thewrap\.com\/.+\/wallkit\.js/,
	"wsj.com": /cdn\.ampproject\.org\/v\d\/amp-access-.+\.js/,
	"historyextra.com": /.+\.evolok\.net\/.+\/authorize\/.+/,
	"barrons.com": /cdn\.ampproject\.org\/v\d\/amp-access-.+\.js/,
	"irishtimes.com": /cdn\.ampproject\.org\/v\d\/amp-access-.+\.js/,
	"elmercurio.com": /(merreader\.emol\.cl\/assets\/js\/merPramV2.js|staticmer\.emol\.cl\/js\/inversiones\/PramModal.+\.js)/,
	"sloanreview.mit.edu": /(.+\.tinypass\.com\/.+|.+\.netdna-ssl\.com\/wp-content\/themes\/smr\/assets\/js\/libs\/welcome-ad\.js)/,
	"latercera.com": /.+\.cxense\.com\/+/,
	"lesechos.fr": /.+\.tinypass\.com\/.+/,
	"washingtonpost.com": /.+\.washingtonpost\.com\/.+\/pwapi-proxy\.min\.js/,
	"thehindu.com": /ajax\.cloudflare\.com\/cdn-cgi\/scripts\/.+\/cloudflare-static\/rocket-loader\.min\.js/,
	"technologyreview.com": /.+\.blueconic\.net\/.+/,
};

module.exports.useGoogleBotSites = [
	"adelaidenow.com.au",
	"barrons.com",
	"couriermail.com.au",
	"dailytelegraph.com.au",
	"fd.nl",
	"genomeweb.com",
	"haaretz.co.il",
	"haaretz.com",
	"heraldsun.com.au",
	"mexiconewsdaily.com",
	"ntnews.com.au",
	"quora.com",
	"seekingalpha.com",
	"telegraph.co.uk",
	"theaustralian.com.au",
	"themarker.com",
	"themercury.com.au",
	"thenational.scot",
	"thetimes.co.uk",
	"wsj.com",
	"kansascity.com",
	"republic.ru",
	"nzz.ch",
	"handelsblatt.com",
	"washingtonpost.com",
	"df.cl",
];

function matchDomain(domains, hostname) {
	let matchedDomain = false;
	if (typeof domains === "string") {
		domains = [domains];
	}
	domains.some(
		(domain) =>
			(hostname === domain || hostname.endsWith("." + domain)) &&
			(matchedDomain = domain)
	);
	return matchedDomain;
}

function matchUrlDomain(domains, url) {
	return matchDomain(domains, urlHost(url));
}

function urlHost(url) {
	if (url && url.startsWith("http")) {
		try {
			return new URL(url).hostname;
		} catch (e) {
			console.log(`url not valid: ${url} error: ${e}`);
		}
	}
	return url;
}

module.exports.matchDomain = matchDomain;
module.exports.matchUrlDomain = matchUrlDomain;
module.exports.urlHost = urlHost;
