<script lang="ts">
  import { onMount } from 'svelte';

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Lista județelor (din fișierele PDF)
  const counties = [
    'Alba', 'Arad', 'Argeș', 'Bacău', 'Bihor', 'Bistrița-Năsăud', 'Botoșani',
    'Brăila', 'Brașov', 'București', 'Buzău', 'Călărași', 'Caraș-Severin',
    'Cluj', 'Constanța', 'Covasna', 'Dâmbovița', 'Dolj', 'Galați', 'Giurgiu',
    'Gorj', 'Harghita', 'Hunedoara', 'Ialomița', 'Iași', 'Ilfov', 'Maramureș',
    'Mehedinți', 'Mureș', 'Neamț', 'Olt', 'Prahova', 'Sălaj', 'Satu Mare',
    'Sibiu', 'Suceava', 'Teleorman', 'Timiș', 'Tulcea', 'Vâlcea', 'Vaslui',
    'Vrancea'
  ];

  let selectedCounty = counties[0];
  let page = 1;
  let pageSize = 20;
  let monuments: any[] = [];
  let totalCount = 0;
  let totalPages = 0;
  let loading = false;
  let error = '';

  async function fetchMonuments() {
    if (!selectedCounty) return;
    
    loading = true;
    error = '';
    
    try {
      const response = await fetch(
        `${API_URL}/monuments?county=${encodeURIComponent(selectedCounty)}&page=${page}&page_size=${pageSize}`
      );
      
      if (!response.ok) {
        throw new Error('Eroare la încărcarea datelor');
      }
      
      const data = await response.json();
      monuments = data.results;
      totalCount = data.count;
      totalPages = data.total_pages;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Eroare necunoscută';
      monuments = [];
      totalCount = 0;
      totalPages = 0;
    } finally {
      loading = false;
    }
  }

  function handleCountyChange() {
    page = 1;
    fetchMonuments();
  }

  function nextPage() {
    if (page < totalPages) {
      page++;
      fetchMonuments();
    }
  }

  function prevPage() {
    if (page > 1) {
      page--;
      fetchMonuments();
    }
  }

  onMount(() => {
    fetchMonuments();
  });
</script>

<div class="container">
  <h1>Monumente Istorice</h1>
  
  <div class="controls">
    <div class="selector-group">
      <label for="county-select">Județ:</label>
      <select 
        id="county-select" 
        bind:value={selectedCounty} 
        on:change={handleCountyChange}
        disabled={loading}
      >
        {#each counties as county}
          <option value={county}>{county}</option>
        {/each}
      </select>
      
      <div class="pagination-controls">
        <button 
          on:click={prevPage} 
          disabled={page === 1 || loading}
          class="btn"
        >
          ← Anterior
        </button>
        <span class="page-info">Pagina {page} din {totalPages || 1}</span>
        <button 
          on:click={nextPage} 
          disabled={page >= totalPages || loading}
          class="btn"
        >
          Următor →
        </button>
      </div>
    </div>
    
    <div class="count-info">
      <span>Total: {totalCount} monumente</span>
      <span>|</span>
      <span>Pagina curentă: {monuments.length} monumente</span>
    </div>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading}
    <div class="loading">Se încarcă...</div>
  {:else if monuments.length === 0}
    <div class="empty">Nu există monumente pentru acest județ.</div>
  {:else}
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Nr. crt.</th>
            <th>Cod LMI</th>
            <th>Denumire</th>
            <th>Localitate</th>
            <th>Adresă</th>
            <th>Datare</th>
          </tr>
        </thead>
        <tbody>
          {#each monuments as monument}
            <tr>
              <td>{monument.id || '-'}</td>
              <td>{monument.lmi_code || '-'}</td>
              <td>{monument.name || '-'}</td>
              <td>{monument.city || '-'}</td>
              <td>{monument.address || '-'}</td>
              <td>{monument.dating || '-'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    
    <div class="pagination-bottom">
      <button 
        on:click={prevPage} 
        disabled={page === 1 || loading}
        class="btn"
      >
        ← Anterior
      </button>
      <span class="page-info">Pagina {page} din {totalPages || 1}</span>
      <button 
        on:click={nextPage} 
        disabled={page >= totalPages || loading}
        class="btn"
      >
        Următor →
      </button>
    </div>
  {/if}
</div>

<style>
  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
  }

  h1 {
    color: #2c3e50;
    margin-bottom: 2rem;
    font-size: 2rem;
  }

  .controls {
    margin-bottom: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .selector-group {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  label {
    font-weight: 600;
    color: #34495e;
  }

  select {
    padding: 0.5rem 1rem;
    font-size: 1rem;
    border: 2px solid #bdc3c7;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    min-width: 200px;
  }

  select:disabled {
    background: #ecf0f1;
    cursor: not-allowed;
  }

  select:hover:not(:disabled) {
    border-color: #3498db;
  }

  .pagination-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-left: auto;
  }

  .count-info {
    display: flex;
    gap: 0.5rem;
    color: #7f8c8d;
    font-size: 0.9rem;
  }

  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn:hover:not(:disabled) {
    background: #2980b9;
  }

  .btn:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
  }

  .page-info {
    font-weight: 500;
    color: #34495e;
  }

  .error {
    padding: 1rem;
    background: #e74c3c;
    color: white;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .loading {
    text-align: center;
    padding: 2rem;
    color: #7f8c8d;
    font-size: 1.1rem;
  }

  .empty {
    text-align: center;
    padding: 2rem;
    color: #7f8c8d;
    font-size: 1.1rem;
  }

  .table-container {
    overflow-x: auto;
    margin-bottom: 1.5rem;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background: white;
  }

  thead {
    background: #34495e;
    color: white;
  }

  th {
    padding: 1rem;
    text-align: left;
    font-weight: 600;
    white-space: nowrap;
  }

  tbody tr {
    border-bottom: 1px solid #ecf0f1;
  }

  tbody tr:hover {
    background: #f8f9fa;
  }

  td {
    padding: 0.75rem 1rem;
    color: #2c3e50;
  }

  .pagination-bottom {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  @media (max-width: 768px) {
    .container {
      padding: 1rem;
    }

    .selector-group {
      flex-direction: column;
      align-items: stretch;
    }

    .pagination-controls {
      margin-left: 0;
      justify-content: center;
    }

    .table-container {
      font-size: 0.85rem;
    }

    th, td {
      padding: 0.5rem;
    }
  }
</style>
