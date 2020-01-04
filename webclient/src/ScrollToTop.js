import React from 'react';
import { withRouter } from 'react-router-dom';

class ScrollToTop extends React.Component {
	componentDidUpdate(prevProps) {
		//console.log(this.props.location.pathname, prevProps.location.pathname);

		if (this.props.location.pathname === prevProps.location.pathname) {
			return;
		}

		if (localStorage.getItem('scrollLock') === 'True') {
			localStorage.setItem('scrollLock', 'False');
			return;
		}

		window.scrollTo(0, 0);
	}

	render() {
		return null;
	}
}

export default withRouter(ScrollToTop);
