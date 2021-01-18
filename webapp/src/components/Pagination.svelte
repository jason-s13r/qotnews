<script>
  import { stores } from "@sapper/app";
  export let href;
  export let search;
  export let count;
  export let inRoute;

  const { page } = stores();

  let skip = 0;
  let limit = 20;
  let prevLink = "";
  let nextLink = "";

  page.subscribe((p) => {
    count = Number(count);
    skip = Number({ ...p.params, ...p.query }.skip) || 0;
    limit = Number(p.query.limit) || 20;

    let previous = new URLSearchParams(search || "");
    let next = new URLSearchParams(search || "");

    previous.append("skip", skip - Math.min(skip, limit));
    previous.append("limit", limit);

    next.append("skip", skip + limit);
    next.append("limit", limit);

    prevLink = nextLink = href;

    if (inRoute) {
      prevLink = squareRoute(href, "skip", previous);
      prevLink = squareRoute(prevLink, "limit", previous);

      nextLink = squareRoute(href, "skip", next);
      nextLink = squareRoute(nextLink, "limit", next);
    }

    if (previous.toString()) {
      prevLink += "?" + previous.toString();
    }
    if (next.toString()) {
      nextLink += "?" + next.toString();
    }
  });

  function squareRoute(url, key, params) {
    const output = url.split(`[${key}]`).join(params.get(key));
    if (output !== url) {
      params.delete(key);
    }
    return output;
  }
</script>

<div class="pagination">
  {#if skip > 0}
    <a class="pagination-link is-prev" href={prevLink} rel="prefetch"
      >&larr; Previous</a
    >
  {/if}
  {#if count >= limit}
    <a class="pagination-link is-next" href={nextLink} rel="prefetch"
      >Next &rarr;</a
    >
  {/if}
</div>

<style>
  .pagination {
    margin: 3rem 0;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .pagination-link {
    font-size: 1.5rem;
    text-decoration: none;
  }
  .pagination-link:hover {
    text-decoration: underline;
  }
  .pagination-link.is-next {
    margin-left: auto;
  }
</style>
