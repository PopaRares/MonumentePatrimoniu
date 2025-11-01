<script lang="ts">
	import { onMount } from 'svelte';

	let data = [];
	let loading = true;
	let error = '';

	const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

	async function fetchData() {
		try {
			loading = true;
			const response = await fetch(`${apiUrl}/api/data`);
			const result = await response.json();
			data = result.data || [];
			error = '';
		} catch (err) {
			error = 'Failed to fetch data';
			console.error(err);
		} finally {
			loading = false;
		}
	}

	async function checkHealth() {
		try {
			const response = await fetch(`${apiUrl}/health`);
			const result = await response.json();
			console.log('Backend health:', result);
		} catch (err) {
			console.error('Health check failed:', err);
		}
	}

	onMount(() => {
		checkHealth();
		fetchData();
	});
</script>

<svelte:head>
	<title>Patrimoniu</title>
</svelte:head>

<main>
	<h1>Patrimoniu Frontend</h1>
	<p>Welcome to the Patrimoniu application</p>

	<div class="status">
		<button on:click={fetchData} disabled={loading}>
			{loading ? 'Loading...' : 'Refresh Data'}
		</button>
	</div>

	{#if error}
		<p class="error">{error}</p>
	{/if}

	{#if loading}
		<p>Loading data...</p>
	{:else if data.length > 0}
		<div class="data-container">
			<h2>Data from MongoDB:</h2>
			<pre>{JSON.stringify(data, null, 2)}</pre>
		</div>
	{:else}
		<p>No data available. Backend is connected and ready!</p>
	{/if}
</main>

<style>
	main {
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem;
		font-family: system-ui, -apple-system, sans-serif;
	}

	h1 {
		color: #333;
		margin-bottom: 0.5rem;
	}

	.status {
		margin: 2rem 0;
	}

	button {
		background: #4f46e5;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 0.5rem;
		cursor: pointer;
		font-size: 1rem;
	}

	button:hover:not(:disabled) {
		background: #4338ca;
	}

	button:disabled {
		background: #9ca3af;
		cursor: not-allowed;
	}

	.error {
		color: #dc2626;
		background: #fee2e2;
		padding: 1rem;
		border-radius: 0.5rem;
		margin: 1rem 0;
	}

	.data-container {
		margin-top: 2rem;
	}

	pre {
		background: #f3f4f6;
		padding: 1rem;
		border-radius: 0.5rem;
		overflow-x: auto;
	}
</style>

