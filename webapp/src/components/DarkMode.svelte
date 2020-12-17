<script>
	import { onMount } from "svelte";

	let theme = "light";

	onMount(() => {
		const prefersDarkScheme = window.matchMedia(
			"(prefers-color-scheme: dark)"
		);
		let currentTheme = localStorage.getItem("theme");
		if (!currentTheme && prefersDarkScheme.matches) {
			currentTheme = "dark";
		}
		if (currentTheme == "dark") {
			document.body.classList.toggle("dark-mode");
		} else if (currentTheme == "light") {
			document.body.classList.toggle("light-mode");
		}
		theme = document.body.classList.contains("dark-mode")
			? "dark"
			: "light";
	});
	function toggleDarkMode() {
		const prefersDarkScheme = window.matchMedia(
			"(prefers-color-scheme: dark)"
		);
		if (prefersDarkScheme.matches) {
			document.body.classList.toggle("light-mode");
		} else {
			document.body.classList.toggle("dark-mode");
		}
		theme = document.body.classList.contains("dark-mode")
			? "dark"
			: "light";
		localStorage.setItem("theme", theme);
	}
</script>

<style>
	.fixed-right {
		position: fixed;
		right: 1rem;
		bottom: 1rem;
	}
	button {
		margin: 0.75em 0;
		background-color: #f76027;
		color: white;
		border: none;
		border-radius: 4px;
		padding: 0.5rem;
		text-transform: uppercase;
	}
	:global(.dark-mode) button {
		background-color: #0084f6;
		color: white;
	}
</style>

<div class="fixed-right">
	<button on:click={toggleDarkMode}>{theme}</button>
</div>
