<script>
  import DOMPurify from "dompurify";
  import { onMount } from "svelte";

  export let html;
  let purify;

  onMount(() => {
    purify = (html) => DOMPurify.sanitize(html);
  });
</script>

{#if purify}
  {@html html}
{:else}{html}{/if}
