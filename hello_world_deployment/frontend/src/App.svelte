<script>
  import { onMount } from 'svelte'
  
  let helloData = null
  let pingData = null
  let healthData = null
  let loading = false
  let error = null
  
  
const API_URL = '/api';   // Relative path
  
  onMount(async () => {
    await fetchHello()
  })
  
  async function fetchHello() {
    try {
      loading = true
      error = null
      console.log('Fetching from:', `${API_URL}/`)
      const response = await fetch(`${API_URL}/`)
      console.log('Response status:', response.status)
      console.log('Response headers:', response.headers)
      
      const text = await response.text()
      console.log('Response body:', text)
      
      if (!response.ok) throw new Error(`Failed to fetch hello: ${response.status}`)
      helloData = JSON.parse(text)
    } catch (err) {
      console.error('Error:', err)
      error = err.message
    } finally {
      loading = false
    }
  }
  
  async function fetchPing() {
    try {
      loading = true
      error = null
      const response = await fetch(`${API_URL}/ping`)
      if (!response.ok) throw new Error('Failed to fetch ping')
      pingData = await response.json()
    } catch (err) {
      error = err.message
    } finally {
      loading = false
    }
  }
  
  async function fetchHealth() {
    try {
      loading = true
      error = null
      const response = await fetch(`${API_BASE}/health`)
      if (!response.ok) throw new Error('Failed to fetch health')
      healthData = await response.json()
    } catch (err) {
      error = err.message
    } finally {
      loading = false
    }
  }
</script>

<main>
  <h1>🚀 hello-deploy</h1>
  
  <div class="container">
    <button on:click={fetchHello} disabled={loading}>
      {loading ? 'Loading...' : 'Get Hello'}
    </button>
    
    <button on:click={fetchPing} disabled={loading}>
      {loading ? 'Loading...' : 'Ping'}
    </button>
    
    <button on:click={fetchHealth} disabled={loading}>
      {loading ? 'Loading...' : 'Health Check'}
    </button>
  </div>
  
  {#if error}
    <div class="error">❌ Error: {error}</div>
  {/if}
  
  {#if helloData}
    <div class="response">
      <h2>Hello Response:</h2>
      <pre>{JSON.stringify(helloData, null, 2)}</pre>
    </div>
  {/if}
  
  {#if pingData}
    <div class="response">
      <h2>Ping Response:</h2>
      <pre>{JSON.stringify(pingData, null, 2)}</pre>
    </div>
  {/if}
  
  {#if healthData}
    <div class="response">
      <h2>Health Check Response:</h2>
      <pre>{JSON.stringify(healthData, null, 2)}</pre>
    </div>
  {/if}
</main>

<style>
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    margin: 0;
    padding: 20px;
    background: #f5f5f5;
  }
  
  main {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  h1 {
    color: #333;
    text-align: center;
    margin-bottom: 30px;
  }
  
  h2 {
    color: #555;
    margin-top: 20px;
  }
  
  .container {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  button {
    padding: 10px 20px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s;
  }
  
  button:hover:not(:disabled) {
    background: #0056b3;
  }
  
  button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
  
  .error {
    background: #f8d7da;
    color: #721c24;
    padding: 12px;
    border-radius: 5px;
    margin-bottom: 20px;
    border: 1px solid #f5c6cb;
  }
  
  .response {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 5px;
    border-left: 4px solid #007bff;
    margin-bottom: 20px;
  }
  
  pre {
    background: #e9ecef;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 13px;
  }
</style>
