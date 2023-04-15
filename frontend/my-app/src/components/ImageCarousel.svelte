<script>
	import { onMount, onDestroy, afterUpdate } from 'svelte';
	import KeenSlider from 'keen-slider';
	import 'keen-slider/keen-slider.min.css';
	// TODO: Send the image list into the Carousel for display.
	export let imageList;

	let slider;
	let keenSlider;

	function prevSlide() {
		keenSlider.prev();
	}

	function nextSlide() {
		keenSlider.next();
	}

	onMount(() => {
		keenSlider = new KeenSlider(slider, {
			loop: true,
			slidesPerView: 1,
			centered: true,
			duration: 3000,
			mode: 'free-snap',
			spacing: 0,
			autoplay: 3000,
			breakpoints: {
				'(min-width: 768px)': {
					slidesPerView: 1,
					mode: 'free-snap'
				}
			}
		});
		console.log(imageList)
	});

	onDestroy(() => {
		if (keenSlider) keenSlider.destroy();
	});
</script>

{#if imageList}
	<div bind:this={slider} class="keen-slider w-full h-full md:h-full overflow-hidden">
		{#each imageList as image}
			<div class="keen-slider__slide w-full h-full">
				<img src={`data:image/jpeg;base64,${image}`} alt={`Image shown lol`} class="w-full h-full object-contain" />
			</div>
		{/each}
		<!-- Add left and right arrow elements -->
		<button
			class="absolute left-0 top-1/2 transform -translate-y-1/2 z-10 bg-white bg-opacity-75 p-2 rounded-r-md focus:outline-none"
			on:click={prevSlide}
		>
			&#8592;
		</button>
		<button
			class="absolute right-0 top-1/2 transform -translate-y-1/2 z-10 bg-white bg-opacity-75 p-2 rounded-l-md focus:outline-none"
			on:click={nextSlide}
		>
			&#8594;
		</button>
	</div>
{/if}
