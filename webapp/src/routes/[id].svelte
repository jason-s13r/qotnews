<script context="module">
  import sources from "../sources.json";

  const key = Object.keys(sources).find(
    (k) => sources[k].primary && sources[k].enabled
  );
  export async function preload({ params }) {
    return this.redirect(302, `${key}/${params.id}`);
  }
</script>
