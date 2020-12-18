<script>
	import { onMount } from "svelte";

	let theme = "light";

	onMount(() => {
		theme = getTheme();
		if (theme === "dark") {
			document.body.classList.toggle("dark-mode");
		} else {
			document.body.classList.remove("dark-mode");
		}
	});

	function toggleDarkMode() {
		document.body.classList.toggle("dark-mode");
		theme = document.body.classList.contains("dark-mode")
			? "dark"
			: "light";
		localStorage.setItem("theme", theme);
	}

	function getTheme() {
		const prefersDarkScheme = window.matchMedia(
			"(prefers-color-scheme: dark)"
		);
		const currentTheme = localStorage.getItem("theme");
		if (!currentTheme && prefersDarkScheme.matches) {
			return "dark";
		}
		return currentTheme || "light";
	}
</script>

<style>
	.fixed-right {
		position: fixed;
		right: 0.5rem;
		bottom: 0.5rem;
	}
	button {
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
