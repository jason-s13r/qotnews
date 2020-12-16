<script>
  import fromUnixTime from "date-fns/fromUnixTime";
  import formatDistanceToNow from "date-fns/formatDistanceToNow";
  export let date;
  $: d = fromUnixTime(date);
  $: datetime = d.toISOString();
  $: title = d.toLocaleString();
  $: dateString = formatDistanceToNow(d, { addSuffix: true });
</script>

<time {datetime} {title}>{dateString}</time>
