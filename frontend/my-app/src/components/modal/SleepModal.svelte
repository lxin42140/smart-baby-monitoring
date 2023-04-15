<script>
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import { createEventDispatcher } from 'svelte';
	export let data = null;
	export let options = null;

	// Add your component logic here
	let selectedDate = '';
	let selectedTime = '';
	let today = new Date().toISOString().split('T')[0];
	let maxTime;
	let chart_bpm_2;
	let isMounted = false;

	function formatHoursAndMinutes(hours, minutes) {
		const formattedHours = hours.toString().padStart(2, '0');
		const formattedMinutes = minutes.toString().padStart(2, '0');
		return `${formattedHours}:${formattedMinutes}`;
	}

	const dispatch = createEventDispatcher();

	function sendData() {
		const data = {"date": selectedDate, "time": selectedTime};
		dispatch('sleep_modal_msg', data);
	}

	$: {
		maxTime = formatHoursAndMinutes(new Date().getHours(), new Date().getMinutes());
		today = new Date().toISOString().split('T')[0];
		console.log(maxTime);
	}

	$: if (isMounted) {
		chart_bpm_2.data.labels = data.labels;
		chart_bpm_2.data.datasets = data.datasets;
		chart_bpm_2.update();
	}

	onMount(() => {
		const canvas_6 = document.getElementById('myChartBPMModal');
		chart_bpm_2 = new Chart(canvas_6, {
			type: 'bar',
			data: data,
			options: options,
			fill: '#990f02'
		});
		isMounted = true;
	});
</script>

<div
	class="pointer-events-auto relative flex w-full flex-col rounded-md border-none bg-white bg-clip-padding text-current shadow-2xl outline-none"
>
	<div
		class="bg-white overflow-hidden shadow rounded-lg transform transition duration-500 hover:scale-105 hover:-translate-y-1 hover:shadow-xl"
	>
		<div class="px-4 py-5 sm:p-6">
			<div class="flex items-center">
				<div class="flex-shrink-0 bg-gray-300 rounded-md p-3">
					<Icon icon="solar:moon-sleep-bold" width="24" />
				</div>
				<div class="ml-5 w-0 flex-1">
					<dt class="text-sm font-medium text-gray-500 truncate font-mono">Sleep Quality</dt>
					<dd class="flex items-baseline">
						<div class="text-lg font-medium text-gray-900 font-mono">Good!</div>
					</dd>
				</div>

				<button
					type="button"
					class="box-content rounded-none border-none hover:no-underline hover:opacity-75 focus:opacity-100 focus:shadow-none focus:outline-none"
					data-te-modal-dismiss
					aria-label="Close"
				>
					<Icon icon="radix-icons:cross-1" width="24" />
				</button>
			</div>
			<div>
				<canvas id="myChartBPMModal" />
			</div>
			<form on:submit={sendData} class="max-w-lg mx-auto">
				<!--This should be the options that allows you to change the data type.-->
				<div class="mb-4">
					<label class="block font-bold text-gray-700 mb-2" for="scale">Y-Axis Scale</label>
					<select
						class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
						id="scale"
						bind:value={options.scales.y.type}
					>
						<option value="linear">Linear</option>
						<option value="logarithmic">Logarithmic</option>
					</select>
				</div>
				<div class="mb-4">
					<label class="block font-bold text-gray-700 mb-2" for="selectedTime"
						>Selected Time (in Minute Intervals):
					</label>
					<input
						type="time"
						class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
						id="selectedTime"
						bind:value={selectedTime}
						max={maxTime}
					/>
				</div>

				<!-- Add date picker -->
				<div class="mb-4">
					<label class="block font-bold text-gray-700 mb-2" for="selectedDate"
						>Selected Date:
					</label>
					<input
						type="date"
						class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
						id="selectedDate"
						bind:value={selectedDate}
						max={today}
					/>
				</div>

				<div class="text-center">
					<button
						class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
						type="submit">Update Chart</button
					>
				</div>
			</form>
		</div>
	</div>
</div>
