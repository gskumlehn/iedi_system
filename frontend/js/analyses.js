// API Base URL
const API_BASE = '/api/analysis';

// State
let analyses = [];
let banks = [];
let currentAnalysis = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadBanks();
    loadAnalyses();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    document.getElementById('btnNewAnalysis').addEventListener('click', openNewAnalysisModal);
    document.getElementById('formNewAnalysis').addEventListener('submit', handleCreateAnalysis);
    document.getElementById('customPeriod').addEventListener('change', toggleCustomPeriod);
    document.getElementById('btnAddBank').addEventListener('click', addBankPeriod);
    document.getElementById('filterStatus').addEventListener('change', filterAnalyses);
}

// Load Data
async function loadBanks() {
    try {
        const response = await fetch('/api/banks');
        banks = await response.json();
    } catch (error) {
        console.error('Erro ao carregar bancos:', error);
        showNotification('Erro ao carregar lista de bancos', 'error');
    }
}

async function loadAnalyses() {
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const tableBody = document.getElementById('analysesTableBody');
    
    loadingState.style.display = 'block';
    emptyState.style.display = 'none';
    
    try {
        const response = await fetch(API_BASE);
        analyses = await response.json();
        
        loadingState.style.display = 'none';
        
        if (analyses.length === 0) {
            emptyState.style.display = 'block';
            tableBody.innerHTML = '';
        } else {
            renderAnalysesTable(analyses);
        }
    } catch (error) {
        console.error('Erro ao carregar análises:', error);
        loadingState.style.display = 'none';
        showNotification('Erro ao carregar análises', 'error');
    }
}

