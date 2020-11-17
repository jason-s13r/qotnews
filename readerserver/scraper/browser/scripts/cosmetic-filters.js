(function () {
	removeHiddenElements();

	if (matchDomain("stuff.co.nz")) {
		removeSelectors([
			".support-brief-container",
			'[class*="donation-in-"]',
			".sics-component__sharebar",
			".breaking-news-pointer",
			".bigbyline-container",
			[
				".sics-component__html-injector.sics-component__story__paragraph",
				"READ MORE:",
			],
		]);
	}
	if (matchDomain("nzherald.co.nz")) {
		removeSelectors([
			"[href$='#commenting-widget']",
			".related-articles",
			".article__print-button",
			".share-bar",
			".c-suggest-links.read-more-links",
			".website-of-year",
			".meta-data",
			".article__kicker",
			".author__image",
		]);
	}
	if (matchDomain(["rnz.co.nz", "radionz.co.nz"])) {
		removeSelectors([".c-advert-app", ".c-sub-nav"]);
	}
	if (matchDomain(["newsroom.co.nz"])) {
		removeSelectors([".article_content__section", ".bio"]);
	}
	if (matchDomain(["newshub.co.nz"])) {
		removeSelectors([
			".c-ArticleHeading-authorPicture",
			".relatedarticles",
			".ArticleAttribution",
			'.GlobalFooter'
		]);
	}
	if (matchDomain(["tvnz.co.nz"])) {
		removeSelectors([".signup-container container"]);
	}
	if (matchDomain(["thespinoff.co.nz"])) {
		removeSelectors([".the-spinoff-club-interruptive", ".bulletin-signup"]);
	}

	function matchDomain(domains) {
		const hostname = window.location.hostname;
		if (typeof domains === "string") {
			domains = [domains];
		}
		return domains.some(
			(domain) => hostname === domain || hostname.endsWith("." + domain)
		);
	}

	function removeDOMElement(...elements) {
		for (const element of elements) {
			if (element) {
				element.remove();
			}
		}
	}

	function pageContains(selector, text) {
		const elements = document.querySelectorAll(selector);
		return Array.prototype.filter.call(elements, function (element) {
			return RegExp(text).test(element.textContent);
		});
	}

	function removeHiddenElements() {
		window.setTimeout(function () {
			const selector = "*:not(script):not(head):not(meta):not(link):not(style)";
			Array.from(document.querySelectorAll(selector))
				.filter((element) => {
					const computed = getComputedStyle(element);
					const displayNone = computed["display"] === "none";
					const visibilityHidden = computed["visibility"] === "hidden";
					return displayNone || visibilityHidden;
				})
				.forEach((element) => element && element.remove());
		}, 1000);
	}

	function removeSelectors(selectors) {
		window.setTimeout(function () {
			const elements = selectors.flatMap((s) => {
				if (typeof s === "string") {
					return Array.from(document.querySelectorAll(s));
				}
				if (s && s.constructor.name === "Array") {
					return pageContains(...s);
				}
				return undefined;
			});
			removeDOMElement(...elements);
		}, 1000);
	}
})();
