import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import queryString from 'query-string';

const getSearch = props => queryString.parse(props.location.search).q;

class Search extends Component {
	constructor(props) {
		super(props);

		this.state = {search: getSearch(this.props)};
		this.inputRef = React.createRef();
	}

	searchArticles = (event) => {
		const search = event.target.value;
		this.setState({search: search});
		if (search.length >= 3) {
			const searchQuery = queryString.stringify({ 'q': search });
			this.props.history.replace('/search?' + searchQuery);
		} else {
			this.props.history.replace('/');
		}
	}

	searchAgain = (event) => {
		event.preventDefault();
		const searchString = queryString.stringify({ 'q': event.target[0].value });
		this.props.history.push('/search?' + searchString);
		this.inputRef.current.blur();
	}

	render() {
		const search = this.state.search;

		return (
			<span className='search'>
				<form onSubmit={this.searchAgain}>
					<input
						placeholder='Search...'
						value={search}
						onChange={this.searchArticles}
						ref={this.inputRef}
					/>
				</form>
			</span>
		);
	}
}

export default withRouter(Search);
