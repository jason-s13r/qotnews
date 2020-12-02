import React from 'react';
import { Helmet } from 'react-helmet';
import AbortController from 'abort-controller';
import { Link } from "react-router-dom";
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
		const params = new URLSearchParams(search);
		params.set('skip', params.get('skip') || 0);
		params.set('limit', params.get('limit') || 20);
		fetch('/api/search?' + params.toString(), { method: 'get', signal: signal })
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

		const search = this.props.location.search;
		const params = new URLSearchParams(search);

		const q = params.get('q') || '';
		const skip = params.get('skip') || 0;
		const limit = params.get('limit') || 20;

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

				<div className="pagination">
					{Number(skip) > 0 && <Link className="pagination-link" to={`/search?q=${q}&skip=${Number(skip) - Math.min(Number(skip), Number(limit))}&limit=${limit}`}>Previous</Link>}
					{stories.length == Number(limit) && <Link className="pagination-link is-right" to={`/search?q=${q}&skip=${Number(skip) + Number(limit)}&limit=${limit}`}>Next</Link>}
				</div>
			</div>
		);
	}
}

export default Results;
