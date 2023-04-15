<script>
	import { getDefaultConfig, getConfig, updateConfig } from '../../api/config';
	import Tooltip from '../../components/Tooltip.svelte';

	let config = undefined;
	let alarmConfig = undefined;
	let awakeDetectionConfig = undefined;
	let monitoringConfig = undefined;

	let updateSuccess = false;
	let updateError = false;
	let invalidValues = {
		alarm_threshold: false,
		alarm_monitoring_interval: false,

		awake_threshold: false,

		monitoring_interval: false
	};

	async function getAllConfigs() {
		config = await getDefaultConfig();
		alarmConfig = await getConfig('alarm');

		let responses = await Promise.all([
			await getConfig('alarm'),
			await getConfig('awake_detection'),
			await getConfig('monitoring')
		]);
		alarmConfig = JSON.parse(responses[0].config);
		awakeDetectionConfig = JSON.parse(responses[1].config);
		monitoringConfig = JSON.parse(responses[2].config);
	}

	async function updateAllConfigs() {
		updateSuccess = false;
		updateError = false;
		Object.keys(invalidValues).forEach((x) => (invalidValues[x] = false));
		if (alarmConfig.alarm_threshold < 0 || alarmConfig.alarm_threshold > 100)
			invalidValues.alarm_threshold = true;
		if (alarmConfig.monitoring_interval < 0) invalidValues.alarm_monitoring_interval = true;
		if (awakeDetectionConfig.awake_threshold < 0 || awakeDetectionConfig.awake_threshold > 1)
			invalidValues.awake_threshold = true;
		if (monitoringConfig.monitoring_interval < 0) invalidValues.monitoring_interval = true;

		if (
			Object.keys(invalidValues)
				.map((x) => invalidValues[x])
				.every((y) => y === false)
		) {
			let responses = await Promise.all([
				await updateConfig('alarm', alarmConfig),
				await updateConfig('awake_detection', awakeDetectionConfig),
				await updateConfig('monitoring', monitoringConfig)
			]);

			if (responses.every((x) => x === true)) updateSuccess = true;
			else updateError = true;
		}
	}

	getAllConfigs();
</script>

<div class="main-body">
	{#if alarmConfig === undefined || awakeDetectionConfig === undefined || monitoringConfig === undefined}
		<p>Loading...</p>
	{:else if alarmConfig === null || awakeDetectionConfig === null || monitoringConfig === null}
		<p>There is an error retrieving the settings.</p>
	{:else}
		<form on:submit|preventDefault={updateAllConfigs}>
			<p class="subheader">Alarm</p>

			<div class="column input-row">
				<div class="row column-center">
					<label for="monitoringinterval">Monitoring Interval (seconds):</label>
					<Tooltip message="Time frame to retrieve the data to determine if the baby is flipped." />
					<input
						type="text"
						id="monitoringinterval"
						bind:value={alarmConfig.monitoring_interval}
						required
					/>
				</div>
				{#if invalidValues.alarm_monitoring_interval}
					<p class="error-message">Monitoring interval must be more than 0</p>
				{/if}
			</div>

			<div class="column input-row">
				<div class="row column-center">
					<label for="alarmthreshold">Alarm threshold:</label>
					<Tooltip
						message="Percentage of the times the baby is identified to be flipped in the given time frame before triggering the alarm."
					/>
					<input
						type="text"
						id="alarmthreshold"
						bind:value={alarmConfig.alarm_threshold}
						required
					/>
				</div>
				{#if invalidValues.alarm_threshold}
					<p class="error-message">Alarm threshold must be between 0 to 100</p>
				{/if}
			</div>

			<div class="row column-center input-row">
				<label for="monitoringinterval">Toggle fog alarm:</label>
				<Tooltip message="Whether the alarm will be triggered when the threshold is hit." />
				<input
					type="checkbox"
					id="toggledfogalarm"
					checked={alarmConfig.toggle_fog_alarm === 1}
					bind:value={alarmConfig.toggle_fog_alarm}
				/>
			</div>

			<p class="subheader">Awake Detection</p>

			<div class="column input-row">
				<div class="row column-center">
					<label for="awakethreshold">Awake threshold:</label>
					<Tooltip
						message="Adjust the sensitivity when detecting whether your baby is awake. A value closer to 1 indicates lower sensitivity while a value closer to 0 indicates higher sensitivity."
					/>
					<input
						type="text"
						id="awakethreshold"
						bind:value={awakeDetectionConfig.awake_threshold}
						required
					/>
				</div>
				{#if invalidValues.awake_threshold}
					<p class="error-message">Awake threshold must be between 0 and 1</p>
				{/if}
			</div>

			<p class="subheader">Monitoring</p>

			<div class="column input-row">
				<div class="row column-center">
					<label for="monitoringinterval">Monitoring interval (seconds):</label>
					<Tooltip
						message="The interval of data collection."
					/>
					<input
						type="text"
						id="monitoringinterval"
						bind:value={monitoringConfig.monitoring_interval}
						required
					/>
				</div>
				{#if invalidValues.monitoring_interval}
					<p class="error-message">Monitoring interval must be more than 0</p>
				{/if}
			</div>

			<button type="submit">Update</button>
			{#if updateSuccess}
				<p class="success-message">Update successful!</p>
			{/if}

			{#if updateError}
				<p class="error-message">There is an error updating the settings.</p>
			{/if}
		</form>
	{/if}
</div>

<style>
	:global(body) {
		font-family: Arial, sans-serif;
		background-color: #f0f0f0;
	}

	.subheader {
		font-size: 26px;
		font-weight: bold;
		margin-top: 30px;
	}

	.main-body {
		margin: 128px 20px 20px 20px;
	}

	label {
		font-weight: bold;
		font-size: 1.1rem;
		/* margin-bottom: 0.5rem; */
	}

	input[type='text'] {
		padding: 0.5rem;
		/* margin-bottom: 1rem; */
		margin: 0 1rem;
		font-size: 1rem;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	input[type='checkbox'] {
		margin: 0 1rem;
	}

	.input-row {
		margin: 10px 0;
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
	}

	.success-message {
		color: green;
	}

	.error-message {
		color: red;
	}
</style>
