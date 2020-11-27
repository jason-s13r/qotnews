<script context="module">
  export function preload() {
    return this.fetch(`index.json`)
      .then((r) => r.json())
      .then(({ stories }) => {
        return { stories };
      });
  }
</script>

<script>
  import { getLogoUrl } from "../utils/logos.js";
  import StoryInfo from "../components/StoryInfo.svelte";

  export let stories;
</script>

<style>
  article {
    margin: 0.5rem 0;
  }
</style>

<svelte:head>
  <title>News</title>
</svelte:head>

<section>
  {#each stories as story}
    <!-- we're using the non-standard `rel=prefetch` attribute to
				tell Sapper to load the data for the page as soon as
				the user hovers over the link or taps it, instead of
				waiting for the 'click' event -->
    <article>
      <header>
        <img
          src={getLogoUrl(story)}
          alt="logo"
          style="height: 1rem; width: 1rem;" />
        <a rel="prefetch" href="/{story.id}">{story.title}</a>
        (<a href={story.url || story.link}>
          {new URL(story.url || story.link).hostname.replace(/^www\./, '')}
        </a>)
      </header>
      <section>
        <StoryInfo {story} />
      </section>
    </article>
  {/each}
</section>
