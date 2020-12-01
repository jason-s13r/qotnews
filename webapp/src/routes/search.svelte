<script context="module">
  export async function preload(page) {
    const { skip, limit, q } = {
      skip: page.query.skip || 0,
      limit: page.query.limit || 20,
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
  import StoryList from "../components/StoryList.svelte";
  import Pagination from "../components/Pagination.svelte";

  export let stories;

  const { page } = stores();
</script>

<svelte:head>
  <title>QotNews</title>
  <meta property="og:title" content="QotNews" />
  <meta property="og:type" content="website" />
</svelte:head>

<StoryList {stories}>
  <Pagination
    href="/search"
    search="q={$page.query.q}"
    count={stories.length} />
</StoryList>
