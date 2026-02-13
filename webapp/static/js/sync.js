/**
 * Sync Module - Frontend (Intervals.icu Integration)
 */

let currentApiKey = '';

window.renderSyncPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    try {
        const athletes = await api.getAthletes();
        window.availableAthletes = athletes;
        
        const athletesOptions = athletes.map(a => 
            `<option value="${a.id}">${a.first_name} ${a.last_name}</option>`
        ).join('');
        
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-sync"></i> Sincronizzazione Intervals.icu
                    </h3>
                </div>
                
                <div class="form-group">
                    <label class="form-label">
                        <i class="fas fa-key"></i> API Key Intervals.icu
                    </label>
                    <input type="password" id="intervals-api-key" class="form-input" 
                           placeholder="Inserisci la tua API key">
                    <small>Ottieni la tua API key da: <a href="https://intervals.icu/settings" target="_blank">intervals.icu/settings</a></small>
                </div>
                
                <div class="form-group">
                    <button class="btn btn-primary" onclick="testIntervalsConnection()">
                        <i class="fas fa-check-circle"></i> Testa Connessione
                    </button>
                </div>
                
                <div id="connection-status"></div>
                
                <hr style="margin: 2rem 0;">
                
                <h4><i class="fas fa-running"></i> Sincronizza Attività</h4>
                
                <div class="form-group">
                    <label class="form-label">Atleta di Destinazione</label>
                    <select id="sync-athlete" class="form-input">
                        <option value="">Seleziona atleta</option>
                        ${athletesOptions}
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Giorni Indietro</label>
                    <input type="number" id="sync-days-back" class="form-input" 
                           value="30" min="1" max="365">
                </div>
                
                <div class="form-group">
                    <button class="btn btn-success" onclick="syncActivities()">
                        <i class="fas fa-download"></i> Sincronizza Attività
                    </button>
                </div>
                
                <hr style="margin: 2rem 0;">
                
                <h4><i class="fas fa-heartbeat"></i> Sincronizza Wellness</h4>
                
                <div class="form-group">
                    <label class="form-label">Atleta di Destinazione</label>
                    <select id="sync-wellness-athlete" class="form-input">
                        <option value="">Seleziona atleta</option>
                        ${athletesOptions}
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Giorni Indietro</label>
                    <input type="number" id="sync-wellness-days-back" class="form-input" 
                           value="7" min="1" max="90">
                </div>
                
                <div class="form-group">
                    <button class="btn btn-success" onclick="syncWellness()">
                        <i class="fas fa-download"></i> Sincronizza Wellness
                    </button>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-info-circle"></i> Informazioni
                    </h3>
                </div>
                <div>
                    <h4>Come Usare</h4>
                    <ol>
                        <li>Ottieni la tua API key da <a href="https://intervals.icu/settings" target="_blank">Intervals.icu Settings</a></li>
                        <li>Incolla l'API key nel campo sopra</li>
                        <li>Clicca "Testa Connessione" per verificare</li>
                        <li>Seleziona l'atleta di destinazione nel database bTeam</li>
                        <li>Imposta il numero di giorni da sincronizzare</li>
                        <li>Clicca "Sincronizza" per importare i dati</li>
                    </ol>
                    
                    <h4>Dati Sincronizzati</h4>
                    <p><strong>Attività:</strong> Nome, data, tipo, distanza, durata, potenza, frequenza cardiaca, TSS, intensità, feel rating</p>
                    <p><strong>Wellness:</strong> Peso, FC riposo, HRV, sonno, umore, fatica, stress, motivazione</p>
                    
                    <h4>Note Importanti</h4>
                    <ul>
                        <li>L'API key è personale e non deve essere condivisa</li>
                        <li>I dati vengono salvati nel database locale bTeam</li>
                        <li>La sincronizzazione non modifica i dati su Intervals.icu</li>
                        <li>Limite di circa 100 richieste al minuto</li>
                    </ul>
                </div>
            </div>
        `;
        
    } catch (error) {
        showToast('Errore nel caricamento della pagina', 'error');
        console.error(error);
    }
};

window.testIntervalsConnection = async function() {
    const apiKey = document.getElementById('intervals-api-key').value.trim();
    
    if (!apiKey) {
        showToast('Inserisci l\'API key', 'warning');
        return;
    }
    
    currentApiKey = apiKey;
    
    try {
        showLoading();
        const result = await api.testConnection(apiKey);
        
        document.getElementById('connection-status').innerHTML = `
            <div style="padding: 1rem; background: rgba(72, 187, 120, 0.1); 
                        border-left: 4px solid #48bb78; border-radius: 0.5rem; margin-top: 1rem;">
                <strong style="color: #48bb78;">
                    <i class="fas fa-check-circle"></i> Connessione Riuscita!
                </strong>
                <p>Atleta: ${result.athlete_name}</p>
            </div>
        `;
        
        showToast('Connessione a Intervals.icu riuscita', 'success');
        
    } catch (error) {
        document.getElementById('connection-status').innerHTML = `
            <div style="padding: 1rem; background: rgba(245, 101, 101, 0.1); 
                        border-left: 4px solid #f56565; border-radius: 0.5rem; margin-top: 1rem;">
                <strong style="color: #f56565;">
                    <i class="fas fa-exclamation-circle"></i> Connessione Fallita
                </strong>
                <p>${error.message}</p>
            </div>
        `;
        
        showToast('Errore nella connessione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.syncActivities = async function() {
    const apiKey = document.getElementById('intervals-api-key').value.trim();
    const athleteId = document.getElementById('sync-athlete').value;
    const daysBack = document.getElementById('sync-days-back').value;
    
    if (!apiKey) {
        showToast('Inserisci l\'API key', 'warning');
        return;
    }
    
    if (!athleteId) {
        showToast('Seleziona un atleta', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        const result = await api.syncActivities({
            athlete_id: parseInt(athleteId),
            api_key: apiKey,
            days_back: parseInt(daysBack),
            include_intervals: true
        });
        
        showToast(result.message, 'success');
        
        // Show summary
        createModal(
            'Sincronizzazione Completata',
            `
            <div style="text-align: center; padding: 2rem;">
                <i class="fas fa-check-circle" style="font-size: 4rem; color: #48bb78;"></i>
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

window.syncWellness = async function() {
    const apiKey = document.getElementById('intervals-api-key').value.trim();
    const athleteId = document.getElementById('sync-wellness-athlete').value;
    const daysBack = document.getElementById('sync-wellness-days-back').value;
    
    if (!apiKey) {
        showToast('Inserisci l\'API key', 'warning');
        return;
    }
    
    if (!athleteId) {
        showToast('Seleziona un atleta', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        const result = await api.syncWellness({
            athlete_id: parseInt(athleteId),
            api_key: apiKey,
            days_back: parseInt(daysBack)
        });
        
        showToast(result.message, 'success');
        
        // Show summary
        createModal(
            'Sincronizzazione Wellness Completata',
            `
            <div style="text-align: center; padding: 2rem;">
                <i class="fas fa-check-circle" style="font-size: 4rem; color: #48bb78;"></i>
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
