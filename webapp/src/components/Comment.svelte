<script>
  import Time from "../components/Time.svelte";

  export let story;
  export let comment;
  export let showComments = true;

  let author = (comment.author || "").replace(" ", "");
  let id = `${author}-${comment.date}`;

  function toggleComments() {
    showComments = !showComments;
  }
</script>

<style>
  .comment {
    margin: 0.5rem 0;
  }
  .comment:not(:first-of-type) {
    margin: 0.5rem 0;
    border-top: solid 1px #ddd;
    padding: 0.5rem 0 0;
  }
  :global(.dark-mode) .comment:not(:first-of-type) {
    border-top-color: #222;
  }
  .comment-info {
    color: #222;
  }
  :global(.dark-mode) .comment-info {
    color: #ddd;
  }
  .comment-author {
    font-weight: 600;
    padding: 0 0.4em 0.2em;
    border-radius: 0.5em;
  }
  .comment-author {
    background: #f1f1f1;
    color: #000;
  }
  :global(.dark-mode) .comment-author,
  .comment-author.is-op {
    background: #333;
    color: #fff;
  }
  :global(.dark-mode) .comment-author.is-op {
    background: #f1f1f1;
    color: #000;
  }
  .comment-text {
    padding: 0 0.5rem;
  }
  .comment-text.is-collapsed {
    height: 3rem;
    overflow: hidden;
    color: #888;
  }
  .comment-children {
    margin-left: 0.5rem;
    padding-left: 0.5rem;
    border-left: solid 1px #000;
  }
  :global(.dark-mode) .comment-children {
    border-left-color: #fff;
  }
  .toggle-children {
    background: none;
    border: none;
    padding: 0 0.25rem;
    color: inherit;
    cursor: pointer;
  }
  .time-link {
    text-decoration: none;
  }
  .time-link:hover {
    text-decoration: underline;
  }
  .is-lighter {
    color: #888;
  }
</style>

<article class="comment" id="comment-{id}">
  <header class="comment-info">
    <span
      class={comment.author === story.author ? 'comment-author is-op' : 'comment-author'}>{comment.author || '[Deleted]'}</span>
    <a class="time-link" href="{story.id}#comment-{id}">
      <Time date={comment.date} />
    </a>
    {#if comment.comments.length}
      <button
        class="toggle-children"
        on:click={toggleComments}>{#if showComments}
          [&ndash;]
        {:else}[+]{/if}</button>
    {/if}
  </header>

  <section class={showComments ? 'comment-text' : 'comment-text is-collapsed'}>
    {@html comment.text}
  </section>

  {#if !showComments}
    <div class="comment-children">
      <button
        class="toggle-children is-lighter"
        on:click={toggleComments}>[expand]</button>
    </div>
  {/if}

  {#if showComments && comment.comments.length}
    <footer class="comment-children">
      {#each comment.comments as child}
        <svelte:self {story} comment={child} />
      {/each}
    </footer>
  {/if}
</article>
