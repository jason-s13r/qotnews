import React from 'react';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';
import './Style-light.css';
import './Style-dark.css';
import './fonts/Fonts.css';
import Feed from './Feed.js';
import Article from './Article.js';
import Comments from './Comments.js';
import ScrollToTop from './ScrollToTop.js';

class App extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			theme: localStorage.getItem('theme') || '',
		};
	}

	light() {
		this.setState({ theme: '' });
		localStorage.setItem('theme', '');
	}

	dark() {
		this.setState({ theme: 'dark' });
		localStorage.setItem('theme', 'dark');
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
					</div>
					<Route path='/' exact component={Feed} />
					<Route path='/:id/c' exact component={Comments} />
					<Route path='/:id' exact component={Article} />

					<ScrollToTop />
				</Router>
			</div>
		);
	}
}

export default App;
