<script context="module">
  export async function preload({ params }) {
    const res = await this.fetch(`${params.id}.json`);
    const data = await res.json();

    if (res.status === 200) {
      return { story: data.story, related: data.related };
    } else {
      this.error(res.status, data.message);
    }
  }
</script>

<script>
  import fromUnixTime from "date-fns/fromUnixTime";
  import Comment from "../components/Comment.svelte";
  import StoryInfo from "../components/StoryInfo.svelte";
  export let story;
  export let related;

  let others = related.filter((r) => r.id !== story.id && r.num_comments);
  let hasComments = related.some((r) => r.num_comments);
</script>

<style>
  /* .article {
  }
  .article-header {
  }

  .article-header .article-title {
  }

  .article-header .article-byline {
  }
  .article-body {
  } */
  .article-body :global(img) {
    max-width: 100%;
  }

  .spacer {
    margin: 3rem 0;
  }
</style>

<svelte:head>
  <title>{story.title}</title>
  <meta property="og:title" content={story.title} />
  <meta property="og:type" content="article" />
  <meta
    property="article:published_time"
    content={fromUnixTime(story.date).toISOString()} />
  <meta property="article:author" content={story.author || story.source} />
</svelte:head>

<article class="article">
  <header class="article-header">
    <h1 class="article-title">{story.title}</h1>
    <StoryInfo class="article-byline" {story} />
  </header>

  <section class="article-body">
    {@html story.text}
  </section>
</article>

{#if hasComments}
  <hr class="spacer" />

  <section class="comments" id="comments">
    <header>
      <h2>Comments</h2>

      {#if others.length}
        <h3>
          Other discussions:
          {#each others as r}
            {#if r.num_comments}
              <a href="/{r.id}#comments" rel="prefetch">{r.source}</a>
            {/if}
          {/each}
        </h3>
      {/if}
    </header>
    {#if story.comments.length}
      <div class="comments">
        {#each story.comments as comment}
          <Comment {story} {comment} />
        {/each}
      </div>
    {/if}
  </section>
{/if}
