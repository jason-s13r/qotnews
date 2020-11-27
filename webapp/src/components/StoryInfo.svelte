<script>
  import fromUnixTime from "date-fns/fromUnixTime";
  import formatDistanceToNow from "date-fns/formatDistanceToNow";
  export let story;
  export let dateString = formatDistanceToNow(fromUnixTime(story.date), {
    addSuffix: true,
  });
</script>

<div class="info">
  <time
    datetime={fromUnixTime(story.date).toISOString()}
    title={fromUnixTime(story.date)}>{dateString}</time>
  {#if story.author && story.author_link}
    by
    <a href={story.author_link}>{story.author}</a>
  {:else if story.author}by {story.author}{/if}
  on
  <a href={story.url}>{story.source}</a>
  {#if story.score}&bull; {story.score} points{/if}
  {#if story.num_comments}
    &bull;
    <a rel="prefetch" href="/{story.id}#comments">{story.num_comments}
      comments</a>
  {/if}
</div>
