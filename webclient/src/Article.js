import React from 'react';
import { Helmet } from 'react-helmet';
import localForage from 'localforage';
import { sourceLink, infoLine, ToggleDot } from './utils.js';

class Article extends React.Component {
	constructor(props) {
		super(props);

		const id = this.props.match ? this.props.match.params.id : 'CLOL';
		const cache = this.props.cache;

		if (id in cache) console.log('cache hit');

		this.state = {
			story: cache[id] || false,
			error: false,
		};
	}
	
	componentDidMount() {
		const id = this.props.match ? this.props.match.params.id : 'CLOL';

		localForage.getItem(id)
			.then(
				(value) => {
					this.setState({ story: value });
				}
			);

		fetch('/api/' + id)
			.then(res => res.json())
			.then(
				(result) => {
					this.setState({ story: result.story });
					localForage.setItem(id, result.story);
				},
				(error) => {
					this.setState({ error: true });
				}
			);
	}

	render() {
		const id = this.props.match ? this.props.match.params.id : 'CLOL';
		const story = this.state.story;
		const error = this.state.error;

		return (
			<div className='article-container'>
				{error && <p>Connection error?</p>}
				{story ?
					<div className='article'>
						<Helmet>
							<title>{story.title} - QotNews</title>
						</Helmet>

						<h1>{story.title}</h1>

						<div className='info'>
							Source: {sourceLink(story)}
						</div>

						{infoLine(story)}

						{story.text ?
							<div className='story-text' dangerouslySetInnerHTML={{ __html: story.text }} />
						:
							<p>Problem getting article :(</p>
						}
					</div>
				:
					<p>loading...</p>
				}
				<ToggleDot id={id} article={false} />
			</div>
		);
	}
}

export default Article;