function renderAnalysesTable(data) {
    const tbody = document.getElementById('analysesTableBody');
    tbody.innerHTML = '';
    
    data.forEach(analysis => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${analysis.name}</strong></td>
            <td>${analysis.query_name}</td>
            <td>${formatPeriod(analysis.start_date, analysis.end_date)}</td>
            <td><span class="status-badge status-${analysis.status}">${formatStatus(analysis.status)}</span></td>
            <td>${analysis.bank_count || '-'}</td>
            <td>${formatDate(analysis.created_at)}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-action btn-view" onclick="viewAnalysis('${analysis.id}')">
                        Ver Detalhes
                    </button>
                    <button class="btn-action btn-delete" onclick="deleteAnalysis('${analysis.id}')">
                        Excluir
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Modal Functions
function openNewAnalysisModal() {
    const modal = document.getElementById('modalNewAnalysis');
    modal.classList.add('active');
    
    // Reset form
    document.getElementById('formNewAnalysis').reset();
    document.getElementById('bankPeriodsContainer').innerHTML = '';
    
    // Add first bank period
    addBankPeriod();
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
}

function toggleCustomPeriod() {
    const isCustom = document.getElementById('customPeriod').checked;
    const globalSection = document.getElementById('globalPeriodSection');
    const bankPeriods = document.querySelectorAll('.bank-period-dates');
    
    if (isCustom) {
        globalSection.style.display = 'none';
        bankPeriods.forEach(el => el.style.display = 'grid');
    } else {
        globalSection.style.display = 'block';
        bankPeriods.forEach(el => el.style.display = 'none');
    }
}

// Bank Period Management
let bankPeriodCounter = 0;

function addBankPeriod() {
    const container = document.getElementById('bankPeriodsContainer');
    const isCustom = document.getElementById('customPeriod').checked;
    const periodId = `bankPeriod${bankPeriodCounter++}`;
    
    const periodHtml = `
        <div class="bank-period-item" id="${periodId}">
            <div class="bank-period-header">
                <h4>Banco ${bankPeriodCounter}</h4>
                <button type="button" class="btn-remove" onclick="removeBankPeriod('${periodId}')">
                    Remover
                </button>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Banco *</label>
                    <select class="bank-select" required>
                        <option value="">Selecione...</option>
                        ${banks.map(b => `<option value="${b.id}">${b.name}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>Categoria Brandwatch *</label>
                    <input type="text" class="category-input" placeholder="Ex: Banco do Brasil" required>
                </div>
            </div>
            <div class="form-row bank-period-dates" style="display: ${isCustom ? 'grid' : 'none'}">
                <div class="form-group">
                    <label>Data Início</label>
                    <input type="datetime-local" class="start-date-input">
                </div>
                <div class="form-group">
                    <label>Data Fim</label>
                    <input type="datetime-local" class="end-date-input">
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', periodHtml);
}

function removeBankPeriod(periodId) {
    const element = document.getElementById(periodId);
    if (element) {
        element.remove();
    }
}

// Form Submission
async function handleCreateAnalysis(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('analysisName').value,
        query_name: document.getElementById('queryName').value,
        custom_period: document.getElementById('customPeriod').checked,
        bank_periods: []
    };
    
    // Global period
    if (!formData.custom_period) {
        formData.start_date = document.getElementById('globalStartDate').value;
        formData.end_date = document.getElementById('globalEndDate').value;
    }
    
    // Bank periods
    const periodItems = document.querySelectorAll('.bank-period-item');
    periodItems.forEach(item => {
        const bankId = item.querySelector('.bank-select').value;
        const category = item.querySelector('.category-input').value;
        
        const period = {
            bank_id: bankId,
            category_detail: category
        };
        
        if (formData.custom_period) {
            period.start_date = item.querySelector('.start-date-input').value;
            period.end_date = item.querySelector('.end-date-input').value;
        } else {
            period.start_date = formData.start_date;
            period.end_date = formData.end_date;
        }
        
        formData.bank_periods.push(period);
    });
    
    try {
        const response = await fetch(API_BASE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Erro ao criar análise');
        }
        
        const result = await response.json();
        
        showNotification('Análise criada com sucesso!', 'success');
        closeModal('modalNewAnalysis');
        loadAnalyses();
    } catch (error) {
        console.error('Erro ao criar análise:', error);
        showNotification('Erro ao criar análise', 'error');
    }
}

// View Analysis Details
async function viewAnalysis(analysisId) {
    try {
        const response = await fetch(`${API_BASE}/${analysisId}`);
        const data = await response.json();
        
        currentAnalysis = data;
        renderAnalysisDetails(data);
        
        const modal = document.getElementById('modalAnalysisDetails');
        modal.classList.add('active');
    } catch (error) {
        console.error('Erro ao carregar detalhes:', error);
        showNotification('Erro ao carregar detalhes da análise', 'error');
    }
}

function renderAnalysisDetails(data) {
    // General info
    document.getElementById('detailsTitle').textContent = data.name;
    document.getElementById('detailName').textContent = data.name;
    document.getElementById('detailQuery').textContent = data.query_name;
    document.getElementById('detailPeriod').textContent = formatPeriod(data.start_date, data.end_date);
    
    const statusBadge = document.getElementById('detailStatus');
    statusBadge.textContent = formatStatus(data.status);
    statusBadge.className = `status-badge status-${data.status}`;
    
    // Bank periods
    const bankPeriodsBody = document.getElementById('detailBankPeriods');
    bankPeriodsBody.innerHTML = '';
    
    if (data.bank_periods && data.bank_periods.length > 0) {
        data.bank_periods.forEach(bp => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${getBankName(bp.bank_id)}</td>
                <td>${bp.category_detail}</td>
                <td>${formatPeriod(bp.start_date, bp.end_date)}</td>
                <td>${bp.total_mentions || 0}</td>
            `;
            bankPeriodsBody.appendChild(row);
        });
    } else {
        bankPeriodsBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #6c757d;">Nenhum período cadastrado</td></tr>';
    }
    
    // IEDI Results
    const resultsBody = document.getElementById('detailResults');
    resultsBody.innerHTML = '';
    
    if (data.results && data.results.length > 0) {
        data.results.forEach(result => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${getBankName(result.bank_id)}</strong></td>
                <td>${result.total_volume}</td>
                <td style="color: #28a745;">${result.positive_volume}</td>
                <td style="color: #dc3545;">${result.negative_volume}</td>
                <td style="color: #6c757d;">${result.neutral_volume}</td>
                <td>${result.average_iedi.toFixed(2)}</td>
                <td><strong>${result.final_iedi.toFixed(2)}</strong></td>
                <td>${result.positivity_rate.toFixed(1)}%</td>
            `;
            resultsBody.appendChild(row);
        });
    } else {
        resultsBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #6c757d;">Nenhum resultado disponível</td></tr>';
    }
}

// Delete Analysis
async function deleteAnalysis(analysisId) {
    if (!confirm('Tem certeza que deseja excluir esta análise? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/${analysisId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Erro ao excluir análise');
        }
        
        showNotification('Análise excluída com sucesso!', 'success');
        loadAnalyses();
    } catch (error) {
        console.error('Erro ao excluir análise:', error);
        showNotification('Erro ao excluir análise', 'error');
    }
}

// Filter
function filterAnalyses() {
    const status = document.getElementById('filterStatus').value;
    
    if (!status) {
        renderAnalysesTable(analyses);
    } else {
        const filtered = analyses.filter(a => a.status === status);
        renderAnalysesTable(filtered);
    }
}

// Utility Functions
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatPeriod(startDate, endDate) {
    if (!startDate || !endDate) return '-';
    const start = new Date(startDate);
    const end = new Date(endDate);
    return `${start.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })} - ${end.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })}`;
}

function formatStatus(status) {
    const statusMap = {
        'pending': 'Pendente',
        'processing': 'Processando',
        'completed': 'Concluída',
        'failed': 'Falha'
    };
    return statusMap[status] || status;
}

function getBankName(bankId) {
    const bank = banks.find(b => b.id === bankId);
    return bank ? bank.name : bankId;
}

function showNotification(message, type = 'info') {
    // Simple notification (can be replaced with a toast library)
    alert(message);
}

// Close modal on outside click
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}
