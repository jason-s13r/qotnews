import React from 'react';
import { Link } from 'react-router-dom';
import { sourceLink, infoLine } from './utils.js';

const apiUrl = 'http://news-api.dns.t0.vc/';

class Article extends React.Component {
	constructor(props) {
		super(props);

		const id = this.props.match.params.id;

		this.state = {
			story: JSON.parse(localStorage.getItem(id)) || false,
			error: false,
		};
	}
	
    componentDidMount() {
		const id = this.props.match.params.id;

        fetch(apiUrl + id)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({ story: result.story });
                    localStorage.setItem(id, JSON.stringify(result.story));
                },
                (error) => {
                    this.setState({ error: true });
                }
            );
	}

	render() {
		const story = this.state.story;
		const error = this.state.error;

		return (
			<div className='article-container'>
				{error ?
					<p>Something went wrong.</p>
				:
					<div>
						{story ?
							<div className='article'>
								<h1>{story.title}</h1>

								<div className='info'>
									Source: {sourceLink(story)}
								</div>

								{infoLine(story)}

								{story.text ?
									<div dangerouslySetInnerHTML={{ __html: story.text }} />
								:
									<p>Problem getting article :(</p>
								}
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

export default Article;
