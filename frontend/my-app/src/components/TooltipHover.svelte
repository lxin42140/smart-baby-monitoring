<script>
	export let title = '';
	export let delay = 1000;
	let isHovered = false;
	let x;
	let y;
	let timeout;
	
	function mouseOver(event) {
		timeout = setTimeout(() => {
			isHovered = true;
			x = event.pageX + 5;
			y = event.pageY + 5;
		}, delay);
	}
	function mouseMove(event) {
		x = event.pageX + 5;
		y = event.pageY + 5;
	}
	function mouseLeave() {
		clearTimeout(timeout);
		isHovered = false;
	}
</script>

<div
	on:mouseover={mouseOver}
	on:mouseleave={mouseLeave}
	on:mousemove={mouseMove}>
	<slot />
</div>

{#if isHovered}
	<div style="top: {y}px; left: {x}px;" class="tooltip">{title}</div>
{/if}

<style>
	.tooltip {
		border: 1px solid #ddd;
		box-shadow: 1px 1px 1px #ddd;
		background: white;
		border-radius: 4px;
		padding: 4px;
		position: absolute;
    z-index: 9999;
	}
</style>
