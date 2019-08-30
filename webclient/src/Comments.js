import React from 'react';
import { Link } from 'react-router-dom';
import moment from 'moment';
import { sourceLink, infoLine, ToggleDot } from './utils.js';

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

	displayComment(story, c, level) {
		return (
			<div className={level ? 'comment lined' : 'comment'}>
				<div className='info'>
					<p>{c.author === story.author ? '[OP]' : ''} {c.author || '[Deleted]'} | {moment.unix(c.date).fromNow()}</p>
				</div>

				<div className='text' dangerouslySetInnerHTML={{ __html: c.text }} />

				{level < 5 ?
					c.comments.map(i => this.displayComment(story, i, level + 1))
				:
					<div className='info'><p>[replies snipped]</p></div>
				}
			</div>
		);
	}

	render() {
		const id = this.props.match.params.id;
		const story = this.state.story;
		const error = this.state.error;

		return (
			<div className='container'>
				{error ?
					<p>Something went wrong.</p>
				:
					<div>
						{story ?
							<div className='article'>
								<h1>{story.title}</h1>

								<div className='info'>
									<Link to={'/' + story.id + '/a'}>View article</Link>
								</div>

								{infoLine(story)}

								<div className='comments'>
									{story.comments.map(c => this.displayComment(story, c, 0))}
								</div>
							</div>
						:
							<p>loading...</p>
						}
						<ToggleDot id={id} article={true} />
					</div>
				}
			</div>
		);
	}
}

export default Article;
