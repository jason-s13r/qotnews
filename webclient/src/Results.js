import React from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { sourceLink, infoLine, logos } from './utils.js';
import AbortController from 'abort-controller';

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
							{stories.length ?
								stories.map((x, i) =>
									<div className='item' key={i}>
										<div className='title'>
											<Link className='link' to={'/' + x.id}>
												<img className='source-logo' src={logos[x.source]} alt='source logo' /> {x.title}
											</Link>

											<span className='source'>
												&#8203;({sourceLink(x)})
											</span>
										</div>

										{infoLine(x)}
									</div>
								)
							:
								<p>none</p>
							}
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
