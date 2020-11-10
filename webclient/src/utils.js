import React from "react";
import moment from "moment";
import { Link } from "react-router-dom";

export const sourceLink = (story) => {
	const url = story.url || story.link;
	const urlObj = new URL(url);
	const host = urlObj.hostname.replace(/^www\./, "");
	return (
		<a className="source" href={url}>
			{host}
		</a>
	);
};

export const infoLine = (story) => (
	<div className="info">
		{story.score} points by <a href={story.author_link}>{story.author}</a>
    &#8203; {moment.unix(story.date).fromNow()}
    &#8203; on <a href={story.link}>{story.source}</a> | &#8203;
		<Link
			className={story.num_comments > 99 ? "hot" : ""}
			to={"/" + story.id + "/c"}
		>
			{story.num_comments} comment{story.num_comments !== 1 && "s"}
		</Link>
	</div>
);

export class ToggleDot extends React.Component {
	render() {
		const id = this.props.id;
		const article = this.props.article;
		return (
			<div className="toggleDot">
				<div className="button">
					<Link to={"/" + id + (article ? "" : "/c")}>
						{article ? "" : ""}
					</Link>
				</div>
			</div>
		);
	}
}

export class ForwardDot extends React.Component {
	goForward() {
		localStorage.setItem("scrollLock", "True");
		window.history.forward();
	}

	render() {
		const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
		if (!isMobile) return null;

		return (
			<div className="forwardDot" onClick={this.goForward}>
				<div className="button"></div>
			</div>
		);
	}
}

