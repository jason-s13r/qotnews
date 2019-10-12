import React from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { siteLogo, sourceLink, infoLine } from './utils.js';
import { clearStorage } from './utils.js';

class Feed extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			stories: JSON.parse(localStorage.getItem('stories')) || false,
			error: false,
		};
	}

	componentDidMount() {
		fetch('/api')
			.then(res => res.json())
			.then(
				(result) => {
					this.setState({ stories: result.stories });
					clearStorage();
					localStorage.setItem('stories', JSON.stringify(result.stories));
					result.stories.filter(x => x.score >= 20).slice(0, 25).forEach(x => {
						fetch('/api/' + x.id)
							.then(res => res.json())
							.then(result => {
								localStorage.setItem(x.id, JSON.stringify(result.story));
								console.log('Preloaded story', x.id, x.title);
							}, error => {}
						);
					});
				},
				(error) => {
					this.setState({ error: true });
				}
			);
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
						{stories.map((x, i) =>
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
						)}
					</div>
				:
					<p>loading...</p>
				}
			</div>
		);
	}
}

export default Feed;
