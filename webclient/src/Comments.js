import React from 'react';
import { Link } from 'react-router-dom';
import { HashLink } from 'react-router-hash-link';
import { Helmet } from 'react-helmet';
import moment from 'moment';
import localForage from 'localforage';
import { infoLine, ToggleDot } from './utils.js';

class Article extends React.Component {
	constructor(props) {
		super(props);

		const id = this.props.match.params.id;
		const cache = this.props.cache;

		if (id in cache) console.log('cache hit');

		this.state = {
			story: cache[id] || false,
			error: false,
			collapsed: [],
			expanded: [],
		};
	}

	componentDidMount() {
		const id = this.props.match.params.id;

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
					this.setState({ story: result.story }, () => {
						const hash = window.location.hash.substring(1);
						if (hash) {
							document.getElementById(hash).scrollIntoView();
						}
					});
					localForage.setItem(id, result.story);
				},
				(error) => {
					this.setState({ error: true });
				}
			);
	}

	collapseComment(cid) {
		this.setState(prevState => ({
			...prevState,
			collapsed: [...prevState.collapsed, cid],
			expanded: prevState.expanded.filter(x => x !== cid),
		}));
	}

	expandComment(cid) {
		this.setState(prevState => ({
			...prevState,
			collapsed: prevState.collapsed.filter(x => x !== cid),
			expanded: [...prevState.expanded, cid],
		}));
	}

	countComments(c) {
		return c.comments.reduce((sum, x) => sum + this.countComments(x), 1);
	}

	displayComment(story, c, level) {
		const cid = c.author + c.date;

		const collapsed = this.state.collapsed.includes(cid);
		const expanded = this.state.expanded.includes(cid);

		const hidden = collapsed || (level == 4 && !expanded);
		const hasChildren = c.comments.length !== 0;

		return (
			<div className={level ? 'comment lined' : 'comment'} key={cid}>
				<div className='info'>
					<p>
						{c.author === story.author ? '[OP]' : ''} {c.author || '[Deleted]'}
						{' '} | <HashLink to={'#' + cid} id={cid}>{moment.unix(c.date).fromNow()}</HashLink>

						{hasChildren && (
							hidden ?
								<span className='collapser pointer' onClick={() => this.collapseComment(cid)}>–</span>
								:
								<span className='collapser expander pointer' onClick={() => this.expandComment(cid)}>+</span>
						)}
					</p>
				</div>

				<div className={collapsed ? 'text hidden' : 'text'} dangerouslySetInnerHTML={{ __html: c.text }} />

				{hidden && hasChildren ?
					<div className='comment lined info pointer' onClick={() => this.expandComment(cid)}>[show {this.countComments(c) - 1} more]</div>
					:
					c.comments.map(i => this.displayComment(story, i, level + 1))
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
				{error && <p>Connection error?</p>}
				{story ?
					<div className='article'>
						<Helmet>
							<title>{story.title} - QotNews Comments</title>
						</Helmet>

						<h1>{story.title}</h1>

						<div className='info'>
							<Link to={'/' + story.id}>View article</Link>
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
		);
	}
}

export default Article;
