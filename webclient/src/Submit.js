import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

class Submit extends Component {
	constructor(props) {
		super(props);

		this.state = {
			progress: null,
		};

		this.inputRef = React.createRef();
	}

	submitArticle = (event) => {
		event.preventDefault();
		const url = event.target[0].value;
		this.inputRef.current.blur();

		this.setState({ progress: 'Submitting...' });

		let data = new FormData();
		data.append('url', url);

		fetch('/api/submit', { method: 'POST', body: data })
			.then(res => res.json())
			.then(
				(result) => {
					this.props.history.replace('/' + result.nid);
				},
				(error) => {
					this.setState({ progress: 'Error' });
				}
			);
	}

	render() {
		const progress = this.state.progress;

		return (
			<span className='search'>
				<form onSubmit={this.submitArticle}>
					<input
						placeholder='Submit Article'
						ref={this.inputRef}
					/>
				</form>
				{progress ? progress : ''}
			</span>
		);
	}
}

export default withRouter(Submit);
