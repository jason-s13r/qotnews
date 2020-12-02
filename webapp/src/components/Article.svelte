<script>
  import StoryInfo from "../components/StoryInfo.svelte";
  import Html from "../components/Html.svelte";

  export let story;

  let host = new URL(story.url || story.link).hostname.replace(/^www\./, "");
</script>

<style>
  .article :global(h1),
  .article :global(h2),
  .article :global(h3),
  .article :global(h4),
  .article :global(h5),
  .article :global(h6) {
    margin: 0 0 0.5em 0;
    font-weight: 400;
    line-height: 1.2;
  }

  .article :global(h1) {
    font-size: 2rem;
  }

  @media only screen and (min-device-width: 320px) and (max-device-width: 480px) {
    .article :global(h1) {
      font-size: 1.5rem;
    }
  }
  .article-title {
    text-align: left;
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
    <h1 class="article-title">
      <Html html={story.title} />
    </h1>
    {#if story.url}
      <div>source: <a class="article-source" href={story.url}>{host}</a></div>
    {/if}
    <section class="article-info">
      <StoryInfo {story} />
    </section>
  </header>

  <section class="article-body">
    <Html html={story.text} />
  </section>
</article>
