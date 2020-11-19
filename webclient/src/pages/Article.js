import React from 'react';
import { Helmet } from 'react-helmet';
import localForage from 'localforage';
import { sourceLink, infoLine, ToggleDot } from '../utils.js';
import { Link } from "react-router-dom";

class Article extends React.Component {
	constructor(props) {
		super(props);

		const id = this.props.match ? this.props.match.params.id : 'CLOL';
		const cache = this.props.cache;

		if (id in cache) console.log('cache hit');

		this.state = {
			story: cache[id] || false,
			related: [],
			error: false,
			pConv: [],
		};
	}

	componentDidMount() {
		const id = this.props.match ? this.props.match.params.id : 'CLOL';

		localForage.getItem(id)
			.then(
				(value) => {
					if (value) {
						this.setState({ story: value });
					}
				}
			);

		fetch('/api/' + id)
			.then(res => res.json())
			.then(
				(result) => {
					this.setState({ story: result.story, related: result.related });
					localForage.setItem(id, result.story);
				},
				(error) => {
					this.setState({ error: true });
				}
			);
	}

	pConvert = (n) => {
		this.setState({ pConv: [...this.state.pConv, n] });
	}

	render() {
		const id = this.props.match ? this.props.match.params.id : 'CLOL';
		const story = this.state.story;
		const related = this.state.related;//.filter(r => r.id != id);
		const error = this.state.error;
		const pConv = this.state.pConv;
		let nodes = null;

		if (story.text) {
			let div = document.createElement('div');
			div.innerHTML = story.text;
			nodes = div.childNodes;
		}

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

						{related.length ? <div className='related indented info'>
							<span>Other discussions: </span>
							{related.map((r, i) =>
								<>
									{i !== 0 ? <> &bull; </> : <></>}
									<Link className='' to={"/" + r.id + "/c"}>{r.source}</Link>
								</>
							)}
						</div> : <></>}

						{nodes ?
							<div className='story-text'>
								{Object.entries(nodes).map(([k, v]) =>
									pConv.includes(k) ?
										v.innerHTML.split('\n\n').map(x =>
											<p dangerouslySetInnerHTML={{ __html: x }} />
										)
										:
										(v.nodeName === '#text' ?
											<p>{v.data}</p>
											:
											<>
												<v.localName dangerouslySetInnerHTML={v.innerHTML ? { __html: v.innerHTML } : null} />
												{v.localName == 'pre' && <button onClick={() => this.pConvert(k)}>Convert Code to Paragraph</button>}
											</>
										)
								)}
							</div>
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
