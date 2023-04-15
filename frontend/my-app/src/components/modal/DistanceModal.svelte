<script>
	import { onMount, createEventDispatcher } from 'svelte';
	import Icon from '@iconify/svelte';
	export let data = null;
	export let options = null;
	export let dist_now_left = 20;
    export let dist_now_right = 20; 
	export let dist_diff = 0; 
	export let updateChart; 

	// Add your component logic here
	let selectedDate = '';
	let selectedTime = '';
	let today = new Date().toISOString().split('T')[0];
	let maxTime; 
    let chart_dist_2; 
    let isMounted = false; 

	function formatHoursAndMinutes(hours, minutes) {
		const formattedHours = hours.toString().padStart(2, '0');
		const formattedMinutes = minutes.toString().padStart(2, '0');
		return `${formattedHours}:${formattedMinutes}`;
	}

	const dispatch = createEventDispatcher();

	function sendData() {
		const data = {"date": selectedDate, "time": selectedTime};
		dispatch('dist_modal_msg', data);
	}

	$: {
		maxTime = formatHoursAndMinutes(new Date().getHours(), new Date().getMinutes());
		today = new Date().toISOString().split('T')[0];
		console.log(maxTime);
	}

    $: if (isMounted) {
		chart_dist_2.data.labels = data.labels;
		chart_dist_2.data.datasets = data.datasets;
		chart_dist_2.update();
	}

	onMount(() => {
		const canvas_6 = document.getElementById('myDistChartModal');
		chart_dist_2 = new Chart(canvas_6, {
			type: 'line',
			data: data,
			options: options,
			fill: '#990f02'
		});
        isMounted = true; 
	})
</script>

<!-- Modal for Temperature -->
<div
	class="pointer-events-auto relative flex w-full flex-col rounded-md border-none bg-white bg-clip-padding text-current shadow-2xl outline-none"
>
	<div
		class="bg-white overflow-hidden shadow rounded-lg transform transition duration-500 hover:scale-105 hover:-translate-y-1 hover:shadow-xl"
	>
		<div class="px-4 py-5 sm:p-6">
			<div class="flex items-center">
				<div class="flex-shrink-0 bg-gray-300 rounded-md p-3">
					<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
						<path
							fill="#990f02"
							d="M17 13V7h2v6h-2m0 4v-2h2v2h-2m-4-4V5c0-1.7-1.3-3-3-3S7 3.3 7 5v8c-2.2 1.7-2.7 4.8-1 7s4.8 2.7 7 1s2.7-4.8 1-7c-.3-.4-.6-.7-1-1m-3-9c.6 0 1 .4 1 1v3H9V5c0-.6.4-1 1-1Z"
						/>
					</svg>
				</div>
				<div class="ml-5 w-0 flex-1">
					<dt class="text-sm font-medium text-gray-500 truncate font-mono">Pressure </dt>
					<dd class="flex items-baseline">
						<div class="text-lg font-medium text-gray-900 font-mono">{dist_now_left} Left {dist_now_right} Right</div>
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
				<canvas id="myDistChartModal" />
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
						>Selected Time (in Minute Intervals)</label
					>
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
<!---End Modal for Temperature-->