export const logos = {
	hackernews: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAC4jAAAuIwF4pT92AAAAB3RJTUUH4wgeBhwhciGZUAAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAGCSURBVFjD7Za/S0JRFMc/+oSgLWjLH/2AIKEhC2opIp1amqw/INCo9lbHghCnKDdpN5OoIGhISSLwx2RCEYSjUWhWpO+9hicopCHh8w29Mx3u/XLv95z7Pedcg+y1VQEBbUw0ang5gGBEY9MJ6ARMbaH6HdBnBlmC+5PfsVYX9PTCSx4KyQ4RsI6DxwcYIGSFxF5znHkOtvZBECDoa4tAe0+QDMFDVvFd7ta4pU0QTAo2GeqwBqIHIEkwMAQzaz/3LfNgn1Qw0aAKIswdQzZVy8Jyk+g3lNTfpSEXUakKjgJQrYB5GKY9DRpZALsDxCqEAyqWYT4G6etaFlYaol8HowCZBOSvVO4DR374+gTLCEytgs0JYxPKWtivUh9otOcM3FzC7CI43fBWVKK/vYBCqkudMLIN7yUYHFXe/qMMkZ0utuLyE8ROwWBU6j5+BqXHLs+C+GHdP9/VYBhJ1bpfedXHsU5A5Q9JKxEWa+KT5T8fY5C9NlnXgE7g3xMQNbxf/AZyEGqvyYs/dQAAAABJRU5ErkJggg==",
	reddit: "data:image/png;base64,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",
	tildes: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7EAAAOxAGVKw4bAAABpklEQVRYhe2VsU4bQRRFz51BLvITVEiRQErltBQ0fANCqQNlGmqUgpLSfAA1JRUlTaQ0lIgq+YhIIO17KXa8M2NbtrFWWgq/bndn5513751dsf/VGbDCkM23AFuADwGws3KFVF97v6d2OYDE3ukElIRy4+X2rFeINRQIKIRp/97rA2ag8FwSuOXJ3RAByFI477HDCTORqgEkPv/41jYG3J3n63M8eS4C34+uUMqEu3HzcLE2RBDcnfwmKK+fU0BS5zlmbfMudIYUCAlgk0gEObEwfvgMqJBDamXH2tl8wXFzt25ydyMirLCgVsWrCSNgLrCi589JfttcXE7G7aLcsdpS5GcR8evTMTHda3DG/+47iIDzuPungzDg8O8uTalAKBHNk+dzgxczldM6ERGnJ2fBewGIU2aHxsGKIYbPgBWmVdKvWQ1ZsQYnAko3ui9Ger7o1EgH40q41vL1QWZD9jR6JXZw8OVtVHneQuT9d3yDqcsqp1JSoPTcqD2freEz0OdmTit7zsTSA9U/gAEHbyMKB1Z+rnsFAL37/zB4BrYAW4DBAf4Dcy2YI/VeqRwAAAAASUVORK5CYII=",
	manual: "data:image/png;base64,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",
	substack: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB80lEQVR4Ae3BwUtTcQAH8O/vt98L3/YYYm2TDusUZCBURlTHSV3yTzA8iHcVaYID50HQIWM3BY8P/QdaIAV2a2HIKDGhukgjtqEi7+3trb3X79c7jijbRr2fBz8fAk8sGIiVn0bL8FG/Xu2v1H9UKCSjkIzB43DhFCpOAT5yuHBw4Twg8PT10L6XTy6/go8evzh+dNLgJwwehRJl6Aq7Ax8plCjwUEjG4BECosnRhI+EgMCF84DAE1ZoOPswnIWPpt8Y04bDDQaPqhB1/IY6Dh/NvTPnDAcGhWQUklFIRiEZhWQUklFIRiEZQ5fKdV6e3zXnCQhZuKstxFQaQxcYOlR3RT37wcpm3lsZs8lNeDa/2JvJW6Hk1GBoKshIEB1gaBMX4PpnW0/tGKmSxUtoYTa5mdoxU2v71trivfDi6HV1lBJQtIGhDdvfmtszBWOmeOQUcYaSxUtjr0/HcntWbuVBeCVx9VICf8Fwho+nzkHybe1Z/rCRRweKR05x+Pnx8Mi1npHl+1rmZq8ygD9g+I2qzavp3Vp6/aC+7nLhokv5w0Z+6+v3rYmB4ER6SEtHVRrFLxha2C7s3J6VWyrWlgyHG/gHXC7c1X1rdeOTvTF7W5udHAxNqgwqWkXUQERP9OpxjcXxn8U1FtcTvXpEDUTg+QkFxcDjVd0KBQAAAABJRU5ErkJggg==",
	"the bulletin": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAADwElEQVR4AcXBW2iWBRzH8e/v/z7vfH3du5rOU7p0w8PwkIlM2kIsSbSoGdhFXkRkh0sp6qLool0EddnJKIT0oqguVDDEUjRRYSbOssY2zWpbs3Ind3Dnd8+/HQij8H0f9WKfjwq27HImkTHJjElmTDLjlghHTBDXiZsVcFOccYJEzCjITzAlDkPD0N45QO+wY4wR4EQREJEAR2wqncuzm0tYu7yQRNyQwIGhdEh9Qyv7Tv3GZ4cv0j0QIkQ2ARHl5Bjv7yijomwJZsa/CUjEY9y7+C5WLZrN848uY8c7JzhZ04KZkYmRlRHivP3CGraUL8HMyESKMa/gTjaVFSKJbAKyCllZdAdPbliBZIxJj6T5/Fg9R84209M/zIxUghVF+TyxfhGz86ex+1ANb+w+hySyCYhgU+kCTGKcOx8d+InKPdWYGU7ImANVTby79zyPlS3gy28bcDeQk01ABEVzc8EBgcvZf+pXMEY5Qoxz6B1wvjjWADIQkRgRhCEIMc6haE4uLsa5O9cJZExwogjIwh1+vtyFA2LCW8+VEY8FHDvXTFvPEIZAjHLAESKqgCzc4WBVI69uKyUnCJCMgvwUO196kJGRkLauXhpbrvHL5aucudDK4e+aaO9JE1UsWVJRSQYSdFxLgw9SvnIeJiGEJGJmpJIJ5s/M457iWWwuXcBTm0sYHOqn+mI7ILKJJUsqKslCwOnaVppaOlhZPJ1UcgqS+C9JJOJxHlhdSHdvH9UX2kEik1iypKKSSERtQxe7D9Vx4sdm6ps6aGrppuvaAEEAuYkcxCgJSaxZOotPvq5nOB2SScBNGk5DVU0bp2taQYwShGnuXzaLXa9tpCCVCxJ5yanct7yAo2dbgJAbMW6BBEiAGKcYp2rb+PSbOpyQMZK4e2Yu4GRiROQ4IsRx/kcCE119wzjXuYtsjIie3riIj19Zz4y8OI7jDo5wHHCm5sSoKCvEZIxxD2m80kM2ARFsf2Qxb24vx8zYsLqQI9WNfH+pnZaOfgyxcG6Kx9cVs3T+dP7xV2cfVTV/AiKTgIyMVcV5VD5TTswMychLTmXruhK2ruOG0iMjvL7rBINDApGRkVHI+UtXefG9o7T19OEekk1P/yAvf3icA1V/4CKrgGxM7DvZzPEf9rLtocU8vHY+yxbOITklhgB3ETr8fqWTr840sOdgLU1tgxgiioCI2nvS7Nxfxwf764jHQmakEkxLGCHiavcgXX1pQIAwoguISEwQkB4xrnQO4ThjhADjVgTcBiFulzHJjElmTLK/AU9/SZ4HPrs9AAAAAElFTkSuQmCC",
	webworm: "data:image/png;base64,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",
};

export const getLogoUrl = (story) => {
	return logos[story.source] || logos[story.source.split(' ')[0]] || story.icon;
}