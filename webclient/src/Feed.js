import React from 'react';
import { Link } from 'react-router-dom';
import { sourceLink, infoLine } from './utils.js';

const apiUrl = 'http://news-api.dns.t0.vc/';


class Feed extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			stories: JSON.parse(localStorage.getItem('stories')) || false,
			error: false,
		};
	}
	
    componentDidMount() {
        fetch(apiUrl)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({ stories: result.stories });
                    localStorage.setItem('stories', JSON.stringify(result.stories));
					result.stories.slice(0, 25).forEach(x => {
						fetch(apiUrl + x.id)
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
				{error ?
					<p>Something went wrong.</p>
				:
					<div>
						{stories ?
							<div>
								{stories.map((x, i) =>
									<div className='item'>
										<div className='num'>
											{i+1}.
										</div>

										<div className='title'>
											<Link className='link' to={'/' + x.id + '/a'}>{x.title}</Link>

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
				}
			</div>
		);
	}
}

export default Feed;
