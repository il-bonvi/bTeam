/**
 * Races Metrics Module - TV (Traguardi Volanti) and GPM (Gran Premi Montagna) management
 * Handles intermediate sprint points and mountain classifications
 */

// Use global state from races-main.js or initialize if needed
window.tvList = window.tvList || [];
window.gpmList = window.gpmList || [];

/**
 * Build metrics tab content with TV and GPM management
 */
function buildMetricsTab(race) {
    return `
        <div style="padding: 15px;">
            <!-- Traguardi Volanti (TV) Section -->
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 30px;">
                <h4 style="color: #3b82f6; margin-bottom: 15px;">🎯 Traguardi Volanti (TV)</h4>
                <p style="color: #666; margin-bottom: 15px; font-size: 14px;">
                    I Traguardi Volanti sono punti intermedi della gara dove si assegnano punti per la classifica a punti.
                </p>
                <div style="display: flex; gap: 10px; margin-bottom: 15px; align-items: center;">
                    <input type="number" id="tv-km" class="form-input" placeholder="Inserisci km" 
                           step="0.1" min="0" style="width: 150px;">
                    <button class="btn btn-secondary" onclick="addTV()" style="white-space: nowrap;">
                        <i class="fas fa-plus"></i> Aggiungi TV
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" onclick="clearAllTV()" title="Rimuovi tutti i TV">
                        <i class="fas fa-trash-alt"></i> Cancella tutti
                    </button>
                </div>
                <div style="max-height: 200px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 4px;">
                    <table id="tv-table" class="data-table" style="width: 100%; margin: 0;">
                        <thead style="background: #f1f1f1; position: sticky; top: 0;">
                            <tr>
                                <th>📍 Chilometro</th>
                                <th style="width: 80px;">Azioni</th>
                            </tr>
                        </thead>
                        <tbody id="tv-tbody">
                            <tr><td colspan="2" style="text-align: center; color: #999; padding: 20px;">
                                Nessun Traguardo Volante aggiunto
                            </td></tr>
                        </tbody>
                    </table>
                </div>
                <div id="tv-summary" style="margin-top: 10px; font-size: 12px; color: #666;">
                    <strong>Total TV:</strong> <span id="tv-count">0</span>
                </div>
            </div>
            
            <!-- Separatore -->
            <hr style="margin: 30px 0; border: none; height: 2px; background: linear-gradient(90deg, #3b82f6, #10b981);">
            
            <!-- Gran Premi di Montagna (GPM) Section -->
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px;">
                <h4 style="color: #10b981; margin-bottom: 15px;">⛰️ Gran Premi di Montagna (GPM)</h4>
                <p style="color: #666; margin-bottom: 15px; font-size: 14px;">
                    I Gran Premi di Montagna sono classifiche sui punti più impegnativi del percorso (salite).
                </p>
                <div style="display: flex; gap: 10px; margin-bottom: 15px; align-items: center;">
                    <input type="number" id="gpm-km" class="form-input" placeholder="Inserisci km" 
                           step="0.1" min="0" style="width: 150px;">
                    <select id="gpm-category" class="form-input" style="width: 120px;">
                        <option value="4">4ª Cat.</option>
                        <option value="3">3ª Cat.</option>
                        <option value="2">2ª Cat.</option>
                        <option value="1">1ª Cat.</option>
                        <option value="HC">HC</option>
                    </select>
                    <button class="btn btn-secondary" onclick="addGPM()" style="white-space: nowrap;">
                        <i class="fas fa-plus"></i> Aggiungi GPM
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" onclick="clearAllGPM()" title="Rimuovi tutti i GPM">
                        <i class="fas fa-trash-alt"></i> Cancella tutti
                    </button>
                </div>
                <div style="max-height: 200px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 4px;">
                    <table id="gpm-table" class="data-table" style="width: 100%; margin: 0;">
                        <thead style="background: #f1f1f1; position: sticky; top: 0;">
                            <tr>
                                <th>📍 Chilometro</th>
                                <th>🏔️ Categoria</th>
                                <th style="width: 80px;">Azioni</th>
                            </tr>
                        </thead>
                        <tbody id="gpm-tbody">
                            <tr><td colspan="3" style="text-align: center; color: #999; padding: 20px;">
                                Nessun Gran Premio di Montagna aggiunto
                            </td></tr>
                        </tbody>
                    </table>
                </div>
                <div id="gpm-summary" style="margin-top: 10px; font-size: 12px; color: #666;">
                    <strong>Total GPM:</strong> <span id="gpm-count">0</span>
                </div>
            </div>
        </div>
    `;
}

/**
 * Add Traguardo Volante (TV)
 */
window.addTV = function() {
    const kmInput = document.getElementById('tv-km');
    const km = parseFloat(kmInput.value);
    
    if (!km || km <= 0) {
        showToast('Inserisci un valore valido per i chilometri', 'warning');
        kmInput.focus();
        return;
    }
    
    // Check if km already exists
    if (window.tvList.includes(km)) {
        showToast('Traguardo Volante già presente a questo chilometro', 'warning');
        return;
    }
    
    // Check if km is within race distance
    const raceDistance = window.currentRaceData?.distance_km || 0;
    if (km > raceDistance) {
        showToast(`Il chilometro deve essere inferiore alla distanza totale (${raceDistance}km)`, 'warning');
        return;
    }
    
    tvList.push(km);
    tvList.sort((a, b) => a - b); // Sort by km
    refreshTVTable();
    kmInput.value = '';
    kmInput.focus();
    
    showToast(`✅ TV aggiunto al km ${km}`, 'success');
};

/**
 * Refresh TV table display
 */
