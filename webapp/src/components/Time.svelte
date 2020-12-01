<script>
  import fromUnixTime from "date-fns/fromUnixTime";
  import formatDistanceToNow from "date-fns/formatDistanceToNow";
  export let date;
  let d = fromUnixTime(date);
  let datetime = d.toISOString();
  let title = d.toLocaleString();
  let dateString = formatDistanceToNow(d, { addSuffix: true });
</script>

<time {datetime} {title}>{dateString}</time>
