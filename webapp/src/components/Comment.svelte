<script>
  import fromUnixTime from "date-fns/fromUnixTime";
  import formatDistanceToNow from "date-fns/formatDistanceToNow";
  export let story;
  export let comment;
  export let showComments = true;
  export let dateString = formatDistanceToNow(fromUnixTime(comment.date), {
    addSuffix: true,
  });
  const author = comment.author.replace(" ", "");
  export let id = `${author}-${comment.date}`;

  export function toggleComments() {
    showComments = !showComments;
  }
</script>

<style>
  .comment-author {
  }
  .comment-text {
    padding: 0 0.5rem;
    color: #333;
  }
  .comment-children {
    margin-left: 1rem;
    padding-left: 1rem;
    border-left: solid 1px #000;
  }
  .link-button {
    background: none;
    border: none;
    padding: 0 0.1rem;
    color: inherit;
    cursor: pointer;
  }
</style>

<div class="comment" id="comment-{id}">
  <div class="comment-author">
    {comment.author}
    |
    <a href="{story.id}#comment-{id}">{dateString}</a>
    {#if comment.comments.length}
      <button
        class="link-button"
        on:click={toggleComments}>[{showComments ? '-' : '+'}]</button>
    {/if}
  </div>
  <div class="comment-text">
    {@html comment.text}
  </div>
  {#if showComments && comment.comments.length}
    <div class="comment-children">
      {#each comment.comments as child}
        <svelte:self {story} comment={child} />
      {/each}
    </div>
  {/if}
</div>
