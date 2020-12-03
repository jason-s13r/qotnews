<script>
  export let story;

  let host = new URL(story.url || story.link).hostname.replace(/^www\./, "");
</script>

<style>
  ul {
    margin: 0;
    padding: 0;
  }
  li {
    display: inline-block;
    list-style-type: circle;
  }
  li:not(:first-of-type)::before {
    content: " | ";
  }
</style>

<ul>
  {#if story.url}
    <li>source: <a class="article-source" href={story.url}>{host}</a></li>
  {/if}
  {#if story.scraper && story.scraper_link}
    <li>scraper: <a href={story.scraper_link}>{story.scraper}</a></li>
  {:else if story.scraper}
    <li>scraper: {story.scraper}</li>
  {/if}
</ul>
