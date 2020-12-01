import React from 'react';
import { Helmet } from 'react-helmet';
import localForage from 'localforage';
import { Link } from "react-router-dom";
import { StoryItem } from '../components/StoryItem.js';

class Feed extends React.Component {
	constructor(props) {
		super(props);

		const query = new URLSearchParams(this.props.location.search);

		this.state = {
			stories: JSON.parse(localStorage.getItem('stories')) || false,
			error: false,
			skip: +query.get('skip') || 0,
			limit: +query.get('limit') || 20
		};
	}

	componentDidMount() {
		fetch(`/api?skip=${this.state.skip}&limit=${this.state.limit}`)
			.then(res => res.json())
			.then(
				(result) => {
					const updated = !this.state.stories || this.state.stories[0].id !== result.stories[0].id;
					console.log('updated:', updated);

					const { stories } = result;
					this.setState({ stories });
					localStorage.setItem('stories', JSON.stringify(stories));

					if (updated) {
						localForage.clear();
						stories.forEach((x, i) => {
							fetch('/api/' + x.id)
								.then(res => res.json())
								.then(({ story, related }) => {
									Promise.all([
										localForage.setItem(x.id, story),
										localForage.setItem(`related-${x.id}`, related)
									]).then(console.log('preloaded', x.id, x.title));
									this.props.updateCache(x.id, story);
									this.props.updateCache(`related-${x.id}`, related);
								}, error => { }
								);
						});
					}
				},
				(error) => {
					this.setState({ error: true });
				}
			);
	}

	render() {
		const stories = this.state.stories;
		const error = this.state.error;
		const skip = this.state.skip;
		const limit = this.state.limit;

		return (
			<div className='container'>
				<Helmet>
					<title>Feed - QotNews</title>
				</Helmet>
				{error && <p>Connection error?</p>}
				{stories ? stories.map(story => <StoryItem story={story}></StoryItem>) : <p>loading...</p>}

				<div className="pagination">
					{Number(skip) > 0 && <Link className="pagination-link" to={`/?skip=${Number(skip) - Math.min(Number(skip), Number(limit))}&limit=${limit}`}>Previous</Link>}
					{stories.length == Number(limit) && <Link className="pagination-link is-right" to={`/?skip=${Number(skip) + Number(limit)}&limit=${limit}`}>Next</Link>}
				</div>
			</div>
		);
	}
}

export default Feed;
