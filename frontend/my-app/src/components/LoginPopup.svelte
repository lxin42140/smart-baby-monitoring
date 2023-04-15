<script>
	let email = '';
	let password = '';
	let showModal = true;

	function handleSubmit(event) {
		event.preventDefault();
		// Perform login logic here
		showModal = false;
	}
</script>

{#if showModal}
	<div class="login-popup" on:click={() => (showModal = false)} on:keypress>
		<form on:click|stopPropagation on:submit|preventDefault={handleSubmit} on:keypress>
			<span class="close" on:click={() => (showModal = false)} on:keypress>&times;</span>
			<h2 class="font-mono justify-center">Login</h2>
			<label for="email" class="font-mono font-thin">Email:</label>
			<input
				type="email"
				id="email"
				bind:value={email}
				required
				class="focus:invalid:border-pink-500 focus:invalid:ring-pink-500"
			/>

			<label for="password" class="font-mono font-thin">Password:</label>
			<input type="password" id="password" bind:value={password} required />

			<button type="submit" class="my-4 font-mono">Log In</button>
			<button class="font-mono"> Sign Up </button>
		</form>
	</div>
{/if}

<style>
	.login-popup {
		display: flex;
		justify-content: center;
		align-items: center;
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		z-index: 1000;
	}

	form {
		display: flex;
		flex-direction: column;
		max-width: 400px;
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

	.close {
		position: absolute;
		top: 10px;
		right: 10px;
		font-size: 1.5rem;
		font-weight: bold;
		color: #333;
		cursor: pointer;
		transition: color 0.3s;
	}

	.close:hover {
		color: #999;
	}
</style>
