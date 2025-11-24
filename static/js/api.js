/**
 * IEDI - API Client Module
 * Handles all HTTP requests to the backend
 */

const API_BASE_URL = '/analysis';

/**
 * Generic HTTP request handler
 */
async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        
        // Handle non-JSON responses
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Resposta inválida do servidor');
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `Erro HTTP: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

/**
 * API Methods
 */
const API = {
    /**
     * Get all analyses
     */
    getAnalyses: async () => {
        return request('/api/analyses');
    },
    
    /**
     * Get analysis by ID
     */
    getAnalysis: async (id) => {
        return request(`/api/analyses/${id}`);
    },
    
    /**
     * Get bank analyses for an analysis
     */
    getBankAnalyses: async (analysisId) => {
        return request(`/api/analyses/${analysisId}/banks`);
    },
    
    /**
     * Create new analysis
     */
    createAnalysis: async (data) => {
        return request('/api/analyses', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * Get all available banks
     */
    getBanks: async () => {
        return request('/api/banks');
    },
};

/**
 * Utility Functions
 */

/**
 * Format date to Brazilian format
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

/**
 * Format date to ISO string for API
 */
function toISOString(dateString) {
    if (!dateString) return null;
    return new Date(dateString).toISOString();
}

/**
 * Get status badge class
 */
function getStatusBadgeClass(status) {
    const statusMap = {
        'PENDING': 'badge-pending',
        'PROCESSING': 'badge-processing',
        'COMPLETED': 'badge-completed',
        'FAILED': 'badge-failed',
    };
    return statusMap[status] || 'badge-pending';
}

/**
 * Get status label
 */
function getStatusLabel(status) {
    const statusMap = {
        'PENDING': 'Pendente',
        'PROCESSING': 'Processando',
        'COMPLETED': 'Concluída',
        'FAILED': 'Falhou',
    };
    return statusMap[status] || status;
}

/**
 * Get type badge class
 */
function getTypeBadgeClass(isCustom) {
    return isCustom ? 'badge-custom' : 'badge-standard';
}

/**
 * Get type label
 */
function getTypeLabel(isCustom) {
    return isCustom ? 'Customizado' : 'Padrão';
}

/**
 * Format bank name for display
 */
function formatBankName(bankName) {
    // Convert BANCO_DO_BRASIL to Banco do Brasil
    return bankName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}

/**
 * Format IEDI score (0-10 scale)
 */
function formatIEDI(score) {
    if (score === null || score === undefined) return '-';
    return score.toFixed(2);
}

/**
 * Format volume
 */
function formatVolume(volume) {
    if (volume === null || volume === undefined) return '-';
    return volume.toFixed(1);
}

/**
 * Show error message
 */
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    const errorTextElement = document.getElementById(`${elementId}-text`);
    
    if (errorElement && errorTextElement) {
        errorTextElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

/**
 * Hide error message
 */
function hideError(elementId) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

/**
 * Show loading state
 */
function showLoading(elementId) {
    const loadingElement = document.getElementById(elementId);
    if (loadingElement) {
        loadingElement.style.display = 'flex';
    }
}

/**
 * Hide loading state
 */
function hideLoading(elementId) {
    const loadingElement = document.getElementById(elementId);
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}
