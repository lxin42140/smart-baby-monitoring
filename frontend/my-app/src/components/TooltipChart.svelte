<script>
	export let text = '';
    import Icon from "@iconify/svelte"
	let showTooltip = false;
</script>

<button
	class="absolute top-1 right-1 text-gray-500 hover:text-gray-900 focus:outline-none"
	aria-label="Information"
	on:mouseenter={() => (showTooltip = true)}
	on:mouseleave={() => (showTooltip = false)}
>
	<Icon icon="mdi:information-slab-box" width=24 height=24/>
</button>

{#if showTooltip}
	<div
		class="absolute top-full mt-2 w-64 p-3 bg-white text-sm text-gray-700 border border-gray-300 rounded-md shadow-lg z-50"
	>
		<p>{text}</p>
	</div>
{/if}
