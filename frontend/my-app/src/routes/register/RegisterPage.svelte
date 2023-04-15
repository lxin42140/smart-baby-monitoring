<script>
	import { register } from '../../api/user';

	let first_name = '';
	let last_name = '';
	let username = '';
	let password = '';
	let confirmPassword = '';
	//errors/success
	let passwordsMismatch = false;
	let registerError = false;
	let loginSuccess = false;

	async function handleSubmit(event) {
		event.preventDefault();
		passwordsMismatch = false;
		registerError = false;
		loginSuccess = false;

		if (password !== confirmPassword) passwordsMismatch = true;
		else {
			const res = await register(username, first_name, last_name, password);
			if (res) loginSuccess = true;
			else registerError = true;
		}
	}
</script>


<form on:submit|preventDefault={handleSubmit}>
	<label for="first_name">First name:</label>
	<input type="text" id="first_name" bind:value={first_name} required />

	<label for="last_name">Last Name:</label>
	<input type="text" id="last_name" bind:value={last_name} required />

	<label for="username">Username:</label>
	<input type="text" id="username" bind:value={username} required />

	<label for="password">Password:</label>
	<input type="password" id="password" bind:value={password} required />

	<label for="confirmPassword">Confirm Password:</label>
	<input type="password" id="confirmPassword" bind:value={confirmPassword} required />

	<button type="submit">Register</button>
	{#if passwordsMismatch}
		<div class="row row-center">
			<p class="error">Passwords do not match!</p>
		</div>
	{:else if registerError}
		<div class="row row-center">
			<p class="error">There is an error creating an account.</p>
		</div>
	{/if}
	<div class="row row-center text">
		<p>Already have an account? <a class="link" href="/login">Login here.</a></p>
	</div>

	{#if loginSuccess}
		<div class="modal-overlay" style={loginSuccess ? 'display: block' : 'display: none'}>
			<div class="modal">
				<div class="modal-content column column-center">
					<!-- <h2>Modal Title</h2> -->
					<p>You have successfully created an account!</p>
					<button on:click={() => (loginSuccess = false)}><a href="/login">Log in</a></button>
				</div>
			</div>
		</div>
	{/if}
</form>

<style>
	:global(body) {
		font-family: Arial, sans-serif;
		background-color: #f0f0f0;
	}

	form {
		display: flex;
		flex-direction: column;
		max-width: 400px;
		margin: 3rem auto;
		padding: 1rem;
		border-radius: 4px;
		background-color: #ffffff;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
	}

	label {
		font-weight: bold;
		font-size: 1.1rem;
		margin-bottom: 0.5rem;
	}

	input {
		padding: 0.5rem;
		margin-bottom: 1rem;
		font-size: 1rem;
		border: 1px solid #ccc;
		border-radius: 4px;
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

	button:hover {
		background-color: #0056b3;
	}

	.text {
		margin: 5px 0;
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
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		background-color: white;
		padding: 20px;
		z-index: 10000; /* ensure the modal appears on top of the overlay */
	}

	.modal-content {
		/* add your own styles here */
	}

	.error {
		color: red;
	}
</style>
