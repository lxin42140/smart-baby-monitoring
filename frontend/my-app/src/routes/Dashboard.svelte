<script>
	// Import required packages and components.
	import Icon from '@iconify/svelte';
	import { onMount, onDestroy } from 'svelte';
	import { io } from 'socket.io-client';
	import Chart from 'chart.js';
	import BabyList from '../components/BabyList.svelte';
	import ImageCarousel from '../components/ImageCarousel.svelte';
	import { baseUrl } from '../api';
	import { getAllBabies } from '../api/baby';
	import TooltipChart from '../components/TooltipChart.svelte';
	import Toolbar from '../components/Toolbar.svelte';
	import { fade } from 'svelte/transition';

	// Define local states.
	let noData = false;
	let chart_temp;
	let chart_pressure;
	let chart_bpm;
	let chart_dist;
	let socket; // Socket
	let dist_now_left;
	let dist_now_right;
	let temperature_now;
	let pressure_now;
	let deviceName;
	let isAsleep = undefined;
	let isSocketEnabled = true;
	// Update this image list to show what image we need.
	let imageList = [];
	let setIntervalRef;

	let characters = [];

	// Temperature
	let data = {
		labels: ['', '', '', '', '', '', ''],
		datasets: [
			{
				label: 'Temperature',
				data: [0, 0, 0, 0, 0, 0, 0],
				fill: '#990f02',
				borderColor: 'red',
				tension: 0.1
			}
		]
	};

	// Pressure
	let data_2 = {
		labels: ['', '', '', '', '', '', ''],
		datasets: [
			{
				label: 'Pressure',
				data: [0, 0, 0, 0, 0, 0, 0],
				fill: '#990f02',
				borderColor: 'red',
				tension: 0.1
			}
		]
	};

	// BPM
	let data_3 = {
		labels: ['', '', '', '', '', '', ''],
		datasets: [
			{
				label: 'Sleep Quality',
				data: [0, 0, 0, 0, 0, 0, 0],
				fill: '#990f02',
				borderColor: 'red',
				borderWidth: 1
			}
		]
	};

	// Video Feed
	let data_4 = {
		labels: ['', '', '', '', '', '', ''],
		datasets: [
			{
				label: 'Left Distance',
				data: [0, 0, 0, 0, 0, 0, 0],
				fill: false,
				borderColor: 'blue',
				tension: 0.1
			},
			{
				label: 'Right Distance',
				data: [0, 0, 0, 0, 0, 0, 0],
				fill: false,
				borderColor: 'green',
				tension: 0.1
			}
		]
	};

	// Options for the graphs.
	const options = {
		scales: {
			y: {
				beginAtZero: true,
				type: 'linear'
			}
		},
		plugins: {
			tooltips: {
				enabled: true,
				backgroundColor: 'rgba(0, 0, 0, 0.8)',
				titleColor: '#ffffff',
				bodyColor: '#ffffff',
				borderColor: '#ffffff',
				borderWidth: 1,
				borderRadius: 5,
				titleFont: {
					size: 16,
					family: 'Arial, sans-serif',
					weight: 'bold'
				},
				bodyFont: {
					size: 14,
					family: 'Arial, sans-serif',
					weight: 'normal'
				},
				callbacks: {
					title: function (context) {
						const point = context[0];
						return `X-axis: ${point.label}`;
					},
					label: function (context) {
						const point = context.parsed;
						return `Y-axis: ${point.y}`;
					}
				}
			},
			title: {
				display: true,
				text: 'Custom Chart Title'
			}
		}
	};

	// Options for the graphs.
	// This is for the Sleep Graph
	const options_2 = {
		scales: {
			y: {
				beginAtZero: false,
				min: 0,
				max: 1
			}
		}
	};

	function formatDatetimeForSQL(date) {
		return date.toISOString().slice(0, 19).replace('T', ' ');
	}

	// This is to update the charts whenever a baby profile is selected.
	function handleBabyCardClick(event) {
		const character = event.detail;
		// Perform any action you want with the character data here
		deviceName = character.devicename;
		// We need to update the data with the correct baby data.
	}

	function handleDateRangeData(event) {
		const filteredData = event.detail;
		filteredData.forEach((sensorData) => {
			const time = new Date(sensorData.timestamp);
			const hours = String(time.getHours()).padStart(2, '0');
			const minutes = String(time.getMinutes()).padStart(2, '0');
			const seconds = String(time.getSeconds()).padStart(2, '0');

			const formattedDateTime = `${hours}:${minutes}:${seconds}`;
			// Temp
			data.labels.push(formattedDateTime);
			data.labels.shift();
			data.datasets[0].data.push(sensorData.temperature);
			data.datasets[0].data.shift();
			chart_temp.update();
			// Pressure
			data_2.labels.push(formattedDateTime);
			data_2.labels.shift();
			data_2.datasets[0].data.push(sensorData.pressure);
			data_2.datasets[0].data.shift();
			chart_pressure.update();

			// This is for Sleep
			data_3.labels.push(formattedDateTime);
			data_3.labels.shift();
			data_3.datasets[0].data.push(sensorData.is_eye_open);
			data_3.datasets[0].data.shift();
			chart_bpm.update();

			// This for Distance.
			data_4.labels.push(formattedDateTime);
			data_4.labels.shift();
			data_4.datasets[0].data.push(sensorData.leftdistance);
			data_4.datasets[0].data.shift();
			data_4.datasets[1].data.push(sensorData.rightdistance);
			data_4.datasets[1].data.shift();
			chart_dist.update();

			imageList.push(sensorData.image);

			dist_now_left = sensorData.leftdistance;
			dist_now_right = sensorData.rightdistance;
		});
	}

	function filterDataByDevice(deviceName, data_in) {
		const filteredData = data_in
			.filter((item) => item.devicename === deviceName)
			.sort((a, b) => {
				const dateA = new Date(a.timestamp);
				const dateB = new Date(b.timestamp);
				return dateA - dateB;
			})
			.slice(0, 20);
		return filteredData;
	}

	async function fetchData() {
		// Get the current date and time
		// Get the current date and time in Singapore time
		let now = new Date().toLocaleString('en-US', { timeZone: 'Asia/Singapore' });

		// Convert the date and time to a Date object
		now = new Date(now);

		// Format the date and time as a string in the desired format
		let currentDate = now
			.toLocaleString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' })
			.replace(/(\d+)\/(\d+)\/(\d+)/, '$3-$1-$2');
		let currentTime = now.toLocaleString('en-US', {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit',
			hour12: false
		});

		// Get the time 10 minutes ago
		let tenMinutesAgo = new Date(now.getTime() - 10 * 60000);

		// Format the date and time as a string in the desired format
		let tenMinutesAgoDate = tenMinutesAgo
			.toLocaleString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' })
			.replace(/(\d+)\/(\d+)\/(\d+)/, '$3-$1-$2');
		let tenMinutesAgoTime = tenMinutesAgo.toLocaleString('en-US', {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit',
			hour12: false
		});

		const API_URL =
			baseUrl +
			`/data/sensor/${deviceName}?start_time=${
				tenMinutesAgoDate + ' ' + tenMinutesAgoTime
			}&end_time=${currentDate + ' ' + currentTime}`;

		const SLEEP_API_URL =
			baseUrl +
			`/data/sleep/${deviceName}?start_time=${
				tenMinutesAgoDate + ' ' + tenMinutesAgoTime
			}&end_time=${currentDate + ' ' + currentTime}&reset=1`;

		// Fetch the data from the API
		const response = await fetch(API_URL);
		const sleepResponse = await fetch(SLEEP_API_URL);
		const data_return = await response.json();
		const sleep_data_return = await sleepResponse.json();

		if (sleep_data_return && sleep_data_return.length > 0) {
			sleep_data_return.forEach((data) => {
				data_3.labels.push(data.timestamp);
				data_3.labels.shift();
				data_3.datasets[0].data.push(data.is_awake);
				data_3.datasets[0].data.shift();
				chart_bpm.update();
			});
			isAsleep =
				sleep_data_return[sleep_data_return.length - 1].is_awake &&
				!sleep_data_return[sleep_data_return.length - 1].is_awake;
		}

		if (data_return?.length == 0) {
			// put the alert here to show no data
			noData = true;
		} else {
			noData = false;
		}
		const filteredData = filterDataByDevice(deviceName, data_return);
		imageList = [];
		temperature_now = filteredData[filteredData.length - 1].temperature;
		pressure_now = filteredData[filteredData.length - 1].pressure;
		dist_now_left = filteredData[filteredData.length - 1].leftdistance;
		dist_now_right = filteredData[filteredData.length - 1].rightdistance;
		filteredData.forEach((sensorData) => {
			const time = new Date(sensorData.timestamp);
			const hours = String(time.getHours()).padStart(2, '0');
			const minutes = String(time.getMinutes()).padStart(2, '0');
			const seconds = String(time.getSeconds()).padStart(2, '0');

			const formattedDateTime = `${hours}:${minutes}:${seconds}`;
			// Temp
			data.labels.push(formattedDateTime);
			data.labels.shift();
			data.datasets[0].data.push(sensorData.temperature);
			data.datasets[0].data.shift();
			chart_temp.update();
			// Pressure
			data_2.labels.push(formattedDateTime);
			data_2.labels.shift();
			data_2.datasets[0].data.push(sensorData.pressure);
			data_2.datasets[0].data.shift();
			chart_pressure.update();

			// This for Distance.
			data_4.labels.push(formattedDateTime);
			data_4.labels.shift();
			data_4.datasets[0].data.push(sensorData.leftdistance);
			data_4.datasets[0].data.shift();
			data_4.datasets[1].data.push(sensorData.rightdistance);
			data_4.datasets[1].data.shift();
			chart_dist.update();

			imageList.push(sensorData.image);

			dist_now_left = sensorData.leftdistance;
			dist_now_right = sensorData.rightdistance;
		});
		imageList = imageList;
	}

	onMount(() => {
		const canvas = document.getElementById('myChart');
		chart_temp = new Chart(canvas, {
			type: 'line',
			data: data,
			options: options,
			fill: '#990f02'
		});
		const canvas_2 = document.getElementById('myPaChart');
		chart_pressure = new Chart(canvas_2, {
			type: 'line',
			data: data_2,
			options: options,
			fill: '#990f02'
		});

		const canvas_3 = document.getElementById('myBPMChart');
		chart_bpm = new Chart(canvas_3, {
			type: 'bar',
			data: data_3,
			options: options_2,
			fill: '#990f02'
		});

		const canvas_4 = document.getElementById('myDistChart');
		chart_dist = new Chart(canvas_4, {
			type: 'line',
			data: data_4,
			options: options,
			fill: '#990f02'
		});

		const module = import('tw-elements');

		socket = io(baseUrl);

		socket.on('connect', (data) => {
			console.log('Connected to WebSocket:', data);
		});

		socket.on('disconnect', () => {
			console.log('Disconnected from WebSocket');
		});

		retrieveBabies();
	});

	//get all the babies here
	const retrieveBabies = async () => {
		const res = await getAllBabies();
		if (res) {
			characters = res;
			if (characters.length > 0) {
				deviceName = characters[0].devicename;
				await fetchData();
			}
		}
	};

	onDestroy(() => {
		//Destroy element
		if (socket) {
			socket.disconnect();
		}
	});
