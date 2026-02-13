/**
 * Wellness Module - Frontend
 */

window.renderWellnessPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    try {
        showLoading();
        const [wellness, athletes] = await Promise.all([
            api.getWellness({ days_back: 30 }),
            api.getAthletes()
        ]);
        
        window.availableAthletes = athletes;
        
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Dati Wellness</h3>
                    <button class="btn btn-primary" onclick="showCreateWellnessDialog()">
                        <i class="fas fa-plus"></i> Nuovo Entry
                    </button>
                </div>
                <div id="wellness-table"></div>
            </div>
        `;
        
        // Render wellness table
        const tableHtml = createTable(
            [
                { key: 'id', label: 'ID' },
                { key: 'athlete_id', label: 'Atleta ID' },
                { key: 'wellness_date', label: 'Data', format: formatDate },
                { key: 'weight_kg', label: 'Peso (kg)', format: v => formatNumber(v, 1) },
                { key: 'resting_hr', label: 'FC Riposo', format: v => v || '-' },
                { key: 'hrv', label: 'HRV', format: v => formatNumber(v, 1) },
                { key: 'sleep_secs', label: 'Sonno', format: v => v ? formatDuration(v / 60) : '-' },
                { key: 'mood', label: 'Umore', format: v => v || '-' },
                {
                    key: 'actions',
                    label: 'Azioni',
                    format: (_, row) => `
                        <button class="btn btn-secondary" onclick="editWellness(${row.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger" onclick="deleteWellnessConfirm(${row.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    `
                }
            ],
            wellness
        );
        
        document.getElementById('wellness-table').innerHTML = tableHtml;
        
    } catch (error) {
        showToast('Errore nel caricamento dei dati wellness', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

window.showCreateWellnessDialog = function() {
    const athletesOptions = window.availableAthletes.map(a => 
        `<option value="${a.id}">${a.first_name} ${a.last_name}</option>`
    ).join('');
    
    createModal(
        'Nuovo Entry Wellness',
        `
        <div class="form-group">
            <label class="form-label">Atleta</label>
            <select id="wellness-athlete" class="form-input" required>
                <option value="">Seleziona atleta</option>
                ${athletesOptions}
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Data</label>
            <input type="date" id="wellness-date" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Peso (kg)</label>
            <input type="number" id="wellness-weight" class="form-input" step="0.1">
        </div>
        <div class="form-group">
            <label class="form-label">FC Riposo (bpm)</label>
            <input type="number" id="wellness-hr" class="form-input" step="1">
        </div>
        <div class="form-group">
            <label class="form-label">HRV (ms)</label>
            <input type="number" id="wellness-hrv" class="form-input" step="0.1">
        </div>
        <div class="form-group">
            <label class="form-label">Passi</label>
            <input type="number" id="wellness-steps" class="form-input" step="1">
        </div>
        <div class="form-group">
            <label class="form-label">Dolori Muscolari (1-10)</label>
            <input type="number" id="wellness-soreness" class="form-input" min="1" max="10" step="1">
        </div>
        <div class="form-group">
            <label class="form-label">Fatica (1-10)</label>
            <input type="number" id="wellness-fatigue" class="form-input" min="1" max="10" step="1">
        </div>
        <div class="form-group">
            <label class="form-label">Stress (1-10)</label>
            <input type="number" id="wellness-stress" class="form-input" min="1" max="10" step="1">
        </div>
        <div class="form-group">
            <label class="form-label">Umore (1-10)</label>
            <input type="number" id="wellness-mood" class="form-input" min="1" max="10" step="1">
        </div>
        <div class="form-group">
            <label class="form-label">Motivazione (1-10)</label>
            <input type="number" id="wellness-motivation" class="form-input" min="1" max="10" step="1">
        </div>
        <div class="form-group">
            <label class="form-label">Sonno (ore)</label>
            <input type="number" id="wellness-sleep" class="form-input" step="0.5" placeholder="Es. 8.5">
        </div>
        <div class="form-group">
            <label class="form-label">Commenti</label>
            <textarea id="wellness-comments" class="form-input" rows="3"></textarea>
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
                onclick: 'createWellness()'
            }
        ]
    );
};

window.createWellness = async function() {
    const athleteId = document.getElementById('wellness-athlete').value;
    const wellnessDate = document.getElementById('wellness-date').value;
    
    if (!athleteId || !wellnessDate) {
        showToast('Seleziona atleta e data', 'warning');
        return;
    }
    
    const sleepHours = document.getElementById('wellness-sleep').value;
    const sleepSecs = sleepHours ? parseFloat(sleepHours) * 3600 : null;
    
    const data = {
        athlete_id: parseInt(athleteId),
        wellness_date: wellnessDate,
        weight_kg: document.getElementById('wellness-weight').value ? parseFloat(document.getElementById('wellness-weight').value) : null,
        resting_hr: document.getElementById('wellness-hr').value ? parseInt(document.getElementById('wellness-hr').value) : null,
        hrv: document.getElementById('wellness-hrv').value ? parseFloat(document.getElementById('wellness-hrv').value) : null,
        steps: document.getElementById('wellness-steps').value ? parseInt(document.getElementById('wellness-steps').value) : null,
        soreness: document.getElementById('wellness-soreness').value ? parseInt(document.getElementById('wellness-soreness').value) : null,
        fatigue: document.getElementById('wellness-fatigue').value ? parseInt(document.getElementById('wellness-fatigue').value) : null,
        stress: document.getElementById('wellness-stress').value ? parseInt(document.getElementById('wellness-stress').value) : null,
        mood: document.getElementById('wellness-mood').value ? parseInt(document.getElementById('wellness-mood').value) : null,
        motivation: document.getElementById('wellness-motivation').value ? parseInt(document.getElementById('wellness-motivation').value) : null,
        sleep_secs: sleepSecs,
        comments: document.getElementById('wellness-comments').value || null
    };
    
    try {
        showLoading();
        await api.createWellness(data);
        showToast('Entry wellness creato con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderWellnessPage();
    } catch (error) {
        showToast('Errore nella creazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.editWellness = async function(wellnessId) {
    try {
        const wellness = await api.getWellnessEntry(wellnessId);
        const sleepHours = wellness.sleep_secs ? (wellness.sleep_secs / 3600).toFixed(1) : '';
        
        createModal(
            'Modifica Wellness',
            `
            <div class="form-group">
                <label class="form-label">Peso (kg)</label>
                <input type="number" id="wellness-weight-edit" class="form-input" value="${wellness.weight_kg || ''}" step="0.1">
            </div>
            <div class="form-group">
                <label class="form-label">FC Riposo (bpm)</label>
                <input type="number" id="wellness-hr-edit" class="form-input" value="${wellness.resting_hr || ''}" step="1">
            </div>
            <div class="form-group">
                <label class="form-label">HRV (ms)</label>
                <input type="number" id="wellness-hrv-edit" class="form-input" value="${wellness.hrv || ''}" step="0.1">
            </div>
            <div class="form-group">
                <label class="form-label">Umore (1-10)</label>
                <input type="number" id="wellness-mood-edit" class="form-input" value="${wellness.mood || ''}" min="1" max="10" step="1">
            </div>
            <div class="form-group">
                <label class="form-label">Sonno (ore)</label>
                <input type="number" id="wellness-sleep-edit" class="form-input" value="${sleepHours}" step="0.5">
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
                    onclick: `updateWellness(${wellnessId}, ${wellness.athlete_id}, '${wellness.wellness_date}')`
                }
            ]
        );
    } catch (error) {
        showToast('Errore nel caricamento dei dati', 'error');
    }
};

