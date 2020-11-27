<script context="module">
  export async function preload({ params }) {
    // the `slug` parameter is available because
    // this file is called [slug].svelte
    const res = await this.fetch(`${params.id}.json`);
    const data = await res.json();

    if (res.status === 200) {
      const related = [];
      const others = data.related.filter(
        (r) => r.id !== data.story.id && !!r.num_comments
      );
      for (const other of others) {
        const r = await this.fetch(`${other.id}.json`);
        if (r.ok) {
          const d = await r.json();
          related.push(d.story);
        }
      }
      return { story: data.story, related };
    } else {
      this.error(res.status, data.message);
    }
  }
</script>

<script>
  import Comment from "../components/Comment.svelte";
  import StoryInfo from "../components/StoryInfo.svelte";
  export let story;
  export let related;

  let hasComments = story.num_comments || related.length;
</script>

<style>
  /*
		By default, CSS is locally scoped to the component,
		and any unused styles are dead-code-eliminated.
		In this page, Svelte can't know which elements are
		going to appear inside the {{{post.html}}} block,
		so we have to use the :global(...) modifier to target
		all elements inside .content
	*/
  .content :global(h2) {
    font-size: 1.4em;
    font-weight: 500;
  }

  .content :global(pre) {
    background-color: #f9f9f9;
    box-shadow: inset 1px 1px 5px rgba(0, 0, 0, 0.05);
    padding: 0.5em;
    border-radius: 2px;
    overflow-x: auto;
  }

  .content :global(pre) :global(code) {
    background-color: transparent;
    padding: 0;
  }

  .content :global(ul) {
    line-height: 1.5;
  }

  .content :global(li) {
    margin: 0 0 0.5em 0;
  }

  .content :global(img) {
    max-width: 100%;
  }

  .spacer {
    margin: 3rem 0;
  }
</style>

<svelte:head>
  <title>{story.title}</title>
</svelte:head>

<h1>{story.title}</h1>
<StoryInfo {story} />

<div class="content">
  {@html story.text}
</div>

{#if hasComments}
  <hr class="spacer" />
  <h2 id="comments">Comments</h2>
  {#if related.length}
    <h3>
      Other discussions:
      {#each related as r}
        {#if r.num_comments}
          <a href="/{r.id}#comments" rel="prefetch">{r.source}</a>
        {/if}
      {/each}
    </h3>
  {/if}
  {#if story.comments.length}
    <div class="comments">
      {#each story.comments as comment}
        <Comment {story} {comment} />
      {/each}
    </div>
  {/if}
{/if}
