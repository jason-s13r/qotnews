<script>
  import Nav from "../components/Nav.svelte";
  import DarkMode from "../components/DarkMode.svelte";
  export let segment;
</script>

<style>
  main {
    position: relative;
    max-width: 64rem;
    padding: 0.5rem;
    margin: 0 auto;
    box-sizing: border-box;
  }
</style>

<Nav {segment} />

<main>
  <slot {segment} />
</main>

<DarkMode />
