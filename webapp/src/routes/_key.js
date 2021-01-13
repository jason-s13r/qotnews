export const keyStory = (story, key) => {
	if (story.id) {
		story.id = `${key}-${story.id}`;
	}
	return story;
};

export const keyStories = (array, key) => {
	if (array instanceof Array) {
		return array.map(story => keyStory(story, key));
	}
	return array;
};