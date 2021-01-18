<script context="module">
  export async function preload(page) {
    const { skip, limit } = {
      skip: page.query.skip || 0,
      limit: page.query.limit || 20,
    };
    const res = await this.fetch(`index.json?skip=${skip}&limit=${limit}`);
    const data = await res.json();

    if (res.status === 200) {
      return { stories: data.stories, skip, limit };
    } else {
      this.error(res.status, data.message);
    }
  }
</script>

<script>
  import StoryList from "../components/StoryList.svelte";
  import Pagination from "../components/Pagination.svelte";

  export let stories;
</script>

<svelte:head>
  <title>QotNews</title>
  <meta property="og:title" content="QotNews" />
  <meta property="og:type" content="website" />
</svelte:head>

<StoryList {stories}>
  <Pagination href="/[skip]" inRoute={true} count={stories.length} />
</StoryList>
