<script>
  import StoryInfo from "../components/StoryInfo.svelte";
  export let story;

  let host = new URL(story.url || story.link).hostname.replace(/^www\./, "");
</script>

<style>
  .article-title {
    text-align: justify;
  }
  .article-header {
    padding: 0 0 1rem;
  }
  .article-body {
    max-width: 45rem;
    margin: 0 auto;
  }
  .article-body :global(figure) {
    margin: 0;
  }
  .article-body :global(figcaption p),
  .article-body :global(figcaption) {
    padding: 0;
    margin: 0;
  }
  .article-body :global(figcaption) {
    font-style: italic;
    margin: 0 1rem;
    font-size: 0.9em;
    text-align: justify;
  }
  .article-body :global(figure),
  .article-body :global(img) {
    max-width: 100%;
    height: auto;
  }
</style>

<article class="article">
  <header class="article-header">
    <h1 class="article-title">{story.title}</h1>
    {#if story.url}
      <div>source: <a href={story.url}>{host}</a></div>
    {/if}
    <StoryInfo class="article-byline" {story} />
  </header>

  <section class="article-body">
    {@html story.text}
  </section>
</article>
