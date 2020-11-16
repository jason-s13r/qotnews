import React from "react";
import { Link } from "react-router-dom";
import { sourceLink, infoLine, getLogoUrl } from "../utils.js";

export class StoryItem extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		const story = this.props.story;
		const { id, title } = story;

		return (
			<div className="item" key={id}>
				<div className="title">
					<Link className="link" to={"/" + id}>
						<img
							className="source-logo"
							src={getLogoUrl(story)}
							alt="source logo"
						/>
						{" "}
						{title}
					</Link>

					<span className="source">({sourceLink(story)})</span>
				</div>

				{infoLine(story)}
			</div>
		);
	}
}
