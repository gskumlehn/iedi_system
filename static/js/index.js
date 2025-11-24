/**
 * IEDI - Index Page (Analyses List)
 */

// Load analyses on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAnalyses();
});

/**
 * Load and display all analyses
 */
async function loadAnalyses() {
    showLoading('loading');
    hideError('error');
    document.getElementById('empty').style.display = 'none';
    document.getElementById('analyses-container').style.display = 'none';
    
    try {
        const data = await API.getAnalyses();
        hideLoading('loading');
        
        if (!data.analyses || data.analyses.length === 0) {
            document.getElementById('empty').style.display = 'block';
            return;
        }
        
        renderAnalysesTable(data.analyses);
        document.getElementById('analyses-container').style.display = 'block';
        
    } catch (error) {
        hideLoading('loading');
        showError('error', error.message || 'Erro ao carregar análises');
    }
}

/**
 * Render analyses table
 */
function renderAnalysesTable(analyses) {
    const tbody = document.getElementById('analyses-tbody');
    tbody.innerHTML = '';
    
    analyses.forEach(analysis => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>
                <strong>${escapeHtml(analysis.name)}</strong>
            </td>
            <td>${escapeHtml(analysis.query_name || '-')}</td>
            <td>
                <span class="badge ${getStatusBadgeClass(analysis.status)}">
                    ${getStatusLabel(analysis.status)}
                </span>
            </td>
            <td>
                <span class="badge ${getTypeBadgeClass(analysis.is_custom_dates)}">
                    ${getTypeLabel(analysis.is_custom_dates)}
                </span>
            </td>
            <td>${formatDate(analysis.created_at)}</td>
            <td>
                <button 
                    class="btn btn-primary btn-sm" 
                    onclick="viewAnalysis('${analysis.id}')"
                >
                    Ver Detalhes
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * Navigate to analysis details page
 */
function viewAnalysis(analysisId) {
    window.location.href = `/detail?id=${analysisId}`;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
