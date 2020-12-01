<script>
  import debounce from "lodash/debounce";
  import { goto, prefetch, stores } from "@sapper/app";
  export let segment;

  const { page } = stores();

  let search;

  let handleSearch = debounce(_handleSearch, 300, {
    trailing: true,
    leading: false,
  });

  page.subscribe((page) => {
    setTimeout(() => {
      if (segment === "search") {
        search && search.focus();
      }
    }, 0);
  });

  async function _handleSearch(event) {
    const url = `/search?q=${event.target.value}`;
    await prefetch(url);
    await goto(url);
  }
</script>

<style>
  .has-highlight,
  [aria-current] {
    position: relative;
    display: inline-block;
  }

  .has-highlight::after,
  [aria-current]::after {
    position: absolute;
    content: "";
    width: calc(100% - 1em);
    height: 2px;
    background-color: rgb(255, 62, 0);
    display: block;
    bottom: -1px;
  }

  .navigation {
    border-bottom: 1px solid rgba(255, 62, 0, 0.1);
    font-weight: 300;
    padding: 0;
  }

  .navigation-container {
    margin: 0 auto;
    padding: 0;
    max-width: 64rem;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
  .navigation-container > * {
    vertical-align: middle;
  }
  .navigation-list {
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: row;
  }

  .navigation-item {
    list-style: none;
  }
  .navigation-text,
  .navigation-link {
    text-decoration: none;
    padding: 1em 0.5em;
    display: block;
  }
  .navigation-input {
    line-height: 2;
    margin: 1em;
    vertical-align: middle;
    width: 15rem;
  }
</style>

<nav class="navigation">
  <div class="navigation-container">
    <ul class="navigation-list" role="menubar">
      <li class="navigation-item">
        <a
          class="navigation-link"
          aria-current={segment === undefined ? 'page' : undefined}
          rel="prefetch"
          href=".">News</a>
      </li>
    </ul>
    <form action="/search" method="GET" rel="prefetch" role="search">
      <input
        class="navigation-input"
        id="search"
        bind:this={search}
        type="text"
        name="q"
        value={$page.query.q || ''}
        placeholder="Search..."
        on:keypress={handleSearch} />
    </form>
    <ul class="navigation-list">
      <li class="navigation-item">
        <span
          class="navigation-text {segment !== undefined ? 'has-highlight' : undefined}">Qot.</span>
      </li>
    </ul>
  </div>
</nav>
