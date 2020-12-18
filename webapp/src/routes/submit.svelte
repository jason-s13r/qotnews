<script>
  import { onMount } from "svelte";
  import { goto, prefetch } from "@sapper/app";

  let input;
  let handleSubmit;
  let hasError;
  let isLoading;

  onMount(() => {
    setTimeout(() => {
      input && input.focus();
    }, 0);
    handleSubmit = async () => {
      isLoading = true;
      hasError = false;
      const url = input.value;
      const response = await fetch(`submit.json`, {
        headers: { "Content-Type": "application/json" },
        method: "POST",
        body: JSON.stringify({ url }),
      });
      if (!response.ok) {
        hasError = true;
        isLoading = false;
        return;
      }
      const { nid } = await response.json();
      await prefetch(`/${nid}`);
      await goto(`/${nid}`);
    };
  });
</script>

<style>
  section {
    max-width: 45rem;
    margin: 5rem auto 0;
  }
  form {
    text-align: center;
    width: 95%;
    border: solid 1px #aaa;
    margin: 3.5rem auto;
    border-radius: 5px;
    overflow: hidden;
    display: flex;
    flex-direction: row;
  }

  form:focus-within {
    box-shadow: 0 0 0.25rem rgba(0, 0, 0, 0.25);
  }
  form:has(input:focus) {
    box-shadow: inset 0 0 0.2rem rgba(0, 0, 0, 0.2);
  }
  :global(.dark-mode) form {
    border-color: #555;
  }
  :global(.dark-mode) form:focus-within {
    box-shadow: 0 0 0.25rem rgba(255, 255, 255, 0.25);
  }
  :global(.dark-mode) form:has(input:focus) {
    box-shadow: inset 0 0 0.2rem rgba(255, 255, 255, 0.2);
  }

  input {
    width: 85%;
    box-sizing: border-box;
    padding: 0.5rem;
    margin: 0;
    font-size: 1.25rem;
    line-height: 1.5;
    border: none;
    border-radius: 0;
    background: #fff;
    vertical-align: middle;
  }
  :global(.dark-mode) input {
    color: #fff;
    background-color: #000;
  }

  button {
    width: 15%;
    box-sizing: border-box;
    padding: 0.5rem;
    margin: 0;
    font-size: 1.25rem;
    line-height: 1.5;
    border: none;
    border-left: solid 1px #aaa;
    border-radius: 0;
    background: #f1f1f1;
    vertical-align: middle;
  }
  :global(.dark-mode) button {
    color: #fff;
    border-left-color: #555;
    background: #0e0e0e;
  }

  :global(.dark-mode) .loading {
    filter: invert(1);
  }

  .loading,
  .is-loading form,
  .is-loading .error {
    display: none;
  }

  .is-loading .loading {
    display: block;
    margin: 3.5rem auto 0;
  }

  .error {
    display: none;
  }

  .has-error .error {
    box-sizing: border-box;
    height: 3rem;
    padding: 0;
    margin: 0;
    color: darkred;
    display: block;
  }
  .has-error form {
    margin-top: 5rem;
  }
</style>

<svelte:head>
  <title>QotNews</title>
  <meta property="og:title" content="QotNews" />
  <meta property="og:type" content="website" />
  <link rel="preload" href="/loading.svg" as="image" />
</svelte:head>

<section class="{isLoading ? 'is-loading' : ''} {hasError ? 'has-error' : ''}">
  <img
    class="loading"
    src="/loading.svg"
    alt="loading..."
    width="200"
    height="200" />

  <form
    action="submit.json"
    method="POST"
    on:submit|preventDefault={handleSubmit}
    autocomplete="off">
    <input
      type="text"
      name="url"
      placeholder="Enter article link"
      pattern="^https?:\/\/(www\.)?.*"
      value=""
      bind:this={input}
      required />
    <button value="true" name="redirect" type="submit">Go</button>
  </form>

  <p class="error">Something went wrong.</p>
</section>
