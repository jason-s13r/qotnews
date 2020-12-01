<script>
  import { stores } from "@sapper/app";
  export let href;
  export let search;
  export let count;

  const { page } = stores();

  let skip = 0;
  let limit = 20;
  let prevLink = "";
  let nextLink = "";

  page.subscribe((p) => {
    count = Number(count);
    skip = Number(p.query.skip) || 0;
    limit = Number(p.query.limit) || 20;

    let previous = new URLSearchParams(search || "");
    let next = new URLSearchParams(search || "");

    previous.append("skip", skip - Math.min(skip, limit));
    previous.append("limit", limit);

    next.append("skip", skip + limit);
    next.append("limit", limit);

    prevLink = href + "?" + previous.toString();
    nextLink = href + "?" + next.toString();
  });
</script>

<style>
  .pagination {
    margin: 3rem 0;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
  .pagination-link.is-next {
    margin-left: auto;
  }
</style>

<div class="pagination">
  {#if skip > 0}
    <a
      class="pagination-link is-prev"
      href={prevLink}
      rel="prefetch">Previous</a>
  {/if}
  {#if count >= limit}
    <a class="pagination-link is-next" href={nextLink} rel="prefetch">Next</a>
  {/if}
</div>
