<script>
	import { getServerConfig } from '../../api/config';
	import { createNewBaby, editBaby } from '../../api/baby';

	export let isCreate; //true if creating, false if editing
	export let character;
	export let openCreateBabyModal;
	export let retrieveBabies;
	export let onCloseModal;

	let uploadImageRef;
	let requireImageError = false;
	let createBabyError = false;
	let fogNames = [];
	let hasImageChanged = false; //prevent re-decoding and encoding in BE

	const getTriggerAlarmOptions = async () => {
		const allAlarmOptions = await getServerConfig();
		if (allAlarmOptions !== null) {
			console.log(fogNames);
			const arr = [...allAlarmOptions.fog_name];
			arr.splice(arr.length - 1, 1); // to remove 'all'
			fogNames = arr;
		}
	};

	getTriggerAlarmOptions();

	const convertBase64 = (file) => {
		return new Promise((resolve, reject) => {
			const fileReader = new FileReader();
			fileReader.readAsDataURL(file);

			fileReader.onload = () => {
				resolve(fileReader.result);
			};

			fileReader.onerror = (error) => {
				reject(error);
			};
		});
	};

	const uploadImage = async (event) => {
		hasImageChanged = true;
		const file = event.target.files[0];
		const base64 = await convertBase64(file);
		character.image = base64.split(',')[1];
	};

	const handleSubmit = async () => {
		requireImageError = false;
		createBabyError = false;
		if (character.image?.length === 0) requireImageError = true;
		else {
			let res;
			if (isCreate) {
				res = await createNewBaby(character);
			} else {
				if (!hasImageChanged) delete character['image'];
				res = await editBaby(character);
			}
			if (res) {
				await retrieveBabies();
				onCloseModal();
			} else {
				createBabyError = true;
			}

			hasImageChanged = false;
		}
	};
</script>

<div
	class={`fixed inset-0 z-50 bg-black bg-opacity-50 flex justify-center items-center ${
		openCreateBabyModal ? '' : 'hidden'
	}`}
