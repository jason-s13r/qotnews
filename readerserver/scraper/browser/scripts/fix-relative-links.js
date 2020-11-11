(function () {
	const { host, protocol } = window.location;
	const url = `${protocol}//${host}`;
	[
		['[src^="/"]', 'src'],
		['[href^="/"]', 'href']
	].forEach(([selector, attribute]) => {
		Array.from(document.querySelectorAll(selector))
			.filter(e => e.attributes[attribute] && /^\/[^\/]/.test(e.attributes[attribute].value))
			.forEach((e) => {
				e.attributes[attribute].value = `${url}${e.attributes[attribute].value}`;
			});
	});
})();