window.updateWellness = async function(wellnessId, athleteId, wellnessDate) {
    const sleepHours = document.getElementById('wellness-sleep-edit').value;
    const sleepSecs = sleepHours ? parseFloat(sleepHours) * 3600 : null;
    
    const data = {
        athlete_id: athleteId,
        wellness_date: wellnessDate,
        weight_kg: document.getElementById('wellness-weight-edit').value ? parseFloat(document.getElementById('wellness-weight-edit').value) : null,
        resting_hr: document.getElementById('wellness-hr-edit').value ? parseInt(document.getElementById('wellness-hr-edit').value) : null,
        hrv: document.getElementById('wellness-hrv-edit').value ? parseFloat(document.getElementById('wellness-hrv-edit').value) : null,
        mood: document.getElementById('wellness-mood-edit').value ? parseInt(document.getElementById('wellness-mood-edit').value) : null,
        sleep_secs: sleepSecs
    };
    
    try {
        showLoading();
        await api.updateWellness(wellnessId, data);
        showToast('Wellness aggiornato con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderWellnessPage();
    } catch (error) {
        showToast('Errore nell\'aggiornamento: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.deleteWellnessConfirm = function(wellnessId) {
    confirmDialog(
        'Sei sicuro di voler eliminare questo entry wellness?',
        async () => {
            try {
                showLoading();
                await api.deleteWellness(wellnessId);
                showToast('Wellness eliminato con successo', 'success');
                window.renderWellnessPage();
            } catch (error) {
                showToast('Errore nell\'eliminazione: ' + error.message, 'error');
            } finally {
                hideLoading();
            }
        }
    );
};
