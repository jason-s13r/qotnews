<script>
  import { debounce } from 'lodash';
  import { goto, prefetch } from "@sapper/app";
  import { stores } from "@sapper/app";

  export let segment;
  const { page } = stores();

  let q;
  let search;

  page.subscribe((value) => {
    q = value.query.q || "";
  });

 let handleSearch = debounce(_handleSearch);

  async function _handleSearch(event) {
    const url = `/search?q=${event.target.value}`;
    await prefetch(url);
    await goto(url);
  }
</script>

<style>
  nav {
    border-bottom: 1px solid rgba(255, 62, 0, 0.1);
    font-weight: 300;
    padding: 0 1em;
  }

  ul {
    margin: 0;
    padding: 0;
  }

  /* clearfix */
  ul::after {
    content: "";
    display: block;
    clear: both;
  }

  li {
    display: block;
    float: left;
  }

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

  a {
    text-decoration: none;
    padding: 1em 0.5em;
    display: block;
  }

  input {
    line-height: 2;
    margin: 1em;
    vertical-align: middle;
  }
</style>

<nav>
  <ul>
    <li>
      <a
        aria-current={segment === undefined ? 'page' : undefined}
        rel="prefetch"
        href=".">News</a>
    </li>
    <li>
      <form action="/search" method="GET" rel="prefetch">
        <input
          id="search"
          bind:this={search}
          type="text"
          name="q"
          value={q}
          placeholder="Search..."
          on:keypress={handleSearch} />
      </form>
    </li>
  </ul>
</nav>
