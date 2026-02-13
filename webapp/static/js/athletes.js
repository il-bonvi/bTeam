/**
 * Athletes Module - Frontend
 */

window.renderAthletesPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    try {
        showLoading();
        const [athletes, teams] = await Promise.all([
            api.getAthletes(),
            api.getTeams()
        ]);
        
        // Store teams globally for use in dialogs
        window.availableTeams = teams;
        
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Gestione Atleti</h3>
                    <button class="btn btn-primary" onclick="showCreateAthleteDialog()">
                        <i class="fas fa-plus"></i> Nuovo Atleta
                    </button>
                </div>
                <div id="athletes-table"></div>
            </div>
        `;
        
        // Render athletes table
        const tableHtml = createTable(
            [
                { key: 'id', label: 'ID' },
                { key: 'first_name', label: 'Nome' },
                { key: 'last_name', label: 'Cognome' },
                { key: 'team_name', label: 'Squadra' },
                { key: 'gender', label: 'Genere', format: v => v || '-' },
                { key: 'weight_kg', label: 'Peso (kg)', format: v => formatNumber(v, 1) },
                { key: 'height_cm', label: 'Alt. (cm)', format: v => v ? formatNumber(v, 0) : '-' },
                { key: 'cp', label: 'FTP', format: v => v ? formatNumber(v, 0) : '-' },
                { key: 'ecp', label: 'eCP', format: v => v ? formatNumber(v, 0) : '-' },
                { key: 'w_prime', label: "W'", format: v => v ? formatNumber(v, 0) : '-' },
                {
                    key: 'actions',
                    label: 'Azioni',
                    format: (_, row) => `
                        <button class="btn btn-secondary" onclick="editAthlete(${row.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-info" onclick="syncAthleteMetrics(${row.id})" title="Sincronizza metriche da Intervals.icu">
                            <i class="fas fa-sync"></i> Sync
                        </button>
                        <button class="btn btn-danger" onclick="deleteAthleteConfirm(${row.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    `
                }
            ],
            athletes
        );
        
        document.getElementById('athletes-table').innerHTML = tableHtml;
        
    } catch (error) {
        showToast('Errore nel caricamento degli atleti', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

window.showCreateAthleteDialog = function() {
    const teamsOptions = window.availableTeams.map(t => 
        `<option value="${t.id}">${t.name}</option>`
    ).join('');
    
    createModal(
        'Nuovo Atleta',
        `
        <div class="form-group">
            <label class="form-label">Nome</label>
            <input type="text" id="athlete-first-name" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Cognome</label>
            <input type="text" id="athlete-last-name" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Squadra</label>
            <select id="athlete-team" class="form-input">
                <option value="">Nessuna squadra</option>
                ${teamsOptions}
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Data di Nascita</label>
            <input type="date" id="athlete-birth-date" class="form-input">
        </div>
        <div class="form-group">
            <label class="form-label">Genere</label>
            <select id="athlete-gender" class="form-input">
                <option value="">Seleziona</option>
                <option value="Maschile">Maschile</option>
                <option value="Femminile">Femminile</option>
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Peso (kg)</label>
            <input type="number" id="athlete-weight" class="form-input" step="0.1">
        </div>
        <div class="form-group">
            <label class="form-label">Altezza (cm)</label>
            <input type="number" id="athlete-height" class="form-input" step="0.1">
        </div>
        <div class="form-group">
            <label class="form-label">Note</label>
            <textarea id="athlete-notes" class="form-input" rows="3"></textarea>
        </div>
        <div style="border-top: 2px solid #e0e0e0; margin-top: 1rem; padding-top: 1rem;">
            <h4>Sincronizzazione Intervals.icu</h4>
            <div class="form-group">
                <label class="form-label">API Key Intervals.icu</label>
                <div style="display: flex; gap: 8px;">
                    <input type="password" id="athlete-api-key" class="form-input" placeholder="Da: intervals.icu/settings" style="flex: 1;">
                    <button type="button" class="btn btn-secondary" onclick="toggleApiKeyVisibility('athlete-api-key')" style="padding: 8px 12px;">
                        👁️
                    </button>
                </div>
                <small>La API key è usata per sincronizzare attività e wellness di questo atleta</small>
            </div>
        </div>
        `,
        [
            {
                label: 'Annulla',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Crea',
                class: 'btn-primary',
                onclick: 'createAthlete()'
            }
        ]
    );
};

window.createAthlete = async function() {
    const firstName = document.getElementById('athlete-first-name').value.trim();
    const lastName = document.getElementById('athlete-last-name').value.trim();
    
    if (!firstName || !lastName) {
        showToast('Inserisci nome e cognome', 'warning');
        return;
    }
    
    const data = {
        first_name: firstName,
        last_name: lastName,
        team_id: document.getElementById('athlete-team').value ? parseInt(document.getElementById('athlete-team').value) : null,
        birth_date: document.getElementById('athlete-birth-date').value || null,
        gender: document.getElementById('athlete-gender').value || null,
        weight_kg: document.getElementById('athlete-weight').value ? parseFloat(document.getElementById('athlete-weight').value) : null,
        height_cm: document.getElementById('athlete-height').value ? parseFloat(document.getElementById('athlete-height').value) : null,
        notes: document.getElementById('athlete-notes').value || null,
        api_key: document.getElementById('athlete-api-key').value.trim() || null
    };
    
    try {
        showLoading();
        await api.createAthlete(data);
        showToast('Atleta creato con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderAthletesPage();
    } catch (error) {
        showToast('Errore nella creazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.editAthlete = async function(athleteId) {
    try {
        const athlete = await api.getAthlete(athleteId);
        
        const teamsOptions = window.availableTeams.map(t => 
            `<option value="${t.id}" ${t.id === athlete.team_id ? 'selected' : ''}>${t.name}</option>`
        ).join('');
        
        createModal(
            'Modifica Atleta',
            `
            <div class="form-group">
                <label class="form-label">Nome</label>
                <input type="text" id="athlete-first-name-edit" class="form-input" value="${athlete.first_name}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Cognome</label>
                <input type="text" id="athlete-last-name-edit" class="form-input" value="${athlete.last_name}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Squadra</label>
                <select id="athlete-team-edit" class="form-input">
                    <option value="">Nessuna squadra</option>
                    ${teamsOptions}
                </select>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label class="form-label">Peso (kg)</label>
                    <input type="number" id="athlete-weight-edit" class="form-input" value="${athlete.weight_kg || ''}" step="0.1">
                </div>
                <div class="form-group">
                    <label class="form-label">Altezza (cm)</label>
                    <input type="number" id="athlete-height-edit" class="form-input" value="${athlete.height_cm || ''}" step="1">
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label class="form-label">FTP (watts)</label>
                    <input type="number" id="athlete-cp-edit" class="form-input" value="${athlete.cp || ''}" step="1">
                </div>
                <div class="form-group">
                    <label class="form-label">eCP (watts) <small style="color: #666;">da Intervals</small></label>
                    <input type="number" id="athlete-ecp-edit" class="form-input" value="${athlete.ecp || ''}" step="1" disabled style="background: #f3f4f6; color: #666;">
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label class="form-label">W' (joule)</label>
                    <input type="number" id="athlete-w-prime-edit" class="form-input" value="${athlete.w_prime || ''}" step="1">
                </div>
                <div class="form-group">
                    <label class="form-label">eW' (joule) <small style="color: #666;">da Intervals</small></label>
                    <input type="number" id="athlete-ew-prime-edit" class="form-input" value="${athlete.ew_prime || ''}" step="1" disabled style="background: #f3f4f6; color: #666;">
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">FC Massima (bpm)</label>
                <input type="number" id="athlete-max-hr-edit" class="form-input" value="${athlete.max_hr || ''}" step="1">
            </div>
            <div class="form-group">
                <label class="form-label">kJ/h/kg (consumo energetico)</label>
                <input type="number" id="athlete-kj-edit" class="form-input" value="${athlete.kj_per_hour_per_kg || 10}" step="0.1" min="0.5" max="50">
                <small style="color: #666;">Default: 10 donna, 15 uomo</small>
            </div>
            <div style="border-top: 2px solid #e0e0e0; margin-top: 1rem; padding-top: 1rem;">
                <h4>Sincronizzazione Intervals.icu</h4>
                <div class="form-group">
                    <label class="form-label">API Key Intervals.icu</label>
                    <div style="display: flex; gap: 8px;">
                        <input type="password" id="athlete-api-key-edit" class="form-input" value="${athlete.api_key || ''}" placeholder="Da: intervals.icu/settings" style="flex: 1;">
                        <button type="button" class="btn btn-secondary" onclick="toggleApiKeyVisibility('athlete-api-key-edit')" style="padding: 8px 12px;">
                            👁️
                        </button>
                    </div>
                    <small>La API key è usata per sincronizzare attività e wellness</small>
                </div>
            </div>
            `,
            [
                {
                    label: 'Annulla',
                    class: 'btn-secondary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                },
                {
                    label: 'Salva',
                    class: 'btn-primary',
                    onclick: `updateAthlete(${athleteId})`
                }
            ]
        );
    } catch (error) {
        showToast('Errore nel caricamento dei dati', 'error');
    }
};

window.updateAthlete = async function(athleteId) {
    const data = {
        first_name: document.getElementById('athlete-first-name-edit').value.trim(),
        last_name: document.getElementById('athlete-last-name-edit').value.trim(),
        team_id: document.getElementById('athlete-team-edit').value ? parseInt(document.getElementById('athlete-team-edit').value) : null,
        weight_kg: document.getElementById('athlete-weight-edit').value ? parseFloat(document.getElementById('athlete-weight-edit').value) : null,
        height_cm: document.getElementById('athlete-height-edit').value ? parseFloat(document.getElementById('athlete-height-edit').value) : null,
        cp: document.getElementById('athlete-cp-edit').value ? parseFloat(document.getElementById('athlete-cp-edit').value) : null,
        w_prime: document.getElementById('athlete-w-prime-edit').value ? parseFloat(document.getElementById('athlete-w-prime-edit').value) : null,
        max_hr: document.getElementById('athlete-max-hr-edit').value ? parseFloat(document.getElementById('athlete-max-hr-edit').value) : null,
        kj_per_hour_per_kg: document.getElementById('athlete-kj-edit').value ? parseFloat(document.getElementById('athlete-kj-edit').value) : null,
        api_key: document.getElementById('athlete-api-key-edit').value.trim() || null
    };
    
    try {
        showLoading();
        await api.updateAthlete(athleteId, data);
        showToast('Atleta aggiornato con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderAthletesPage();
    } catch (error) {
        showToast('Errore nell\'aggiornamento: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.deleteAthleteConfirm = function(athleteId) {
    confirmDialog(
        'Sei sicuro di voler eliminare questo atleta? Verranno eliminate anche tutte le sue attività.',
        async () => {
            try {
                showLoading();
                await api.deleteAthlete(athleteId);
                showToast('Atleta eliminato con successo', 'success');
                window.renderAthletesPage();
            } catch (error) {
                showToast('Errore nell\'eliminazione: ' + error.message, 'error');
            } finally {
                hideLoading();
            }
        }
    );
};

/**
 * Toggle API key visibility
 */
window.toggleApiKeyVisibility = function(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';
};

/**
 * Sync athlete metrics from Intervals.icu
 */
window.syncAthleteMetrics = async function(athleteId) {
    try {
        const athlete = await api.getAthlete(athleteId);
        
        if (!athlete.api_key) {
            showToast('L\'atleta non ha una API key configurata', 'warning');
            return;
        }
        
        showLoading();
        const result = await api.syncAthleteMetrics(athleteId, athlete.api_key);
        
        // Build detailed sync message
        const synced = result.synced_fields || {};
        const messages = [];
        if (synced.weight_kg) messages.push(`Peso: ${synced.weight_kg.toFixed(1)} kg`);
        if (synced.height_cm) messages.push(`Altezza: ${synced.height_cm.toFixed(0)} cm`);
        if (synced.cp) messages.push(`FTP: ${synced.cp.toFixed(0)} W`);
        if (synced.ecp) messages.push(`eCP: ${synced.ecp.toFixed(0)} W`);
        if (synced.w_prime) messages.push(`W': ${synced.w_prime.toFixed(0)} J`);
        if (synced.ew_prime) messages.push(`eW': ${synced.ew_prime.toFixed(0)} J`);
        if (synced.max_hr) messages.push(`FC Max: ${synced.max_hr.toFixed(0)} bpm`);
        
        const message = messages.length > 0 
            ? `Metriche sincronizzate!\\n${messages.join('\\n')}`
            : 'Nessun dato disponibile da sincronizzare';
        
        showToast(message, messages.length > 0 ? 'success' : 'warning');
        window.renderAthletesPage();
    } catch (error) {
        showToast('Errore nella sincronizzazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};
