<script>
	import { onMount } from 'svelte';
	import { io } from 'socket.io-client';
	import { baseUrl } from '../api';

	let showAlert = false;
    let socket; 

	onMount(() => {
		// ...WebSocket code as before...
		socket = io(baseUrl);

		socket.on('connect', (data) => {
			console.log('Connected to WebSocket:', data);
		});

        // Listen for messages
		socket.addEventListener('flipped_alarm', (event) => {
			const alertText = 'Alarm triggered! Please acknowledge.';
            showAlert = true;
		});
	});

	function closeAlert() {
		showAlert = false;
	}
</script>

{#if showAlert}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white p-6 rounded-lg shadow-lg text-center">
			<h2 class="text-2xl font-bold mb-4">Alarm triggered!</h2>
			<p class="mb-6">Please acknowledge.</p>
			<button
				on:click={closeAlert}
				class="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-700 transition-colors duration-300"
			>
				Acknowledge
			</button>
		</div>
	</div>
{/if}
