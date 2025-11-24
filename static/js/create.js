/**
 * IEDI - Create Page (New Analysis)
 */

let availableBanks = [];
let currentMode = 'standard';
let customBankCounter = 0;

// Initialize page on load
document.addEventListener('DOMContentLoaded', () => {
    loadBanks();
    setupFormHandlers();
});

/**
 * Load available banks from API
 */
async function loadBanks() {
    const loadingEl = document.getElementById('banks-loading');
    const errorEl = document.getElementById('banks-error');
    const containerEl = document.getElementById('banks-container');
    
    loadingEl.style.display = 'flex';
    errorEl.style.display = 'none';
    containerEl.style.display = 'none';
    
    try {
        const data = await API.getBanks();
        availableBanks = data.banks || [];
        
        loadingEl.style.display = 'none';
        
        if (availableBanks.length === 0) {
            document.getElementById('banks-error-text').textContent = 'Nenhum banco disponível';
            errorEl.style.display = 'flex';
            return;
        }
        
        renderBanksCheckboxes();
        containerEl.style.display = 'block';
        
    } catch (error) {
        loadingEl.style.display = 'none';
        document.getElementById('banks-error-text').textContent = error.message || 'Erro ao carregar bancos';
        errorEl.style.display = 'flex';
    }
}

/**
 * Render banks as checkboxes
 */
function renderBanksCheckboxes() {
    const container = document.getElementById('banks-checkboxes');
    container.innerHTML = '';
    
    availableBanks.forEach(bank => {
        const item = document.createElement('div');
        item.className = 'checkbox-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `bank-${bank.name}`;
        checkbox.value = bank.name;  // Usar enum name (e.g., "BANCO_DO_BRASIL")
        
        const label = document.createElement('label');
        label.htmlFor = `bank-${bank.name}`;
        label.textContent = bank.display_name || formatBankName(bank.name);
        
        item.appendChild(checkbox);
        item.appendChild(label);
        container.appendChild(item);
    });
}

/**
 * Set date mode (standard or custom)
 */
function setDateMode(mode) {
    currentMode = mode;
    
    // Update toggle buttons
    document.getElementById('mode-standard').classList.toggle('active', mode === 'standard');
    document.getElementById('mode-custom').classList.toggle('active', mode === 'custom');
    
    // Update hint text
    const hintText = mode === 'standard' 
        ? 'Período Padrão: Todos os bancos usam o mesmo período de análise'
        : 'Períodos Customizados: Defina períodos diferentes para cada banco';
    document.getElementById('mode-hint').textContent = hintText;
    
    // Show/hide fields
    document.getElementById('standard-fields').style.display = mode === 'standard' ? 'block' : 'none';
    document.getElementById('custom-fields').style.display = mode === 'custom' ? 'block' : 'none';
    
    // Clear custom banks if switching to standard
    if (mode === 'standard') {
        document.getElementById('custom-banks-container').innerHTML = '';
        customBankCounter = 0;
    }
}

/**
 * Add custom bank period
 */
function addCustomBank() {
    const container = document.getElementById('custom-banks-container');
    const id = `custom-bank-${customBankCounter++}`;
    
    const item = document.createElement('div');
    item.className = 'custom-bank-item';
    item.id = id;
    
    item.innerHTML = `
        <div class="custom-bank-header">
            <span class="custom-bank-title">Banco ${customBankCounter}</span>
            <button type="button" class="btn-remove" onclick="removeCustomBank('${id}')" title="Remover">
                ✕
            </button>
        </div>
        <div class="form-group">
            <label class="form-label">Banco *</label>
            <select class="form-input custom-bank-select" required>
                <option value="">Selecione um banco</option>
                ${availableBanks.map(bank => `
                    <option value="${bank.name}">
                        ${bank.display_name || formatBankName(bank.name)}
                    </option>
                `).join('')}
            </select>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Data Início *</label>
                <input type="datetime-local" class="form-input custom-start-date" required>
            </div>
            <div class="form-group">
                <label class="form-label">Data Fim *</label>
                <input type="datetime-local" class="form-input custom-end-date" required>
            </div>
        </div>
    `;
    
    container.appendChild(item);
}

/**
 * Remove custom bank period
 */
function removeCustomBank(id) {
    const item = document.getElementById(id);
    if (item) {
        item.remove();
    }
}

