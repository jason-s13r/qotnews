import createDOMPurify from 'dompurify';
import { JSDOM } from 'jsdom';

export const purify = (story, DOMPurify) => {
	if (!DOMPurify) {
		DOMPurify = createDOMPurify(new JSDOM('').window);
	}
	if (story.title) {
		story.title = DOMPurify.sanitize(story.title);
	}
	if (story.text) {
		story.text = DOMPurify.sanitize(story.text);
	}
	return story;
};

export const purifyArray = (array, DOMPurify) => {
	if (array instanceof Array) {
		if (!DOMPurify) {
			DOMPurify = createDOMPurify(new JSDOM('').window);
		}
		return array.map(story => purify(story, DOMPurify));
	}
	return array;
};