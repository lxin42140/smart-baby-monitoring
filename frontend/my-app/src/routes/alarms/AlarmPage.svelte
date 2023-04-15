<script>
	import DataTable, { Head, Body, Row, Cell } from '@smui/data-table';
	import { getAllAlarms, getFilteredAlarms } from '../../api/alarm';
	import { isBefore, isEmptyDateTime, isValidDateTime } from '../../helper/alarm';
	import { getServerConfig } from '../../api/config';
	import Select, { Option } from '@smui/select';

	let allAlarms = [];
	let allFogs = [];
	let filterFog = 'all';
	let startDate;
	let endDate;
	let selectedStartTime;
	let selectedEndTime;
	let invalidFog = false;
	let invalidStartDate = false;
	let invalidEndDate = false;

	const retrieveAllAlarms = async () => {
		const res = await getAllAlarms();
		if (res) allAlarms = res;
	};

	const retrieveDefaultConfig = async () => {
		const res = await getServerConfig();
		if (res) {
			allFogs = res.fog_name;
		}
	};

	const onResetFilter = () => {
		startDate = '';
		endDate = '';
		// filterFog = 'all'
		retrieveDefaultConfig();
	};

	const onSubmitFilter = async () => {
		invalidFog = false;
		invalidStartDate = false;
		invalidEndDate = false;
		if (!filterFog || filterFog.length === 0) {
			invalidFog = true;
		}
		if (
			!isEmptyDateTime(startDate, selectedStartTime) ||
			!isEmptyDateTime(endDate, selectedEndTime)
		) {
			if (!isValidDateTime(startDate, selectedStartTime)) {
				invalidStartDate = true;
			}
			if (!isValidDateTime(endDate, selectedEndTime)) {
				invalidEndDate = true;
			}
			if (invalidStartDate && !invalidEndDate) invalidEndDate = true;
			if (invalidEndDate && !invalidStartDate) invalidStartDate = true;

			if (!isBefore(startDate, selectedStartTime, endDate, selectedEndTime)) {
				invalidEndDate = true;
			}
		}

		if (!invalidStartDate && !invalidEndDate && !invalidFog) {
			const res = await getFilteredAlarms(
				filterFog,
				startDate,
				selectedStartTime,
				endDate,
				selectedEndTime
			);
			if (res) allAlarms = res;
		}
	};

	retrieveAllAlarms();
	retrieveDefaultConfig();
</script>

<div class="bg-white">
	<div class="filter-box">
		<h3 class="font-mono text-lg font-bold">Filter</h3>

		<div class="row column-center">
			<Select bind:value={filterFog} label="Fog">
				{#each allFogs as fog}
					<Option value={fog}>{fog}</Option>
				{/each}
			</Select>
			{#if invalidFog}
				<p class="text-red-400 ml-5">Invalid fog name</p>
			{/if}
		</div>

		<div class="row column-center my-1">
			<label class="block font-bold text-gray-700 mr-2" for="selectedStartDate"
				>Start date and time</label
			>
			<input
				type="date"
				class="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
				id="selectedStartDate"
				bind:value={startDate}
			/>
			<input
				type="time"
				class="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
				id="selectedStartTime"
				bind:value={selectedStartTime}
				max={'23:59'}
			/>
			{#if invalidStartDate}
				<p class="text-red-400 ml-5">Invalid start date</p>
			{/if}
		</div>

		<div class="row column-center my-1">
			<label class="block font-bold text-gray-700 mr-2" for="selectedEndDate"
				>End date and time</label
			>
			<input
				type="date"
				class="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
				id="selectedEndDate"
				bind:value={endDate}
			/>
			<input
				type="time"
				class="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
				id="selectedEndTime"
				bind:value={selectedEndTime}
				max={'23:59'}
			/>
			{#if invalidEndDate}
				<p class="text-red-400 ml-5">Invalid end date</p>
			{/if}
		</div>

		<div class="row">
			<button class="filter-button" on:click={onSubmitFilter}>Filter</button>
			<button class="reset-button" on:click={onResetFilter}>Reset</button>
		</div>
	</div>

	{#if allAlarms.length > 0}
		<DataTable table$aria-label="Alarm list" style="width: calc(100% - 40px); margin: 20px">
			<Head>
				<Row>
					<Cell numeric>ID</Cell>
					<Cell style="width: 100%;">Device name</Cell>
					<Cell>Interval start</Cell>
					<Cell>Interval end</Cell>
					<Cell>Sensor data count</Cell>
					<Cell>Flipped count</Cell>
					<Cell>Ratio</Cell>
					<Cell>Alarm Threshold</Cell>
				</Row>
			</Head>
			<Body>
				{#each allAlarms as item (item.id)}
					<Row>
						<Cell numeric>{item.id}</Cell>
						<Cell>{item.devicename}</Cell>
						<Cell>{item.interval_start}</Cell>
						<Cell>{item.interval_end}</Cell>
						<Cell>{item.sensor_data_count}</Cell>
						<Cell>{item.flipped_count}</Cell>
						<Cell>{item.ratio}</Cell>
						<Cell>{item.threshold}</Cell>
					</Row>
				{/each}
			</Body>
		</DataTable>
	{:else}
		<div class="row row-center">
			<p class="font-mono m-10">There are no alarms triggered yet.</p>
		</div>
	{/if}
</div>

<style>
	.filter-box {
		display: flex;
		flex-direction: column;
		/* max-width: 400px; */
		width: calc(100% - 6rem);
		margin: 3rem;
		padding: 1rem;
		border-radius: 4px;
		background-color: #ffffff;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
	}
	.filter-button {
		cursor: pointer;
		font-size: 1rem;
		padding: 0.5rem 1rem;
		background-color: #007bff;
		color: #fff;
		border: none;
		border-radius: 4px;
		transition: background-color 0.3s;
		margin: 10px;
	}

	.reset-button {
		cursor: pointer;
		font-size: 1rem;
		padding: 0.5rem 1rem;
		/* background-color: #007bff; */
		color: #007bff;
		/* border: none; */
		border: 1px solid #007bff;
		border-radius: 4px;
		transition: background-color 0.3s;
		margin: 10px;
	}
</style>
