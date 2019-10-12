import React from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { siteLogo, sourceLink, infoLine } from './utils.js';

class Results extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			stories: false,
			error: false,
		};

	}

	performSearch = () => {
		const search = this.props.location.search;
		fetch('/api/search' + search)
			.then(res => res.json())
			.then(
				(result) => {
					this.setState({ stories: result.results });
				},
				(error) => {
					this.setState({ error: true });
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
					<div>
						{stories.length ?
							stories.map((x, i) =>
								<div className='item' key={i}>
									<div className='num'>
										{i+1}.
									</div>

									<div className='title'>
										<Link className='link' to={'/' + x.id}>{siteLogo[x.source]} {x.title}</Link>

										<span className='source'>
											&#8203;({sourceLink(x)})
										</span>
									</div>

									{infoLine(x)}
								</div>
							)
						:
							<p>no results</p>
						}
					</div>
				:
					<p>loading...</p>
				}
			</div>
		);
	}
}

export default Results;
