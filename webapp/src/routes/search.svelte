<script context="module">
  export async function preload(page) {
    const { skip, limit, q } = {
      skip: page.query.skip || 0,
      limit: page.query.query || 20,
      q: page.query.q || "",
    };
    const res = await this.fetch(
      `search.json?q=${q}&skip=${skip}&limit=${limit}`
    );
    const data = await res.json();

    if (res.status === 200) {
      return { stories: data.results, skip, limit };
    } else {
      this.error(res.status, data.message);
    }
  }
</script>

<script>
  import { stores } from "@sapper/app";
  import { getLogoUrl } from "../utils/logos.js";
  import StoryInfo from "../components/StoryInfo.svelte";

  export let stories;
  export let skip;
  export let limit;
  export let q;

  const { page } = stores();

  page.subscribe((value) => {
    skip = value.query.skip || 0;
    limit = value.query.limit || 20;
    q = value.query.query || "";
  });
</script>

<style>
  article {
    margin: 0.5rem 0;
  }

  .pagination {
    margin: 3rem 0;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
  .pagination-link {
    /* border: solid 1px #aaa;
    border-radius: 0;
    background: #f1f1f1;
    border-radius: 5px;
    margin: 0.5rem;
    padding: 0.5rem;
    text-decoration: none; */
  }
  .pagination-link.is-right {
    margin-left: auto;
  }
</style>

<svelte:head>
  <title>QotNews</title>
  <meta property="og:title" content="QotNews" />
  <meta property="og:type" content="website" />
</svelte:head>

<section>
  {#each stories as story}
    <article>
      <header>
        <img
          src={getLogoUrl(story)}
          alt="logo"
          style="height: 1rem; width: 1rem;" />
        <a rel="prefetch" href="/{story.id}">{story.title}</a>
        (<a
          href={story.url || story.link}>{new URL(story.url || story.link).hostname.replace(/^www\./, '')}</a>)
      </header>
      <section>
        <StoryInfo {story} />
      </section>
    </article>
  {/each}
</section>

<div class="pagination">
  {#if Number(skip) > 0}
    <a
      class="pagination-link is-left"
      href="?skip={Number(skip) - Math.min(Number(skip), Number(limit))}&limit={limit}"
      rel="prefetch">Previous</a>
  {/if}
  {#if stories.length == Number(limit)}
    <a
      class="pagination-link is-right"
      href="?skip={Number(skip) + Number(limit)}&limit={limit}"
      rel="prefetch">Next</a>
  {/if}
</div>
