<script context="module">

  username = localStorage.getItem('username');

  export async function load({ page, fetch, username }) {
    if (!username) {
      return {
        status: 303,
        redirect: '/login'
      };
    }

    return {
      props: {}
    };
  }
</script>

<slot />