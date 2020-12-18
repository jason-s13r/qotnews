<script>
  import { getLogoUrl } from "../utils/logos.js";
  import StoryInfo from "../components/StoryInfo.svelte";
  export let stories;

  const host = (url) => new URL(url).hostname.replace(/^www\./, "");
</script>

<style>
  .story-item {
    margin: 0.5rem 0 0;
    padding-left: 1.2em;
  }
  .story-icon,
  .story-title {
    font-size: 1.2rem;
  }
  .story-icon {
    width: 1rem;
    height: 1rem;
    margin-left: -1.2em;
  }
  :global(.dark-mode) .story-icon {
    filter: brightness(0.8) contrast(1.2) drop-shadow(0 0 0.5px #fff);
  }
  .story-source::before {
    content: "(";
  }
  .story-source::after {
    content: ")";
  }

  .story-item :global(a) {
    text-decoration: none;
  }
  .story-item :global(a:hover) {
    text-decoration: underline;
  }
</style>

{#each stories as story}
  <article class="story-item">
    <header class="story-header">
      <img src={getLogoUrl(story)} alt="logo" class="story-icon" />
      <a class="story-title" rel="prefetch" href="/{story.id}">
        {@html story.title}
      </a>
      <a
        class="story-source"
        href={story.url || story.link}>{host(story.url || story.link)}</a>
    </header>
    <aside class="story-info">
      <StoryInfo {story} />
    </aside>
  </article>
{/each}

<slot />
