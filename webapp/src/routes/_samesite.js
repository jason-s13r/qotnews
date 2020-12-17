import { JSDOM } from 'jsdom';

export const samesite = (story, links) => {
	console.log(story.text && links);
	if (story.text && links) {
		const { window } = new JSDOM(`<html>${story.text}</html>`);
		links.forEach((item) => {
			const $links = window.document.querySelectorAll(`a[href="${item.url}"]`);
			Array.from($links, ($link) => {
				$link.href = `/${item.id}`;
				$link.setAttribute("rel", "prefetch");
			});
		});
		const $html = window.document.querySelector('html');
		story.text = $html.innerHTML || story.text;
	}
	return story;
};