<script>
  import DOMPurify from "dompurify";
  import { onMount } from "svelte";

  export let html;
  export let text;
  let purify;

  onMount(() => {
    purify = (html) => DOMPurify.sanitize(html);
  });
</script>

{#if purify}
  {@html html}
{:else if text}{text}{/if}
