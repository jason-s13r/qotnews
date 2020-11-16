import React from 'react';
import { Helmet } from 'react-helmet';
import AbortController from 'abort-controller';
import { StoryItem } from '../components/StoryItem.js';

class Results extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			stories: false,
			error: false,
		};

		this.controller = null;
	}

	performSearch = () => {
		if (this.controller) {
			this.controller.abort();
		}

		this.controller = new AbortController();
		const signal = this.controller.signal;

		const search = this.props.location.search;
		fetch('/api/search' + search, { method: 'get', signal: signal })
			.then(res => res.json())
			.then(
				(result) => {
					this.setState({ stories: result.results });
				},
				(error) => {
					if (error.message !== 'The operation was aborted. ') {
						this.setState({ error: true });
					}
				}
			);
	}

	componentDidMount() {
		this.performSearch();
	}

	componentDidUpdate(prevProps) {
		if (this.props.location.search !== prevProps.location.search) {
			this.performSearch();
		}
	}

	render() {
		const stories = this.state.stories;
		const error = this.state.error;

		return (
			<div className='container'>
				<Helmet>
					<title>Feed - QotNews</title>
				</Helmet>
				{error && <p>Connection error?</p>}
				{stories ?
					<>
						<p>Search results:</p>
						<div className='comment lined'>
							{stories ? stories.map(story => <StoryItem story={story}></StoryItem>) : <p>loading...</p>}
						</div>
					</>
					:
					<p>loading...</p>
				}
			</div>
		);
	}
}

export default Results;
