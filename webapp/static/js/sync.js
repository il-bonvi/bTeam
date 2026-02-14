/**
 * Sync Module - Frontend (Intervals.icu Integration)
 * Ogni atleta ha la sua API key salvata nel database
 */

// Use window object to avoid scope conflicts
window.selectedAthleteData = null;

window.renderSyncPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    try {
        const athletes = await api.getAthletes();
        window.availableAthletes = athletes;
        
        const athletesOptions = athletes.map(a => 
            `<option value="${a.id}" data-api-key="${a.api_key || ''}">${a.first_name} ${a.last_name}</option>`
        ).join('');
        
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="bi bi-arrow-repeat"></i> Sincronizzazione Intervals.icu
                    </h3>
                </div>
                
                <div style="background: #f0f8ff; border-left: 4px solid #3b82f6; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                    <strong>ℹ️ Nota:</strong> Ogni atleta ha una sua API key salvata. Seleziona l'atleta per sincronizzare i suoi dati da Intervals.icu
                </div>
                
                <hr style="margin: 1rem 0;">
                
                <h4><i class="bi bi-activity"></i> Sincronizza Attività</h4>
                
                <div class="form-group">
                    <label class="form-label">Atleta</label>
                    <select id="sync-athlete" class="form-input" onchange="onAthleteSelected('activities')">
                        <option value="">Seleziona atleta</option>
                        ${athletesOptions}
                    </select>
                </div>
                
                <div id="athlete-api-status-activities" style="display: none; margin-bottom: 1rem;"></div>
                
                <div class="form-group">
                    <label class="form-label">Giorni Indietro</label>
                    <input type="number" id="sync-days-back" class="form-input" 
                           value="30" min="1" max="365">
                </div>
                
                <div class="form-group">
                    <button class="btn btn-success" onclick="testAndSyncActivities()">
                        <i class="bi bi-download"></i> Sincronizza Attività
                    </button>
                </div>
                
                <hr style="margin: 2rem 0;">
                
                <h4><i class="bi bi-heart-pulse"></i> Sincronizza Wellness</h4>
                
                <div class="form-group">
                    <label class="form-label">Atleta</label>
                    <select id="sync-wellness-athlete" class="form-input" onchange="onAthleteSelected('wellness')">
                        <option value="">Seleziona atleta</option>
                        ${athletesOptions}
                    </select>
                </div>
                
                <div id="athlete-api-status-wellness" style="display: none; margin-bottom: 1rem;"></div>
                
                <div class="form-group">
                    <label class="form-label">Giorni Indietro</label>
                    <input type="number" id="sync-wellness-days-back" class="form-input" 
                           value="30" min="1" max="90">
                </div>
                
                <div class="form-group">
                    <button class="btn btn-success" onclick="testAndSyncWellness()">
                        <i class="bi bi-download"></i> Sincronizza Wellness
                    </button>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="bi bi-info-circle"></i> Informazioni
                    </h3>
                </div>
                <div>
                    <h4>Come Usare</h4>
                    <ol>
                        <li>Vai su <a href="https://intervals.icu/settings" target="_blank">Intervals.icu Settings</a> e copia la tua API key</li>
                        <li>Modifica il tuo atleta e incolla l'API key nel campo "API Key Intervals.icu"</li>
                        <li>Salva i dati dell'atleta</li>
                        <li>Torna a questa pagina e seleziona il tuo atleta</li>
                        <li>Clicca "Sincronizza Attività" o "Sincronizza Wellness"</li>
                    </ol>
                    
                    <h4>Dati Sincronizzati</h4>
                    <p><strong>Attività:</strong> Nome, data, tipo, distanza, durata, potenza, frequenza cardiaca, TSS, intensità, feel rating</p>
                    <p><strong>Wellness:</strong> Peso, FC riposo, HRV, sonno, umore, fatica, stress, motivazione</p>
                    
                    <h4>Note Importanti</h4>
                    <ul>
                        <li>L'API key è personale e salvata nel database</li>
                        <li>I dati vengono salvati nel database locale bTeam</li>
                        <li>La sincronizzazione non modifica i dati su Intervals.icu</li>
                        <li>Limite di circa 100 richieste al minuto su Intervals.icu</li>
                    </ul>
                </div>
            </div>
        `;
        
    } catch (error) {
        showToast('Errore nel caricamento della pagina', 'error');
        console.error(error);
    }
};

window.onAthleteSelected = function(type) {
    const selectId = type === 'wellness' ? 'sync-wellness-athlete' : 'sync-athlete';
    const statusId = type === 'wellness' ? 'athlete-api-status-wellness' : 'athlete-api-status-activities';
    
    const athleteId = document.getElementById(selectId).value;
    const statusDiv = document.getElementById(statusId);
    
    if (!athleteId) {
        statusDiv.style.display = 'none';
        return;
    }
    
    const athlete = window.availableAthletes.find(a => a.id === parseInt(athleteId));
    window.selectedAthleteData = athlete;
    
    if (athlete.api_key) {
        statusDiv.innerHTML = `
            <div style="padding: 0.75rem; background: rgba(72, 187, 120, 0.1); 
                        border-left: 4px solid #48bb78; border-radius: 5px;">
                <strong style="color: #48bb78;">✅ API Key Salvata</strong>
                <p>Sincronizzerai i dati personali di <strong>${athlete.first_name} ${athlete.last_name}</strong></p>
            </div>
        `;
    } else {
        statusDiv.innerHTML = `
            <div style="padding: 0.75rem; background: rgba(245, 101, 101, 0.1); 
                        border-left: 4px solid #f56565; border-radius: 5px;">
                <strong style="color: #f56565;">⚠️ API Key Mancante</strong>
                <p>Aggiungi l'API key per <strong>${athlete.first_name} ${athlete.last_name}</strong> prima di sincronizzare</p>
                <button class="btn btn-warning btn-sm" onclick="editAthleteApiKey(${athlete.id})">
                    <i class="bi bi-pencil"></i> Aggiungi API Key
                </button>
            </div>
        `;
    }
    
    statusDiv.style.display = 'block';
};

window.editAthleteApiKey = async function(athleteId) {
    try {
        const athlete = await api.getAthlete(athleteId);
        
        createModal(
            `Aggiungi API Key - ${athlete.first_name} ${athlete.last_name}`,
            `
            <p>Inserisci la tua API key di Intervals.icu</p>
            <div class="form-group">
                <label class="form-label">API Key Intervals.icu</label>
                <div style="display: flex; gap: 8px;">
                    <input type="password" id="quick-api-key" class="form-input" value="${athlete.api_key || ''}" 
                           placeholder="Da: intervals.icu/settings" style="flex: 1;">
                    <button type="button" class="btn btn-secondary" onclick="toggleApiKeyVisibility('quick-api-key')" style="padding: 8px 12px;">
                        👁️
                    </button>
                </div>
                <small><a href="https://intervals.icu/settings" target="_blank">Ottieni la tua API key</a></small>
            </div>
            `,
            [
                {
                    label: 'Annulla',
                    class: 'btn-secondary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                },
                {
                    label: '💾 Salva',
                    class: 'btn-primary',
                    onclick: `saveAthleteApiKey(${athleteId})`
                }
            ]
        );
    } catch (error) {
        showToast('Errore nel caricamento', 'error');
    }
};

window.saveAthleteApiKey = async function(athleteId) {
    const apiKey = document.getElementById('quick-api-key').value.trim();
    
    try {
        showLoading();
        await api.updateAthlete(athleteId, { api_key: apiKey });
        showToast('✅ API Key salvata', 'success');
        
        // Reload sync page
        document.querySelector('.modal-overlay').remove();
        await window.renderSyncPage();
    } catch (error) {
        showToast('Errore nel salvataggio: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.testAndSyncActivities = async function() {
    const athleteId = document.getElementById('sync-athlete').value;
    const daysBack = document.getElementById('sync-days-back').value;
    
    if (!athleteId) {
        showToast('Seleziona un atleta', 'warning');
        return;
    }
    
    const athlete = window.availableAthletes.find(a => a.id === parseInt(athleteId));
    
    if (!athlete.api_key) {
        showToast('L\'atleta non ha un\'API key salvata', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        const result = await api.syncActivities({
            athlete_id: parseInt(athleteId),
            api_key: athlete.api_key,
            days_back: parseInt(daysBack),
            include_intervals: true
        });
        
        showToast(result.message, 'success');
        
        // Show summary
        createModal(
            'Sincronizzazione Completata',
            `
            <div style="text-align: center; padding: 2rem;">
                <i class="bi bi-check-circle" style="font-size: 4rem; color: #48bb78;"></i>
                <h3 style="margin-top: 1rem;">${result.message}</h3>
                <p style="margin-top: 1rem; font-size: 1.2rem;">
                    Importate <strong>${result.imported}</strong> attività su ${result.total}
                </p>
            </div>
            `,
            [
                {
                    label: 'OK',
                    class: 'btn-primary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                }
            ]
        );
        
    } catch (error) {
        showToast('Errore nella sincronizzazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.testAndSyncWellness = async function() {
    const athleteId = document.getElementById('sync-wellness-athlete').value;
    const daysBack = document.getElementById('sync-wellness-days-back').value;
    
    if (!athleteId) {
        showToast('Seleziona un atleta', 'warning');
        return;
    }
    
    const athlete = window.availableAthletes.find(a => a.id === parseInt(athleteId));
    
    if (!athlete.api_key) {
        showToast('L\'atleta non ha un\'API key salvata', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        const result = await api.syncWellness({
            athlete_id: parseInt(athleteId),
            api_key: athlete.api_key,
            days_back: parseInt(daysBack)
        });
        
        showToast(result.message, 'success');
        
        // Show summary
        createModal(
            'Sincronizzazione Wellness Completata',
            `
            <div style="text-align: center; padding: 2rem;">
                <i class="bi bi-check-circle" style="font-size: 4rem; color: #48bb78;"></i>
                <h3 style="margin-top: 1rem;">${result.message}</h3>
                <p style="margin-top: 1rem; font-size: 1.2rem;">
                    Importati <strong>${result.imported}</strong> entry wellness
                </p>
            </div>
            `,
            [
                {
                    label: 'OK',
                    class: 'btn-primary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                }
            ]
        );
        
    } catch (error) {
        showToast('Errore nella sincronizzazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};