</script>

<section class="bg-white py-20 overflow-hidden shadow-lg banner">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="text-center">
			<h2 class="text-3xl font-extrabold text-gray-200 font-mono sm:text-4xl">Dashboard</h2>
			<p class="mt-4 text-lg text-gray-600 bg-white rounded-lg overflow-hidden font-mono">
				(Analyze your data for your child in one location).
			</p>
		</div>
	</div>
</section>

<BabyList {characters} on:babyCardClicked={handleBabyCardClick} {retrieveBabies} />

<section class="bg-gray-200 py-5">
	<Toolbar on:viewPastChart={handleDateRangeData} activeDeviceName={deviceName} {setIntervalRef} />
	{#if noData}
		<div class="row row-center w-100">
			<span
				class="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-700 bg-red-100 rounded-full"
				>No data</span
			>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 w-100">
			<!-- Card #4 Image -->
			<div class="relative" style="z-index: 1;">
				<div
					class="bg-white overflow-hidden shadow rounded-lg"
					style={`
						position: relative;
						top: {$cardState.top};
						left: {$cardState.left};
						width: {$cardState.width};
						height: {$cardState.height};
						z-index: {$cardState.zIndex};
						`}
				>
					<div class="px-4 py-5 sm:p-6">
						<div class="flex items-center">
							<div class="flex-shrink-0 bg-gray-300 rounded-md p-3">
								<Icon icon="ph:baby" width="24" />
							</div>
							<div class="ml-5 w-0 flex-1">
								<dt class="text-sm font-medium text-gray-500 truncate font-mono">Child Position</dt>
								<dd class="flex items-baseline">
									<div class="text-lg font-medium text-green-700 font-mono">Okay</div>
									<div
										class="ml-2 flex items-baseline text-sm font-mono font-semibold text-red-500"
									>
										<svg
											class="self-center flex-shrink-0 h-5 w-5 text-indigo-500"
											viewBox="0 0 20 20"
											fill="currentColor"
											aria-hidden="true"
										>
											<path fill-rule="evenodd" d="M16.707 5" />
										</svg>
									</div>
								</dd>
							</div>
						</div>
						<div>
							<ImageCarousel {imageList} />
						</div>
					</div>
				</div>
				<TooltipChart
					text="This chart shows the image of your baby. You can click through it to view images in ten min intervals."
				/>
			</div>
			<div class="relative">
				<div
					class="bg-white overflow-hidden shadow rounded-lg transform transition duration-500 hover:scale-105 hover:-translate-y-1 hover:shadow-xl"
					data-te-toggle="modal"
					data-te-target="#exampleModalCenteredScrollable"
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
								<dt class="text-sm font-medium text-gray-500 truncate font-mono">Temperature</dt>
								<dd class="flex items-baseline">
									<div class="text-lg font-medium text-gray-900 font-mono">{temperature_now}˚C</div>
								</dd>
							</div>
						</div>
						<div>
							<canvas id="myChart" />
						</div>
					</div>
				</div>
				<TooltipChart
					text="This chart shows the temperature surrounding your baby, measured in Celcius."
				/>
			</div>

			<div class="relative">
				<div
					class="bg-white overflow-hidden shadow rounded-lg transform transition duration-500 hover:scale-105 hover:-translate-y-1 hover:shadow-xl"
					data-te-toggle="modal"
					data-te-target="#exampleModalCenteredScrollablePressure"
				>
					<div class="px-4 py-5 sm:p-6">
						<div class="flex items-center">
							<div class="flex-shrink-0 bg-gray-300 rounded-md p-3">
								<Icon icon="material-symbols:blood-pressure" width="24" />
							</div>
							<div class="ml-5 w-0 flex-1">
								<dt class="text-sm font-medium text-gray-500 truncate font-mono">Pressure</dt>
								<dd class="flex items-baseline">
									<div class="text-lg font-medium text-gray-900 font-mono">{pressure_now} Pa</div>
								</dd>
							</div>
						</div>
						<div>
							<canvas id="myPaChart" />
						</div>
					</div>
				</div>
				<TooltipChart text="This chart shows the pressure surrounding your baby, measured in Pa" />
			</div>

			<div class="relative">
				<div
					class="bg-white overflow-hidden shadow rounded-lg transform transition duration-500 hover:scale-105 hover:-translate-y-1 hover:shadow-xl"
					data-te-toggle="modal"
					data-te-target="#exampleModalCenteredScrollableSleep"
				>
					<div class="px-4 py-5 sm:p-6">
						<div class="flex items-center">
							<div class="flex-shrink-0 bg-gray-300 rounded-md p-3">
								<Icon icon="solar:moon-sleep-bold" width="24" />
							</div>
							<div class="ml-5 w-0 flex-1">
								<dt class="text-sm font-medium text-gray-500 truncate font-mono">Sleep Quality</dt>
								<dd class="flex items-baseline">
									{#if isAsleep}
										<div
											class="text-lg font-medium text-green-500 font-mono"
											in:fade={{ duration: 300 }}
											out:fade={{ duration: 300 }}
										>
											Asleep
										</div>
									{:else if isAsleep === false}
										<div
											class="text-lg font-medium text-red-500 font-mono"
											in:fade={{ duration: 300 }}
											out:fade={{ duration: 300 }}
										>
											Awake
										</div>
									{/if}
								</dd>
							</div>
						</div>
						<div class="mt-2">
							<canvas id="myBPMChart" />
						</div>
						<div class="mt-2" />
					</div>
				</div>
				<TooltipChart
					text="This chart shows whether the baby was awake or not. A full bar means he is awake."
				/>
			</div>

			<div class="relative">
				<div
					class="bg-white overflow-hidden shadow rounded-lg transform transition duration-500 hover:scale-105 hover:-translate-y-1 hover:shadow-xl"
					data-te-toggle="modal"
					data-te-target="#exampleModalCenteredScrollableDist"
				>
					<div class="px-4 py-5 sm:p-6">
						<div class="flex items-center">
							<div class="flex-shrink-0 bg-gray-300 rounded-md p-3">
								<Icon icon="iconoir:crib" width="26" height="26" />
							</div>
							<div class="ml-5 w-0 flex-1">
								<dt class="text-sm font-medium text-gray-500 truncate font-mono">
									Distance From Crib
								</dt>
								<dd class="flex items-baseline">
									<div class="text-lg font-medium text-gray-900 font-mono">
										{dist_now_left} Left(cm) / {dist_now_right} Right(cm)
									</div>
								</dd>
							</div>
						</div>
						<div>
							<canvas id="myDistChart" />
						</div>
					</div>
				</div>
				<TooltipChart
					text="This chart shows the distance of the baby from the crib on the left and right sides, measured in meters."
				/>
			</div>
		</div>
	{/if}
</section>

<style>
	.banner {
		background-position: center left;
		background-color: #293B58;
	}

	h2 {
		font-size: 28px;
		font-weight: bold;
	}
</style>
