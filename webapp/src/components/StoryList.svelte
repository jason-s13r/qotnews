<script>
  import DOMPurify from "dompurify";
  import { onMount } from "svelte";
  import { getLogoUrl } from "../utils/logos.js";
  import StoryInfo from "../components/StoryInfo.svelte";
  export let stories;

  const host = (url) => new URL(url).hostname.replace(/^www\./, "");
  let purify;

  onMount(() => {
    purify = (html) => DOMPurify.sanitize(html);
  });
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
    margin-left: -1.2rem;
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
      <img
        src={getLogoUrl(story)}
        alt="logo"
        class="story-icon"
        style="height: 1rem; width: 1rem;" />
      <a class="story-title" rel="prefetch" href="/{story.id}">
        {#if !purify}
          {story.title}
        {:else}
          {@html purify(story.title)}
        {/if}
      </a>
      <a
        class="story-source"
        href={story.url || story.link}>{host(story.url || story.link)}</a>
    </header>
    <section class="story-info">
      <StoryInfo {story} />
    </section>
  </article>
{/each}

<slot />