>
	<div class="modal bg-gray-100 w-full max-w-lg p-6 mx-4 md:mx-0 rounded-md shadow-lg">
		{#if isCreate}
			<h3 class="text-xl font-mono mb-2">Create baby record</h3>
		{:else}
			<h3 class="text-xl font-mono mb-2">Edit baby record</h3>
		{/if}
		<hr class="border-t border-gray-300 mb-0" />
		<form on:submit|preventDefault={handleSubmit} class="space-y-0 mt-0 pt-0">
			<div class="mb-4 mt-0">
				<label for="firstname" class="block text-sm font-mono font-medium text-gray-700"
					>First name:</label
				>
				<input
					type="text"
					id="firstname"
					bind:value={character.first_name}
					required
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
				/>
			</div>

			<div class="mb-4">
				<label for="lastname" class="block text-sm font-mono font-medium text-gray-700"
					>Last name:</label
				>
				<input
					type="text"
					id="lastname"
					bind:value={character.last_name}
					required
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
				/>
			</div>

			<div class="mb-4">
				<label for="age" class="block text-sm font-medium font-mono text-gray-700">Age:</label>
				<input
					type="number"
					id="age"
					bind:value={character.age}
					required
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
				/>
			</div>

			<div class="mb-4">
				<label for="height" class="block text-sm font-medium font-mono text-gray-700"
					>Height (cm):</label
				>
				<input
					type="number"
					id="height"
					bind:value={character.height}
					required
					step="0.01"
					pattern="^\d*(\.\d{(0, 2)})?$"
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
				/>
			</div>

			<div class="mb-4">
				<label for="weight" class="block text-sm font-medium font-mono text-gray-700"
					>Weight (kg):</label
				>
				<input
					type="number"
					id="weight"
					bind:value={character.weight}
					required
					step="0.01"
					pattern="^\d*(\.\d{(0, 2)})?$"
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
				/>
			</div>

			<div class="mb-4">
				<label for="devicename" class="block text-sm font-medium font-mono text-gray-700"
					>Device name:</label
				>
				<select
					class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
					id="devicename"
					bind:value={character.devicename}
				>
					{#each fogNames as name}
						<option value={name}>{name}</option>
					{/each}
				</select>
			</div>

			<div class="mb-4">
				<label for="image" class="block text-sm font-mono font-medium text-gray-700"
					>Upload image:</label
				>
				<div class="flex items-center space-x-2 mt-2">
					<button
						class="upload-image-button text-white py-1 px-3 rounded-md hover:bg-blue-300"
						on:click={() => uploadImageRef.click()}>Upload</button
					>
					{#if character.image?.length > 0}
						<button
							class="remove-image-button bg-red-600 text-white py-1 px-3 rounded-md hover:bg-red-700"
							on:click={() => (character.image = '')}>Remove</button
						>
					{/if}
					<input
						bind:this={uploadImageRef}
						type="file"
						accept="image/*"
						style="display: none;"
						name="image"
						multiple
						on:change={(e) => {
							uploadImage(e);
						}}
					/>
				</div>
				{#if requireImageError}
					<p class="text-sm text-red-400 mt-1">An image is required!</p>
				{/if}
			</div>
			{#if character.image?.length > 0}
				<img src={`data:image/jpeg;base64,${character.image}`} alt="" class="max-w-9/10 mb-4" />
			{/if}
			<div class="modal-content flex flex-col items-center">
				<div class="flex space-x-2 mb-2">
					<button
						class="add-baby-button bg-gray-300 py-1 px-3 rounded-md hover:bg-gray-400"
						on:click={() => onCloseModal()}>Cancel</button
					>
					{#if isCreate}
						<button
							class="add-baby-button bg-green-600 text-white py-1 px-3 rounded-md hover:bg-green-700"
							type="submit">Create</button
						>
					{:else}
						<button
							class="add-baby-button bg-green-600 text-white py-1 px-3 rounded-md hover:bg-green-700"
							type="submit">Edit</button
						>
					{/if}
				</div>
				{#if createBabyError}
					<p class="text-sm text-red-400">There is an error creating a record. Try again later.</p>
				{/if}
			</div>
		</form>
		<hr class="border-t border-gray-300 mb-4" />
	</div>
</div>

<style>
	.upload-image-button {
		cursor: pointer;
		font-size: 1rem;
		padding: 0.5rem;
		color: #1d5087;
		border-width: 1px;
		border-color: #007bff;
		border-style: solid;
		border-radius: 4px;
		transition: background-color 0.3s;
		margin: 10px;
	}

	.remove-image-button {
		cursor: pointer;
		font-size: 1rem;
		padding: 0.5rem;
		color: red;
		border-width: 1px;
		border-color: red;
		border-style: solid;
		border-radius: 4px;
		transition: background-color 0.3s;
		margin: 10px;
	}

	form {
		display: flex;
		flex-direction: column;
		/* max-width: 400px; */
		margin: 1rem auto;
		padding: 1rem;
		border-radius: 4px;
		background-color: #ffffff;
		/* box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24); */
	}

	label {
		font-weight: bold;
		font-size: 1.1rem;
		margin-bottom: 0.5rem;
	}

	input {
		padding: 0.5rem;
		margin: 1rem;
		font-size: 1rem;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	.cancel-button {
		background-color: red;
	}

	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5); /* semi-transparent black */
		z-index: 9999; /* ensure the overlay appears on top of other content */
	}

	.modal {
		position: absolute;
		top: 55%;
		left: 50%;
		transform: translate(-50%, -50%);
		background-color: white;
		padding: 20px;
		z-index: 10000; /* ensure the modal appears on top of the overlay */
		width: 60%;
		height: 70%;
		overflow: scroll;
	}

	.header {
		font-size: 28px;
		font-weight: bold;
	}
</style>
