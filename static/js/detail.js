/**
 * IEDI - Detail Page (Analysis Details)
 */

let currentAnalysisId = null;

// Load analysis details on page load
document.addEventListener('DOMContentLoaded', () => {
    // Get analysis ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    currentAnalysisId = urlParams.get('id');
    
    if (!currentAnalysisId) {
        showError('error', 'ID da análise não fornecido');
        hideLoading('loading');
        return;
    }
    
    loadAnalysisDetails();
});

/**
 * Load and display analysis details
 */
async function loadAnalysisDetails() {
    showLoading('loading');
    hideError('error');
    document.getElementById('details-container').style.display = 'none';
    
    try {
        // Load analysis info
        const analysisData = await API.getAnalysis(currentAnalysisId);
        const analysis = analysisData.analysis;
        
        // Load bank analyses
        const bankData = await API.getBankAnalyses(currentAnalysisId);
        const bankAnalyses = bankData.bank_analyses || [];
        
        hideLoading('loading');
        
        // Render analysis info
        renderAnalysisInfo(analysis);
        
        // Show processing message if not completed
        if (analysis.status === 'PENDING' || analysis.status === 'PROCESSING') {
            document.getElementById('processing-message').style.display = 'flex';
            document.getElementById('results-container').style.display = 'none';
        } else {
            document.getElementById('processing-message').style.display = 'none';
            
            // Render bank results
            if (bankAnalyses.length === 0) {
                document.getElementById('results-container').style.display = 'block';
                document.getElementById('no-results').style.display = 'block';
                document.getElementById('results-grid').style.display = 'none';
            } else {
                renderBankResults(bankAnalyses);
                document.getElementById('results-container').style.display = 'block';
                document.getElementById('no-results').style.display = 'none';
                document.getElementById('results-grid').style.display = 'grid';
            }
        }
        
        document.getElementById('details-container').style.display = 'block';
        
    } catch (error) {
        hideLoading('loading');
        showError('error', error.message || 'Erro ao carregar detalhes da análise');
    }
}

/**
 * Render analysis information
 */
function renderAnalysisInfo(analysis) {
    // Status badge
    const statusBadge = document.getElementById('status-badge');
    statusBadge.className = `badge ${getStatusBadgeClass(analysis.status)}`;
    statusBadge.textContent = getStatusLabel(analysis.status);
    
    // Analysis info
    document.getElementById('analysis-name').textContent = analysis.name;
    document.getElementById('analysis-query').textContent = analysis.query_name || '-';
    document.getElementById('analysis-type').textContent = getTypeLabel(analysis.is_custom_dates);
    document.getElementById('analysis-created').textContent = formatDate(analysis.created_at);
}

/**
 * Render bank analysis results
 */
function renderBankResults(bankAnalyses) {
    const resultsGrid = document.getElementById('results-grid');
    resultsGrid.innerHTML = '';
    
    bankAnalyses.forEach(bankAnalysis => {
        const card = createBankResultCard(bankAnalysis);
        resultsGrid.appendChild(card);
    });
}

/**
 * Create bank result card element
 */
function createBankResultCard(bankAnalysis) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    const bankName = formatBankName(bankAnalysis.bank_name);
    const period = `${formatDate(bankAnalysis.start_date)} - ${formatDate(bankAnalysis.end_date)}`;
    
    card.innerHTML = `
        <div class="result-header">
            <div>
                <div class="result-bank-name">${bankName}</div>
                <div class="result-period">${period}</div>
            </div>
        </div>
        <div class="result-metrics">
            <div class="metric">
                <span class="metric-label">Total Menções</span>
                <span class="metric-value">${bankAnalysis.total_mentions || 0}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volume Positivo</span>
                <span class="metric-value">${formatVolume(bankAnalysis.positive_volume)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Volume Negativo</span>
                <span class="metric-value">${formatVolume(bankAnalysis.negative_volume)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">IEDI Médio</span>
                <span class="metric-value">${formatIEDI(bankAnalysis.iedi_mean)}</span>
            </div>
            <div class="metric" style="grid-column: 1 / -1;">
                <span class="metric-label">IEDI Final</span>
                <span class="metric-value highlight">${formatIEDI(bankAnalysis.iedi_score)}</span>
            </div>
        </div>
    `;
    
    return card;
}
