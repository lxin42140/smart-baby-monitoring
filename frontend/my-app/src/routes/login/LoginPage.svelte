<script>
	import { login } from '../../api/user';
	import { browser } from '$app/environment';

	let username = '';
	let password = '';
	let hasLoginError = false;

	async function handleSubmit(event) {
		event.preventDefault();
		hasLoginError = false;
		const res = await login(username, password);
		if (res) {
			//navigate to home
			if (browser) {
				localStorage.setItem('username', username);
			}
			window.location.href = '/';
		} else {
			hasLoginError = true;
		}
	}
</script>

<form on:submit|preventDefault={handleSubmit}>
	<h1 class="text-l md:text-4xl font-mono text-center text-blue-500 my-8 px-10">Login to SlumberWatch</h1>
	<label for="username">Username:</label>
	<input type="text" id="email" bind:value={username} required />

	<label for="password">Password:</label>
	<input type="password" id="password" bind:value={password} required />

	<button type="submit">Log In</button>
	{#if hasLoginError}
		<div class="row row-center">
			<p class="error">Invalid username and/or password</p>
		</div>
	{/if}
	<div class="row row-center text">
		<p>Do not have an account? <a class="link" href="/register">Register here.</a></p>
	</div>
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

	.error {
		color: red;
	}
</style>
