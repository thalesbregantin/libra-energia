// ============================================================================
// LIBRA ENERGIA - DASHBOARD JAVASCRIPT
// ============================================================================

// Global variables
let allLeads = [];
let filteredLeads = [];
let levelChart = null;
let scoreChart = null;
let campaignRunning = false;

// API Configuration
const API_BASE = window.location.origin.includes('localhost') 
    ? 'http://localhost:8000' 
    : window.location.origin;

console.log('🔧 API Base configurada:', API_BASE);

// ============================================================================
// INITIALIZATION
// ============================================================================

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando dashboard...');
    testConnectivity();
    loadData();
    setupEventListeners();
});

// ============================================================================
// API CONNECTIVITY
// ============================================================================

// Test API connectivity
async function testConnectivity() {
    console.log('🔍 Testando conectividade com API...');
    try {
        const response = await fetch(`${API_BASE}/`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API conectada:', data.message);
            return true;
        } else {
            console.log('❌ API retornou erro:', response.status);
            return false;
        }
    } catch (error) {
        console.log('❌ Erro de conectividade:', error.message);
        return false;
    }
}

// ============================================================================
// DATA LOADING
// ============================================================================

// Load data from API
async function loadData() {
    console.log('📡 Carregando dados...');
    updateStatus('Carregando dados...', 'loading');
    
    try {
        // Tentar endpoint simplificado primeiro
        const response = await fetch(`${API_BASE}/leads`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Dados carregados:', result);
        
        if (result.success && result.data) {
            allLeads = result.data;
            filteredLeads = [...allLeads];
            updateDashboard();
            updateStatus(`Dados carregados: ${allLeads.length} leads (${result.source})`, 'success');
            
            // Cache no localStorage
            localStorage.setItem('leads', JSON.stringify(allLeads));
            localStorage.setItem('leads_timestamp', new Date().toISOString());
        } else {
            throw new Error('Resposta inválida da API');
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        updateStatus('Erro ao carregar dados da API', 'error');
        
        // Fallback: tentar endpoint completo
        try {
            const response = await fetch(`${API_BASE}/api/leads`);
            if (response.ok) {
                const result = await response.json();
                if (result.success && result.data) {
                    allLeads = result.data;
                    filteredLeads = [...allLeads];
                    updateDashboard();
                    updateStatus(`Dados carregados: ${allLeads.length} leads (fallback)`, 'success');
                    return;
                }
            }
        } catch (fallbackError) {
            console.log('❌ Fallback também falhou:', fallbackError);
        }
        
        // Último recurso: carregar arquivo local
        await loadLocalData();
    }
}

// Load local data as fallback
async function loadLocalData() {
    console.log('📁 Tentando carregar dados locais...');
    
    // Primeiro, tentar localStorage
    const cachedLeads = localStorage.getItem('leads');
    const cachedTimestamp = localStorage.getItem('leads_timestamp');
    
    if (cachedLeads && cachedTimestamp) {
        const cacheAge = new Date() - new Date(cachedTimestamp);
        if (cacheAge < 5 * 60 * 1000) { // 5 minutos
            console.log('📦 Carregando dados do cache...');
            allLeads = JSON.parse(cachedLeads);
            filteredLeads = [...allLeads];
            updateDashboard();
            updateStatus(`Dados carregados do cache: ${allLeads.length} leads`, 'warning');
            return;
        }
    }
    
    const leadFiles = [
        'leads_coletados_20250904_123747.json',  // Arquivo mais recente da campanha
        'leads_coletados_20250904_115438.json',
        'leads_coletados_20250903_213934.json',
        'leads_coletados_20250903_200444.json',
        'leads_coletados_20250903_193153.json',
        'leads_coletados_20250903_171709.json'
    ];
    
    for (const filename of leadFiles) {
        try {
            const response = await fetch(filename);
            if (response.ok) {
                const data = await response.json();
                if (Array.isArray(data) && data.length > 0) {
                    console.log(`✅ Dados locais carregados: ${filename}`);
                    allLeads = data;
                    filteredLeads = [...allLeads];
                    updateDashboard();
                    updateStatus(`Dados locais carregados: ${allLeads.length} leads`, 'success');
                    return;
                }
            }
        } catch (error) {
            console.log(`❌ Erro ao carregar ${filename}:`, error);
        }
    }
    
    // Se não conseguiu carregar nada, usar dados de exemplo
    console.log('⚠️ Usando dados de exemplo...');
    allLeads = getSampleData();
    filteredLeads = [...allLeads];
    updateDashboard();
    updateStatus('Usando dados de exemplo', 'warning');
}

// Get sample data
function getSampleData() {
    return [
        {
            nome: "Supermercado Exemplo Ltda",
            telefone: "(11) 99999-9999",
            website: "https://exemplo.com",
            endereco: "Rua Exemplo, 123 - São Paulo, SP",
            score: 5.5,
            nivel: "A",
            qualificado: true,
            fonte: "Google Places"
        },
        {
            nome: "Padaria do João",
            telefone: "(11) 88888-8888",
            website: "https://padariadojoao.com",
            endereco: "Av. Principal, 456 - São Paulo, SP",
            score: 4.2,
            nivel: "B",
            qualificado: true,
            fonte: "Instagram"
        },
        {
            nome: "Academia Fitness",
            telefone: "(11) 77777-7777",
            website: "https://academiafitness.com",
            endereco: "Rua da Saúde, 789 - São Paulo, SP",
            score: 3.8,
            nivel: "C",
            qualificado: false,
            fonte: "Google Places"
        }
    ];
}

// ============================================================================
// UI UPDATES
// ============================================================================

// Update status bar
function updateStatus(message, type) {
    const statusIcon = document.getElementById('status-icon');
    const statusText = document.getElementById('status-text');
    const lastUpdate = document.getElementById('last-update');
    const statusBar = document.getElementById('status-bar');
    
    statusText.textContent = message;
    lastUpdate.textContent = `Última atualização: ${new Date().toLocaleString('pt-BR')}`;
    
    // Update icon color based on type
    statusIcon.className = 'w-3 h-3 rounded-full';
    statusBar.className = 'bg-white rounded-lg shadow-sm border p-4';
    
    switch (type) {
        case 'success':
            statusIcon.classList.add('bg-green-500');
            break;
        case 'error':
            statusIcon.classList.add('bg-red-500');
            statusBar.classList.add('border-red-400');
            break;
        case 'warning':
            statusIcon.classList.add('bg-yellow-500');
            statusBar.classList.add('border-yellow-400');
            break;
        case 'loading':
            statusIcon.classList.add('bg-blue-500');
            break;
        default:
            statusIcon.classList.add('bg-gray-500');
    }
}

// Update dashboard metrics
function updateDashboard() {
    console.log('📊 Atualizando dashboard...');
    
    if (!allLeads || allLeads.length === 0) {
        console.log('⚠️ Nenhum lead disponível');
        return;
    }
    
    // Calculate metrics
    const totalLeads = allLeads.length;
    const qualifiedLeads = allLeads.filter(lead => lead.qualificado).length;
    const avgScore = allLeads.reduce((sum, lead) => sum + (lead.score || 0), 0) / totalLeads;
    const qualificationRate = (qualifiedLeads / totalLeads) * 100;
    
    // Update metric cards
    document.getElementById('total-leads').textContent = totalLeads;
    document.getElementById('qualified-leads').textContent = qualifiedLeads;
    document.getElementById('avg-score').textContent = `${avgScore.toFixed(1)}/6`;
    document.getElementById('qualification-rate').textContent = `${qualificationRate.toFixed(1)}%`;
    
    // Update charts
    updateCharts();
    
    // Update table
    updateTable();
    
    console.log('✅ Dashboard atualizado');
}

// Update charts
function updateCharts() {
    // Level distribution chart
    const levelData = {};
    allLeads.forEach(lead => {
        const level = lead.nivel || 'C';
        levelData[level] = (levelData[level] || 0) + 1;
    });
    
    const levelCtx = document.getElementById('levelChart').getContext('2d');
    if (levelChart) levelChart.destroy();
    
    levelChart = new Chart(levelCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(levelData),
            datasets: [{
                data: Object.values(levelData),
                backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // Score chart
    const scoreCtx = document.getElementById('scoreChart').getContext('2d');
    if (scoreChart) scoreChart.destroy();
    
    const topLeads = allLeads
        .sort((a, b) => (b.score || 0) - (a.score || 0))
        .slice(0, 10);
    
    scoreChart = new Chart(scoreCtx, {
        type: 'bar',
        data: {
            labels: topLeads.map(lead => lead.nome.substring(0, 15) + '...'),
            datasets: [{
                label: 'Score',
                data: topLeads.map(lead => lead.score || 0),
                backgroundColor: '#3B82F6',
                borderColor: '#1D4ED8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 6
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Update table
function updateTable() {
    const tbody = document.getElementById('leads-table');
    tbody.innerHTML = '';
    
    if (filteredLeads.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                    Nenhum lead encontrado
                </td>
            </tr>
        `;
        return;
    }
    
    filteredLeads.forEach(lead => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        
        const qualificadoBadge = lead.qualificado 
            ? '<span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Sim</span>'
            : '<span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Não</span>';
        
        const nivelBadge = `<span class="px-2 py-1 text-xs font-medium bg-${getNivelColor(lead.nivel)}-100 text-${getNivelColor(lead.nivel)}-800 rounded-full">${lead.nivel || 'C'}</span>`;
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${lead.nome || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${lead.telefone || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${lead.website ? `<a href="${lead.website}" target="_blank" class="text-blue-600 hover:text-blue-800">${lead.website}</a>` : 'N/A'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${(lead.score || 0).toFixed(1)}/6</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${nivelBadge}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${qualificadoBadge}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// Get color for level
function getNivelColor(nivel) {
    switch (nivel) {
        case 'A': return 'green';
        case 'B': return 'yellow';
        case 'C': return 'red';
        default: return 'gray';
    }
}

// ============================================================================
// FILTERS AND SEARCH
// ============================================================================

// Setup event listeners
function setupEventListeners() {
    document.getElementById('search-input').addEventListener('input', applyFilters);
    document.getElementById('level-filter').addEventListener('change', applyFilters);
}

// Apply filters
function applyFilters() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const levelFilter = document.getElementById('level-filter').value;
    
    filteredLeads = allLeads.filter(lead => {
        const matchesSearch = !searchTerm || 
            (lead.nome && lead.nome.toLowerCase().includes(searchTerm)) ||
            (lead.telefone && lead.telefone.includes(searchTerm)) ||
            (lead.endereco && lead.endereco.toLowerCase().includes(searchTerm));
        
        const matchesLevel = !levelFilter || lead.nivel === levelFilter;
        
        return matchesSearch && matchesLevel;
    });
    
    updateTable();
}

// Clear filters
function clearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('level-filter').value = '';
    filteredLeads = [...allLeads];
    updateTable();
}

// ============================================================================
// ACTIONS
// ============================================================================

// Refresh data
async function refreshData() {
    console.log('🔄 Atualizando dados...');
    
    // Show loading spinner
    const refreshIcon = document.getElementById('refresh-icon');
    const originalIcon = refreshIcon.textContent;
    refreshIcon.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        await loadData();
    } finally {
        // Restore original icon
        refreshIcon.textContent = originalIcon;
    }
}

// Run campaign
async function runCampaign() {
    if (campaignRunning) {
        console.log('⚠️ Campanha já está em execução');
        return;
    }
    
    console.log('🚀 Iniciando campanha...');
    campaignRunning = true;
    
    // Show campaign progress
    document.getElementById('campaign-progress').classList.remove('hidden');
    document.getElementById('campaign-btn').disabled = true;
    document.getElementById('campaign-text').textContent = 'Executando...';
    document.getElementById('campaign-icon').innerHTML = '<div class="loading-spinner"></div>';
    
    // Clear previous log
    document.getElementById('campaign-log').innerHTML = '';
    
    try {
        // Simulate campaign steps
        await simulateCampaignSteps();
        
        // Call real API
        const response = await fetch(`${API_BASE}/api/campaign/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Campanha executada:', result);
        
        if (result.success) {
            addCampaignLog('✅ Campanha executada com sucesso!');
            updateCampaignProgress(100, 'Finalizado');
            
            // Update campaign metrics
            if (result.data) {
                document.getElementById('campaign-leads').textContent = result.data.leads_collected || 0;
                document.getElementById('campaign-qualified').textContent = result.data.leads_qualified || 0;
                document.getElementById('campaign-score').textContent = '5.0'; // Default score
            }
            
            // Reload data to show new leads
            setTimeout(() => {
                addCampaignLog('🔄 Recarregando dados...');
                loadData();
            }, 1000);
        } else {
            throw new Error(result.message || 'Erro na campanha');
        }
        
    } catch (error) {
        console.error('❌ Erro na campanha:', error);
        addCampaignLog(`❌ Erro: ${error.message}`);
        updateCampaignProgress(0, 'Erro');
    } finally {
        campaignRunning = false;
        document.getElementById('campaign-btn').disabled = false;
        document.getElementById('campaign-text').textContent = 'Rodar Campanha';
        document.getElementById('campaign-icon').textContent = '🚀';
    }
}

// Simulate campaign steps
async function simulateCampaignSteps() {
    const steps = [
        { progress: 10, text: 'Configurando parâmetros da campanha...' },
        { progress: 25, text: 'Conectando com API da Libra Energia...' },
        { progress: 40, text: 'Executando campanha de coleta...' },
        { progress: 60, text: 'Processando resultados da campanha...' },
        { progress: 80, text: 'Finalizando campanha...' },
        { progress: 90, text: 'Chamando API para executar campanha...' }
    ];
    
    for (const step of steps) {
        if (!campaignRunning) break;
        
        updateCampaignProgress(step.progress, step.text);
        addCampaignLog(step.text);
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}

// Update campaign progress
function updateCampaignProgress(progress, text) {
    document.getElementById('progress-bar').style.width = `${progress}%`;
    document.getElementById('progress-percent').textContent = `${progress}%`;
    document.getElementById('progress-text').textContent = text;
}

// Add campaign log entry
function addCampaignLog(message) {
    const log = document.getElementById('campaign-log');
    const timestamp = new Date().toLocaleTimeString('pt-BR');
    const entry = document.createElement('div');
    entry.textContent = `[${timestamp}] ${message}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

// Stop campaign
function stopCampaign() {
    campaignRunning = false;
    document.getElementById('campaign-progress').classList.add('hidden');
    document.getElementById('campaign-btn').disabled = false;
    document.getElementById('campaign-text').textContent = 'Rodar Campanha';
    document.getElementById('campaign-icon').textContent = '🚀';
}
