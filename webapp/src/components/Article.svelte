<script>
  import StoryInfo from "../components/StoryInfo.svelte";
  import StoryMeta from "../components/StoryMeta.svelte";

  export let story;
</script>

<style>
  @import url(/fonts/Fonts.css);
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
    font: 1.2rem/1.5 "Apparatus SIL", sans-serif;
    text-rendering: optimizeLegibility;
  }
  .article-body :global(figure p),
  .article-body :global(figure),
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
  .article-body :global(video),
  .article-body :global(img) {
    max-width: 100%;
    height: auto;
  }

  .article-body :global(a:not(.internal-link)) {
    padding-right: 1rem;
    background: url(/external-link.svg) no-repeat;
    background-position: center right;
    background-size: 0.75em;
  }
  .article-body :global(.external-source-link) {
    font-variant: small-caps;
    margin-left: 0.25rem;
    font-size: 0.7em;
    text-decoration: none;
  }
</style>

<svelte:head>
  <link rel="preload" href="/external-link.svg" as="image" />
</svelte:head>

<article class="article">
  <header class="article-header">
    <h1 class="article-title">
      {@html story.title}
    </h1>

    <section class="article-info">
      <StoryInfo {story} />
    </section>
    <aside class="article-info">
      <StoryMeta {story} />
    </aside>
  </header>

  <section class="article-body">
    {@html story.text}
  </section>
</article>
