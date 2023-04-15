<script>
	import { baseUrl } from '../../api';
	import { getServerConfig } from '../../api/config';
	import Select, { Option } from '@smui/select';
	import { io } from 'socket.io-client';

	let allAlarmOptions = undefined;
	let fogCommand;
	let fogName;
	let fogState;
	let emitSuccessful;

	let socket = io(baseUrl);

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

	const sendAlarmToBackend = () => {
		if (fogCommand && fogName && fogState) {
			socket.emit('alarm', fogCommand, fogName, fogState);
		}
		emitSuccessful = true;
		setTimeout(() => {
			emitSuccessful = false;
		}, 5000);
	};

	getTriggerAlarmOptions();
</script>

<div class="bg-white p-10">
	<h2>Trigger commands</h2>
	<p style="margin-bottom: 10px;">You can execute different commands here.</p>
	<div class="column column-center">
		{#if allAlarmOptions !== null && allAlarmOptions !== undefined}
			<div class="row" style="justify-content: flex-start;">
				<div class="select">
					<Select bind:value={fogCommand} label="Command">
						{#each allAlarmOptions.fog_command as command}
							<Option value={command}>{command}</Option>
						{/each}
					</Select>
				</div>

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
			<button on:click={() => sendAlarmToBackend()}>Send</button>
		</div>
		{#if emitSuccessful}
			<p class="text-green-400">Command has been sent!</p>
		{/if}
	</div>
</div>

<style>
	h2 {
		font-size: 28px;
		font-weight: bold;
	}

	.select {
		margin: 0 10px;
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
</style>
