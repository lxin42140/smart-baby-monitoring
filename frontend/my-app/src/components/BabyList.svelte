<!-- BabyList.svelte -->
<script>
	import BabyCard from './BabyCard.svelte';
	import { slide } from 'svelte/transition';
	import { createNewBaby, getAllBabies } from '../api/baby';
	import Icon from '@iconify/svelte';
	import { createEventDispatcher, onMount } from 'svelte';
	import BabyModal from './modal/BabyModal.svelte';

	export let characters = [];
	export let retrieveBabies;
	let deviceName;
	let openCreateBabyModal = false;
	let openEditBabyModal = false;

	const dispatch = createEventDispatcher();

	let isOpen = true;
	let newCharacter = {
		first_name: '',
		last_name: '',
		age: '',
		height: '',
		weight: '',
		devicename: '',
		image: ''
	};
	console.log(characters)

	const onCloseModal = () => {
		Object.keys(newCharacter).map((key) => {
			newCharacter[key] = '';
		});
		openCreateBabyModal = false;
	};
	const onCloseEditBabyModal = () => {
		deviceName = '';
		openEditBabyModal = false;
	};

	function toggleCharacterList() {
		isOpen = !isOpen;
	}

	function handleBabyCardClick(event) {
		const baby = event.detail;
		console.log('Baby card clicked:', baby);
		deviceName = baby.devicename;
		openEditBabyModal = true;
		// Perform any action you want with the baby data here
		dispatch('babyCardClicked', baby);
	}
</script>

<section class="banner-list">
	<div class="container mx-auto px-4 py-8">
		<div class="flex items-center justify-between mb-4">
			<div class="row column-center">
				<h1 class="text-3xl font-mono text-gray-200">Baby List</h1>
				<button
					on:click={() => {
						openCreateBabyModal = true;
					}}
					class="add-baby-button transform transition duration-500 hover:scale-105 hover:-translate-y-1 hover:shadow-l"
					>Add baby</button
				>
			</div>
			<button
				class="w-8 h-8 bg-white shadow-md rounded-full flex items-center justify-center focus:outline-none"
				on:click={toggleCharacterList}
			>
				<Icon
					icon="material-symbols:arrow-drop-down"
					width="52"
					height="52"
					rotate={isOpen ? 2 : 0}
				/>
			</button>
		</div>
		{#if isOpen}
			<div transition:slide={{ duration: 300 }}>
				{#if characters.length === 0}
					<div>
						<h1 class="font-mono text-gray-400 transition-colors">
							You do not have any babies added to the system currently. Add a new baby to view them.
						</h1>
					</div>
				{:else}
					<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
						{#each characters as character}
							<BabyCard {character} on:cardClicked={handleBabyCardClick} />
						{/each}
					</div>
				{/if}
			</div>
		{/if}

		<BabyModal
			isCreate={true}
			character={newCharacter}
			{openCreateBabyModal}
			{onCloseModal}
			{retrieveBabies}
		/>
		{#if deviceName}
			<BabyModal
				isCreate={false}
				character={characters.filter((x) => x.devicename === deviceName)[0]}
				openCreateBabyModal={openEditBabyModal}
				onCloseModal={onCloseEditBabyModal}
				{retrieveBabies}
			/>
		{/if}
	</div>
</section>

<style>
	.banner-list {
		background-position: center left;
		background-color: #293B58;
	}

	.add-baby-button {
		cursor: pointer;
		font-size: 1rem;
		padding: 0.5rem;
		background-color: #0056b3;
		color: #fff;
		border: none;
		border-radius: 4px;
		transition: background-color 0.3s;
		margin: 10px;
	}
</style>
