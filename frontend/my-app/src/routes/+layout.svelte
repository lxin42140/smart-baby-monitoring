<script>
	// Add any JavaScript code here if needed
	import MoonLogo from '../public/baby_picture_2.svelte';
	import '../app.css';
	import Icon from '@iconify/svelte';
	import { browser } from '$app/environment';
	import { logout } from '../api/user';
	import Alarm from '../components/Alarm.svelte';

	let isLogin = false;
	let redirectOnce = false;
	let username;

	if (browser) {
		username = localStorage.getItem('username');
		isLogin = localStorage.getItem('username') !== null;

		if (!isLogin && (window.location.href !== 'http://127.0.0.1:5173/login' && window.location.href !== 'http://localhost:5173/login') ) {
			window.location.href = '/login';
			redirectOnce = true;
		}
	}

	async function handleLogout() {
		if (confirm('Are you sure you want to log out?') === true) {
			// const res = await logout();
			if (res) {
				window.location.href = '/';
				if (browser) {
					localStorage.removeItem('username');
				}
			}
		}
	}
</script>

<Alarm />
<nav class="p-4 shadow-xl navbar visible">
	<ul class="flex items-center justify-center space-x-8 text-white">
		<div
			class="logo-container pr-5 py-2 relative top-[-0.8rem] bg-center bg-no-repeat bg-contain justify-between w-40 h-30"
		>
			<div class="animate-pulse">
				<MoonLogo />
				<div
					class="inset-0 flex items-center justify-center text-lg font-mono -my-4 text-white-400"
				>
					SlumberWatch
				</div>
			</div>
		</div>
		<li>
			<a
				href="/"
				class="text-lg font-semibold font-mono text-white-400 hover:text-gray-400 transition-colors"
			>
				Home
			</a>
		</li>
		<li>
			<a
				href="/about"
				class="text-lg font-semibold font-mono hover:text-gray-400 transition-colors"
			>
				About
			</a>
		</li>
		{#if isLogin}
			<li>
				<a
					href="/alarms"
					class="text-lg font-semibold font-mono hover:text-gray-400 transition-colors hover:animate-ping"
				>
					Alarms
				</a>
			</li>
			<li>
				<a
					href="/commands"
					class="text-lg font-semibold font-mono hover:text-gray-400 transition-colors hover:animate-ping"
				>
					Commands
				</a>
			</li>
			<li>
				<a
					href="/settings"
					class="text-lg font-semibold font-mono hover:text-gray-400 transition-colors hover:animate-ping"
				>
					Settings
				</a>
			</li>
		{/if}
		{#if !isLogin}
			<li>
				<a
					href="/login"
					class="text-lg font-semibold font-mono hover:text-gray-400 transition-colors"
				>
					Login
				</a>
			</li>
		{:else}
			<li>
				<!-- svelte-ignore a11y-click-events-have-key-events -->
				<!-- svelte-ignore a11y-missing-attribute -->
				<a
					on:click={handleLogout}
					class="text-lg font-semibold font-mono hover:text-gray-400 transition-colors"
				>
					Logout
				</a>
			</li>
		{/if}
	</ul>
	{#if isLogin}
		<div class="profile-container mr-16 column column-center">
			<Icon icon="carbon:user-avatar-filled" width="36" height="36" color="white" />
			<p class="text-white">{username}</p>
		</div>
	{/if}
</nav>

<div style="margin-top: 128.1px;">
	<slot />
</div>

<footer class="bg-gray-800">
	<div
		class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 flex flex-col items-center justify-center"
	>
		<p class="text-gray-400 mb-2">© 2023 SlumberWatch. All rights reserved.</p>
		<div class="flex space-x-4">
			<a href="https://www.instagram.com" class="text-gray-400 hover:text-white">
				<Icon icon="mdi:instagram" color="currentColour" width="24" />
			</a>
			<a href="https://www.facebook.com" class="text-gray-400 hover:text-white">
				<Icon icon="ic:baseline-facebook" color="currentColor" width="24" />
			</a>
			<a href="https://www.twitter.com" class="text-gray-400 hover:text-white">
				<Icon icon="mdi:twitter" color="currentColor" width="24" />
			</a>
		</div>
	</div>
</footer>

<style lang="postcss">
	:global(html) {
		background-color: #243c5a;
	}

	@keyframes gradient-animation {
		0% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
		100% {
			background-position: 0% 50%;
		}
	}

	.navbar {
		background-image: url('/images/banner-starry.png');
		background-size: cover;
		background-repeat: no-repeat;
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		z-index: 999;
		transition: transform 0.3s ease-out;
		transform: translateY(-100%);
	}

	.navbar.visible {
		transform: translateY(0);
	}

	.profile-container {
		position: absolute;
		top: 50%;
		right: 0;
		transform: translateY(-50%);
	}

	/* .nav {
        position: relative; 
    }

	

    .nav::before {
        content: "";
        background-image: url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%23fff' d='M29.6 67.6l-4.4-13.4L15.8 48l13.4-4.4L29.6 30l4.4 13.4 13.4 4.4-13.4 4.4 4.4 13.4-13.4-4.4zm24-9.6l-4.4-13.4-13.4-4.4 13.4-4.4 4.4-13.4 4.4 13.4 13.4 4.4-13.4 4.4 4.4 13.4z'/%3E%3C/svg%3E");
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        animation: stars-animation 20s linear infinite;
        opacity: 0.8;
    }

    @keyframes stars-animation {
        from {
            transform: translateY(0);
        }
        to {
            transform: translateY(-100%);
        }
    } */
</style>
