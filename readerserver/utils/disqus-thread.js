module.exports.disqusThread = data => {
	const comments = data.response.posts.reduce((c, post) => ({
		...c,
		[post.id.toString()]: {
			author: post.author.name,
			authorLink: post.author.profileUrl,
			date: post.createdAt,
			text: post.raw_message,
			score: post.points,
			children: [],
			id: post.id.toString(),
			parent: (post.parent || '').toString(),
		}
	}), {});
	Object.keys(comments).filter(id => !!comments[id].parent).forEach(id => {
		const comment = comments[id];
		comments[comment.parent].children.push(comment);
	});
	const parents = Object.keys(comments).filter(id => comments[id].parent).map(id => comments[id]);
	return parents;
};