<script>
  import debounce from "lodash/debounce";
  import { goto, prefetch, stores } from "@sapper/app";
  export let segment;

  const { page } = stores();

  let search;
  let isSearching;

  let __handleSearch = debounce(_handleSearch, 300, {
    trailing: true,
    leading: false,
  });
  let handleSearch = (e) => {
    isSearching = true;
    __handleSearch(e);
  };

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
    isSearching = false;
  }
</script>

<style>
  [aria-current] {
    position: relative;
    display: inline-block;
  }

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

  /* @media (max-device-width: 480px) {
    .navigation-container {
      justify-content: space-evenly;
    }
  } */
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
  .navigation-link {
    text-decoration: none;
    padding: 1em 0.5em;
    display: block;
  }
  .navigation-input {
    line-height: 2;
    vertical-align: middle;
    width: 30rem;
    max-width: 45vw;
    font-size: 1.1rem;
    padding: 0.25em 0.5em;
    margin: 0.25em 0.5em;
    border-radius: 5px;
    border: solid 1px #aaa;
  }
  input:focus {
    box-shadow: 0 0 0.25rem rgba(0, 0, 0, 0.25);
  }

  .is-searching {
    padding-right: 0.5rem;
    background-image: url(/svg-loaders/black/grid.svg);
    background-size: 1.2em 1.2em;
    background-position: right 0.5em center;
    background-repeat: no-repeat;
  }
</style>

<svelte:head>
  <link rel="preload" href="/svg-loaders/black/grid.svg" as="image" />
</svelte:head>

<nav class="navigation">
  <div class="navigation-container">
    <ul class="navigation-list" role="menu">
      <li class="navigation-item">
        <a
          class="navigation-link"
          aria-current={segment === undefined ? 'page' : undefined}
          rel="prefetch"
          href=".">
          {#if [undefined, 'submit'].includes(segment)}
            Qot. news
          {:else}&larr; News feed{/if}
        </a>
      </li>
      {#if [undefined, 'submit'].includes(segment)}
        <li class="navigation-item">
          <a
            class="navigation-link"
            aria-current={segment === 'submit' ? 'page' : undefined}
            rel="prefetch"
            href="/submit">
            Submit
          </a>
        </li>
      {/if}
    </ul>
    <form action="/search" method="GET" rel="prefetch" role="search">
      <input
        class="navigation-input {(isSearching && 'is-searching') || ''}"
        id="search"
        bind:this={search}
        type="text"
        name="q"
        value={$page.query.q || ''}
        placeholder="Search..."
        on:keypress={handleSearch} />
    </form>
  </div>
</nav>
