<script>
	import { onMount, onDestroy } from 'svelte';
	import { tweened } from 'svelte/motion';
	import Tailwind from '../routes/Tailwind.svelte';
	// Define an array of colors to animate through
	const colors = ['bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500'];

	// Use a tweened store to animate the color index
	const colorIndex = tweened(0, {
		duration: 1000, // Duration of each color animation
		easing: (t) => t * t // Easing function for the color animation
	});

	let colorClass = colors[0]; // Initial color class

	const nextColor = () => {
		// Move to the next color in the array
		let index = (colorIndex + 1) % colors.length;
		colorIndex.set(index);
		colorClass = colors[index];
	};

	let intervalId;

	onMount(() => {
		// Start the color animation loop
		intervalId = setInterval(nextColor, 1000);
	});

	onDestroy(() => {
		// Stop the color animation loop when the component is destroyed
		clearInterval(intervalId);
	});
</script>

<div class="text-4xl font-bold">
	<!-- Bind the color class to the tweened store -->
	<span class="rounded-md p-2 text-white" class:bind={colorClass}> SlumberWatch </span>
</div>
