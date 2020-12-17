import { JSDOM } from 'jsdom';

export const samesite = (story, links) => {
	if (story.text && links) {
		const { window } = new JSDOM(`<html>${story.text}</html>`);
		links.forEach((item) => {
			const $links = window.document.querySelectorAll(`a[href="${item.url}"]`);
			Array.from($links, ($source) => {
				const $link = $source.cloneNode(true);
				$link.href = `/${item.id}`;
				$link.setAttribute("class", "internal-link");
				$link.setAttribute("rel", "prefetch");
				$source.innerHTML = "source";
				$source.setAttribute("class", "external-source-link");
				$source.parentNode.insertBefore($link, $source);
			});
		});
		const $html = window.document.querySelector('html');
		story.text = $html.innerHTML || story.text;
	}
	return story;
};