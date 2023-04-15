<script>
	import { createEventDispatcher } from 'svelte';
	import Select, { Option } from '@smui/select';
	import { getServerConfig } from '../api/config';
	import { io } from 'socket.io-client';
	import { baseUrl } from '../api';

	const dispatch = createEventDispatcher();

	export let activeDeviceName;

	let startDate = '';
	let endDate = '';
	let startTime = '';
	let endTime = '';
	let today = new Date().toISOString().split('T')[0];
	let maxTime;
	let socket; // Socket

	let openTriggerAlarmModal = false;
	let allAlarmOptions = undefined;
	let fogCommand;
	let fogName;
	let fogState;

	let minEndDate = today;
	let maxStartTime = '23:59';
	let minEndTime = '00:00';

	socket = io(baseUrl);
	socket.on('connect', (data) => {
		console.log('Connected to WebSocket:', data);
	});

	const getTriggerAlarmOptions = async () => {
		allAlarmOptions = await getServerConfig();
		if (allAlarmOptions !== null) {
			fogCommand = allAlarmOptions.fog_command[0];
			fogName = allAlarmOptions.fog_name[0];
			fogState = allAlarmOptions.fog_state[0];
		}
	};
	const sendAlarmToBackend = async () => {
		if (fogCommand && fogName && fogState) {
			await fetch(`${baseUrl}/command/${fogName}/${fogCommand}/${fogState}`);
		}
	};

	getTriggerAlarmOptions();

	// Update constraints based on the selected values
	$: {
		if (startDate) {
			minEndDate = startDate;
		}
		if (endDate) {
			maxStartTime = endDate === startDate ? maxTime : '23:59';
		}
		if (startTime) {
			minEndTime = startDate === endDate ? startTime : '00:00';
		}
	}

	$: {
		maxTime = formatHoursAndMinutes(new Date().getHours(), new Date().getMinutes());
		today = new Date().toISOString().split('T')[0];
		console.log(maxTime);
	}

	function formatHoursAndMinutes(hours, minutes) {
		const formattedHours = hours.toString().padStart(2, '0');
		const formattedMinutes = minutes.toString().padStart(2, '0');
		return `${formattedHours}:${formattedMinutes}`;
	}

	function formatDateForSQL(date, time) {
		if (!date || !time) return '';
		const [year, month, day] = date.split('-');
		const [hours, minutes] = time.split(':');
		const datee = new Date(year, month - 1, day, hours, minutes).toLocaleString();
		const arr = datee.split(",");
		const dateArr = arr[0].split("/");
		arr[0] = `${dateArr[2]}-${dateArr[1]}-${dateArr[0]}`
		return arr.join("");
	}

	async function handleViewPastChart() {
		if (startDate && endDate) {
			const sqlStartDate = formatDateForSQL(startDate, startTime);
			const sqlEndDate = formatDateForSQL(endDate, endTime);

			const res = await fetch(
				`${baseUrl}/data/sensor/${activeDeviceName}?start_time=${sqlStartDate}&end_time=${sqlEndDate}`
			);
			const ress = await res.json()
			dispatch('viewPastChart', ress);
		} else {
			const res = await fetch(`${baseUrl}/data/sensor/${activeDeviceName}`);
			const ress = await res.json()
			dispatch('viewPastChart', ress);
		}
	}
</script>

<div class="toolbar flex flex-wrap items-center p-4 bg-gray-100 rounded row-center">
	<label class="flex items-center space-x-2 mb-2 sm:mb-0 sm:space-x-4 sm:mr-4">
		<span class="text-sm sm:text-base">Start Date:</span>
		<input
			type="date"
			bind:value={startDate}
			max={today}
			class="border rounded px-2 py-1 text-sm sm:text-base"
		/>
	</label>
	<label class="flex items-center space-x-2 mb-2 sm:mb-0 sm:space-x-4 sm:mr-4">
		<span class="text-sm sm:text-base">End Date:</span>
		<input
			type="date"
			bind:value={endDate}
			max={today}
			min={minEndDate}
			class="border rounded px-2 py-1 text-sm sm:text-base"
		/>
	</label>
	<label class="flex items-center space-x-2 mb-2 sm:mb-0 sm:space-x-4 sm:mr-4">
		<span class="text-sm sm:text-base">Start Time:</span>
		<input
			type="time"
			bind:value={startTime}
			max={maxStartTime}
			class="border rounded px-2 py-1 text-sm sm:text-base"
		/>
	</label>
	<label class="flex items-center space-x-2 mb-2 sm:mb-0 sm:space-x-4 sm:mr-4">
		<span class="text-sm sm:text-base">End Time:</span>
		<input
			type="time"
			bind:value={endTime}
			min={minEndTime}
			max={maxTime}
			class="border rounded px-2 py-1 text-sm sm:text-base"
		/>
	</label>
	<button
		on:click={handleViewPastChart}
		class="bg-blue-600 text-white px-4 py-1 rounded mb-2 sm:mb-0 sm:mr-4"
	>
		View Data
	</button>
	<button
		on:click={() => {
			openTriggerAlarmModal = true;
		}}
		class="transform transition duration-500 hover:scale-105 hover:-translate-y-1 hover:shadow-l"
		>Trigger alarm</button
	>

	<!-- Modal to trigger alarm -->
	<div class="modal-overlay" style={openTriggerAlarmModal ? 'display: block' : 'display: none'}>
		<div class="modal">
			<h2>Trigger alarm</h2>
			<p style="margin-bottom: 10px;">
				Select the name of the command and the state to turn the alarm on/off.
			</p>
			<div class="modal-content column column-center">
				{#if allAlarmOptions !== null && allAlarmOptions !== undefined}
					<div class="row" style="justify-content: flex-start;">
						<div class="select">
							<Select bind:value={fogName} label="Name">
								{#each allAlarmOptions.fog_name as name}
									<Option value={name}>{name}</Option>
								{/each}
							</Select>
						</div>

						<div class="select">
							<Select bind:value={fogState} label="State">
								{#each allAlarmOptions.fog_state as state}
									<Option value={state}>{state}</Option>
								{/each}
							</Select>
						</div>
					</div>
				{/if}
				<div class="row">
					<button class="cancel-button" on:click={() => (openTriggerAlarmModal = false)}
						>Close</button
					>
					<button on:click={() => sendAlarmToBackend()}>Send</button>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
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
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		background-color: white;
		padding: 20px;
		z-index: 10000; /* ensure the modal appears on top of the overlay */
		width: 85%;
	}

	button {
		cursor: pointer;
		font-size: 1rem;
		padding: 0.5rem;
		background-color: #007bff;
		color: #fff;
		border: none;
		border-radius: 4px;
		transition: background-color 0.3s;
		margin: 10px;
	}
	.cancel-button {
		background-color: red;
	}

	.select {
		margin: 0 10px;
	}
	h2 {
		font-size: 28px;
		font-weight: bold;
	}
</style>