/**
 * Setup form handlers
 */
function setupFormHandlers() {
    const form = document.getElementById('analysis-form');
    form.addEventListener('submit', handleFormSubmit);
}

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    hideError('form-error');
    
    // Validate and collect form data
    const formData = collectFormData();
    
    if (!formData) {
        return; // Validation failed
    }
    
    // Show loading state
    document.getElementById('submit-text').style.display = 'none';
    document.getElementById('submit-loading').style.display = 'inline-flex';
    document.getElementById('submit-btn').disabled = true;
    
    try {
        await API.createAnalysis(formData);
        
        // Redirect to list page on success
        window.location.href = '/';
        
    } catch (error) {
        // Hide loading state
        document.getElementById('submit-text').style.display = 'inline';
        document.getElementById('submit-loading').style.display = 'none';
        document.getElementById('submit-btn').disabled = false;
        
        showError('form-error', error.message || 'Erro ao criar análise');
    }
}

/**
 * Collect and validate form data
 */
function collectFormData() {
    const name = document.getElementById('name').value.trim();
    const query = document.getElementById('query').value.trim();
    
    if (!name) {
        showError('form-error', 'Nome da análise é obrigatório');
        return null;
    }
    
    if (!query) {
        showError('form-error', 'Query Brandwatch é obrigatória');
        return null;
    }
    
    if (currentMode === 'standard') {
        return collectStandardModeData(name, query);
    } else {
        return collectCustomModeData(name, query);
    }
}

/**
 * Collect data for standard mode
 */
function collectStandardModeData(name, query) {
    // Get selected banks
    const checkboxes = document.querySelectorAll('#banks-checkboxes input[type="checkbox"]:checked');
    const bankNames = Array.from(checkboxes).map(cb => cb.value);
    
    if (bankNames.length === 0) {
        showError('form-error', 'Selecione pelo menos um banco');
        return null;
    }
    
    // Get dates
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    if (!startDate || !endDate) {
        showError('form-error', 'Datas de início e fim são obrigatórias');
        return null;
    }
    
    // Validate dates
    if (new Date(startDate) >= new Date(endDate)) {
        showError('form-error', 'Data de início deve ser anterior à data de fim');
        return null;
    }
    
    if (new Date(endDate) > new Date()) {
        showError('form-error', 'Data de fim deve ser anterior à data atual');
        return null;
    }
    
    return {
        name,
        query,
        bank_names: bankNames,
        start_date: toISOString(startDate),
        end_date: toISOString(endDate),
    };
}

/**
 * Collect data for custom mode
 */
function collectCustomModeData(name, query) {
    const customBanks = document.querySelectorAll('.custom-bank-item');
    
    if (customBanks.length === 0) {
        showError('form-error', 'Adicione pelo menos um banco com período customizado');
        return null;
    }
    
    const customBankDates = [];
    
    for (const item of customBanks) {
        const bankSelect = item.querySelector('.custom-bank-select');
        const startDateInput = item.querySelector('.custom-start-date');
        const endDateInput = item.querySelector('.custom-end-date');
        
        const bankName = bankSelect.value;
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        
        if (!bankName) {
            showError('form-error', 'Selecione um banco para todos os períodos customizados');
            return null;
        }
        
        if (!startDate || !endDate) {
            showError('form-error', 'Preencha as datas de início e fim para todos os bancos');
            return null;
        }
        
        if (new Date(startDate) >= new Date(endDate)) {
            showError('form-error', 'Data de início deve ser anterior à data de fim para todos os bancos');
            return null;
        }
        
        if (new Date(endDate) > new Date()) {
            showError('form-error', 'Data de fim deve ser anterior à data atual para todos os bancos');
            return null;
        }
        
        customBankDates.push({
            bank_name: bankName,
            start_date: toISOString(startDate),
            end_date: toISOString(endDate),
        });
    }
    
    // Check for duplicate banks
    const bankNames = customBankDates.map(b => b.bank_name);
    const uniqueBanks = new Set(bankNames);
    if (uniqueBanks.size !== bankNames.length) {
        showError('form-error', 'Não é permitido adicionar o mesmo banco mais de uma vez');
        return null;
    }
    
    return {
        name,
        query,
        custom_bank_dates: customBankDates,
    };
}
