import React from 'react';
import { BrowserRouter as Router, Route, Link, Switch } from 'react-router-dom';
import localForage from 'localforage';
import './Style-light.css';
import './Style-dark.css';
import './fonts/Fonts.css';
import { ForwardDot } from './utils.js';
import Search from './Search.js';
import Submit from './Submit.js';
import ScrollToTop from './ScrollToTop.js';
import Feed from './pages/Feed.js';
import Article from './pages/Article.js';
import Comments from './pages/Comments.js';
import Results from './pages/Results.js';


class App extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			theme: localStorage.getItem('theme') || '',
		};

		this.cache = {};
	}

	updateCache = (key, value) => {
		this.cache[key] = value;
	}

	light() {
		this.setState({ theme: '' });
		localStorage.setItem('theme', '');
	}

	dark() {
		this.setState({ theme: 'dark' });
		localStorage.setItem('theme', 'dark');
	}

	componentDidMount() {
		if (!this.cache.length) {
			localForage.iterate((value, key) => {
				this.updateCache(key, value);
			});
			console.log('loaded cache from localforage');
		}
	}

	render() {
		const theme = this.state.theme;
		document.body.style.backgroundColor = theme === 'dark' ? '#000' : '#eeeeee';

		return (
			<div className={theme}>
				<Router>
					<div className='container menu'>
						<p>
							<Link to='/'>QotNews - Feed</Link>
							<span className='theme'>Theme: <a href='#' onClick={() => this.light()}>Light</a> - <a href='#' onClick={() => this.dark()}>Dark</a></span>
							<br />
							<span className='slogan'>Reddit, Hacker News, and Tildes combined, then pre-rendered in reader mode.</span>
						</p>
						<Route path='/(|search)' component={Search} />
						<Route path='/(|search)' component={Submit} />
					</div>

					<Route path='/' exact render={(props) => <Feed {...props} updateCache={this.updateCache} />} />
					<Switch>
						<Route path='/search' component={Results} />
						<Route path='/:id' exact render={(props) => <Article {...props} cache={this.cache} />} />
					</Switch>
					<Route path='/:id/c' exact render={(props) => <Comments {...props} cache={this.cache} />} />

					<ForwardDot />

					<ScrollToTop />
				</Router>
			</div>
		);
	}
}

export default App;
