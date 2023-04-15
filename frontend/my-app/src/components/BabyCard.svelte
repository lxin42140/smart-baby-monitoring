<!-- BabyCard.svelte -->
<script>
	export let character;
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	function handleCardClick() {
		dispatch('cardClicked', character);
	}
	// There needs to be a function here to do something when on:click is used.
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
	class="bg-white rounded-lg shadow-md p-4 w-60 cursor-pointer transition duration-300 ease-in-out transform hover:-translate-y-1 hover:scale-105"
	on:click={handleCardClick}
>
	<img
		class="rounded-full w-32 h-32 mx-auto mb-4"
		src={`data:image/jpeg;base64,${character.image}`}
		alt={character.first_name}
	/>
	<h3 class="text-lg font-semibold mb-2">{character.first_name} {character.last_name}</h3>
	<p class="text-gray-500 text-sm">Age: {character.age}</p>
	<p class="text-gray-500 text-sm">Height: {character.height}cm</p>
	<p class="text-gray-500 text-sm">Weight: {character.weight}kg</p>
</div>