function refreshTVTable() {
    const tbody = document.getElementById('tv-tbody');
    const countSpan = document.getElementById('tv-count');
    
    if (window.tvList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="2" style="text-align: center; color: #999; padding: 20px;">Nessun Traguardo Volante aggiunto</td></tr>';
        if (countSpan) countSpan.textContent = '0';
        return;
    }
    
    tbody.innerHTML = window.tvList.map((km, index) => `
        <tr>
            <td>
                <strong style="color: #3b82f6;">${km.toFixed(1)} km</strong>
                <small style="color: #666; margin-left: 10px;">
                    (${((km / (window.currentRaceData?.distance_km || 1)) * 100).toFixed(1)}% percorso)
                </small>
            </td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="removeTV(${index})" title="Rimuovi TV">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
    
    if (countSpan) countSpan.textContent = tvList.length;
}

/**
 * Remove specific TV
 */
window.removeTV = function(index) {
    const km = window.tvList[index];
    window.tvList.splice(index, 1);
    refreshTVTable();
    showToast(`TV rimosso dal km ${km}`, 'info');
};

/**
 * Clear all TV
 */
window.clearAllTV = function() {
    if (window.tvList.length === 0) {
        showToast('Nessun TV da rimuovere', 'info');
        return;
    }
    
    if (confirm(`Rimuovere tutti i ${window.tvList.length} Traguardi Volanti?`)) {
        window.tvList = [];
        refreshTVTable();
        showToast('Tutti i TV sono stati rimossi', 'success');
    }
};

/**
 * Add Gran Premio di Montagna (GPM)
 */
window.addGPM = function() {
    const kmInput = document.getElementById('gpm-km');
    const categorySelect = document.getElementById('gpm-category');
    const km = parseFloat(kmInput.value);
    const category = categorySelect.value;
    
    if (!km || km <= 0) {
        showToast('Inserisci un valore valido per i chilometri', 'warning');
        kmInput.focus();
        return;
    }
    
    // Check if km already exists
    if (window.gpmList.find(g => g.km === km)) {
        showToast('Gran Premio di Montagna già presente a questo chilometro', 'warning');
        return;
    }
    
    // Check if km is within race distance
    const raceDistance = window.currentRaceData?.distance_km || 0;
    if (km > raceDistance) {
        showToast(`Il chilometro deve essere inferiore alla distanza totale (${raceDistance}km)`, 'warning');
        return;
    }
    
    window.gpmList.push({ km, category });
    window.gpmList.sort((a, b) => a.km - b.km); // Sort by km
    refreshGPMTable();
    kmInput.value = '';
    kmInput.focus();
    
    showToast(`✅ GPM ${category} aggiunto al km ${km}`, 'success');
};

/**
 * Refresh GPM table display
 */
function refreshGPMTable() {
    const tbody = document.getElementById('gpm-tbody');
    const countSpan = document.getElementById('gpm-count');
    
    if (window.gpmList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #999; padding: 20px;">Nessun Gran Premio di Montagna aggiunto</td></tr>';
        if (countSpan) countSpan.textContent = '0';
        return;
    }
    
    const categoryColors = {
        '4': '#94a3b8',  // slate
        '3': '#fbbf24',  // yellow
        '2': '#f97316',  // orange
        '1': '#ef4444',  // red
        'HC': '#8b5cf6'  // purple
    };
    
    tbody.innerHTML = window.gpmList.map((gpm, index) => `
        <tr>
            <td>
                <strong style="color: #10b981;">${gpm.km.toFixed(1)} km</strong>
                <small style="color: #666; margin-left: 10px;">
                    (${((gpm.km / (window.currentRaceData?.distance_km || 1)) * 100).toFixed(1)}% percorso)
                </small>
            </td>
            <td>
                <span style="background: ${categoryColors[gpm.category]}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                    ${gpm.category === 'HC' ? 'HC' : gpm.category + 'ª Cat.'}
                </span>
            </td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="removeGPM(${index})" title="Rimuovi GPM">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
    
    if (countSpan) countSpan.textContent = gpmList.length;
}

/**
 * Remove specific GPM
 */
window.removeGPM = function(index) {
    const gpm = window.gpmList[index];
    window.gpmList.splice(index, 1);
    refreshGPMTable();
    showToast(`GPM ${gpm.category} rimosso dal km ${gpm.km}`, 'info');
};

/**
 * Clear all GPM
 */
window.clearAllGPM = function() {
    if (window.gpmList.length === 0) {
        showToast('Nessun GPM da rimuovere', 'info');
        return;
    }
    
    if (confirm(`Rimuovere tutti i ${window.gpmList.length} Gran Premi di Montagna?`)) {
        window.gpmList = [];
        refreshGPMTable();
        showToast('Tutti i GPM sono stati rimossi', 'success');
    }
};

/**
 * Initialize metrics tab when displayed
 */
window.initializeMetricsTab = function() {
    // Clear existing data
    window.tvList = [];
    window.gpmList = [];
    
    // Load race-specific metrics if available
    if (window.currentRaceData?.tv_points) {
        window.tvList = [...window.currentRaceData.tv_points];
        refreshTVTable();
    }
    
    if (window.currentRaceData?.gpm_points) {
        window.gpmList = [...window.currentRaceData.gpm_points];
        refreshGPMTable();
    }
    
    // Setup keyboard shortcuts
    const tvInput = document.getElementById('tv-km');
    const gpmInput = document.getElementById('gpm-km');
    
    if (tvInput) {
        tvInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addTV();
            }
        });
    }
    
    if (gpmInput) {
        gpmInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addGPM();
            }
        });
    }
};