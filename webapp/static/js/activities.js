/**
 * Activities Module - Frontend
 */

window.renderActivitiesPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    try {
        showLoading();
        const [activities, athletes] = await Promise.all([
            api.getActivities({ limit: 100 }),
            api.getAthletes()
        ]);
        
        window.availableAthletes = athletes;
        
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Attività</h3>
                    <div class="flex gap-1">
                        <button class="btn btn-secondary" onclick="filterActivities()">
                            <i class="fas fa-filter"></i> Filtra
                        </button>
                        <button class="btn btn-primary" onclick="showCreateActivityDialog()">
                            <i class="fas fa-plus"></i> Nuova Attività
                        </button>
                    </div>
                </div>
                <div id="activities-table"></div>
            </div>
        `;
        
        // Render activities table
        const tableHtml = createTable(
            [
                { key: 'id', label: 'ID' },
                { key: 'athlete_name', label: 'Atleta' },
                { key: 'title', label: 'Titolo' },
                { key: 'activity_date', label: 'Data', format: formatDate },
                { key: 'activity_type', label: 'Tipo' },
                { key: 'distance_km', label: 'Distanza (km)', format: v => formatNumber(v, 1) },
                { key: 'duration_minutes', label: 'Durata', format: formatDuration },
                { key: 'tss', label: 'TSS', format: v => formatNumber(v, 0) },
                { key: 'avg_watts', label: 'Potenza Media', format: v => v ? formatNumber(v, 0) : '-' },
                {
                    key: 'actions',
                    label: 'Azioni',
                    format: (_, row) => `
                        <button class="btn btn-danger" onclick="deleteActivityConfirm(${row.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    `
                }
            ],
            activities
        );
        
        document.getElementById('activities-table').innerHTML = tableHtml;
        
    } catch (error) {
        showToast('Errore nel caricamento delle attività', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

window.showCreateActivityDialog = function() {
    const athletesOptions = window.availableAthletes.map(a => 
        `<option value="${a.id}">${a.first_name} ${a.last_name}</option>`
    ).join('');
    
    createModal(
        'Nuova Attività',
        `
        <div class="form-group">
            <label class="form-label">Atleta</label>
            <select id="activity-athlete" class="form-input" required>
                <option value="">Seleziona atleta</option>
                ${athletesOptions}
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Titolo</label>
            <input type="text" id="activity-title" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Data</label>
            <input type="date" id="activity-date" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Tipo</label>
            <select id="activity-type" class="form-input">
                <option value="Ride">Ride</option>
                <option value="Run">Run</option>
                <option value="VirtualRide">VirtualRide</option>
                <option value="Swim">Swim</option>
                <option value="WeightTraining">WeightTraining</option>
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Distanza (km)</label>
            <input type="number" id="activity-distance" class="form-input" step="0.1">
        </div>
        <div class="form-group">
            <label class="form-label">Durata (minuti)</label>
            <input type="number" id="activity-duration" class="form-input" step="1">
        </div>
        <div class="form-group">
            <label class="form-label">TSS</label>
            <input type="number" id="activity-tss" class="form-input" step="0.1">
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
                onclick: 'createActivity()'
            }
        ]
    );
};

window.createActivity = async function() {
    const athleteId = document.getElementById('activity-athlete').value;
    const title = document.getElementById('activity-title').value.trim();
    const activityDate = document.getElementById('activity-date').value;
    
    if (!athleteId || !title || !activityDate) {
        showToast('Compila i campi obbligatori', 'warning');
        return;
    }
    
    const data = {
        athlete_id: parseInt(athleteId),
        title: title,
        activity_date: activityDate,
        activity_type: document.getElementById('activity-type').value,
        distance_km: document.getElementById('activity-distance').value ? parseFloat(document.getElementById('activity-distance').value) : null,
        duration_minutes: document.getElementById('activity-duration').value ? parseFloat(document.getElementById('activity-duration').value) : null,
        tss: document.getElementById('activity-tss').value ? parseFloat(document.getElementById('activity-tss').value) : null,
        source: 'MANUAL'
    };
    
    try {
        showLoading();
        await api.createActivity(data);
        showToast('Attività creata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderActivitiesPage();
    } catch (error) {
        showToast('Errore nella creazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.deleteActivityConfirm = function(activityId) {
    confirmDialog(
        'Sei sicuro di voler eliminare questa attività?',
        async () => {
            try {
                showLoading();
                await api.deleteActivity(activityId);
                showToast('Attività eliminata con successo', 'success');
                window.renderActivitiesPage();
            } catch (error) {
                showToast('Errore nell\'eliminazione: ' + error.message, 'error');
            } finally {
                hideLoading();
            }
        }
    );
};

window.filterActivities = function() {
    const athletesOptions = window.availableAthletes.map(a => 
        `<option value="${a.id}">${a.first_name} ${a.last_name}</option>`
    ).join('');
    
    createModal(
        'Filtra Attività',
        `
        <div class="form-group">
            <label class="form-label">Atleta</label>
            <select id="filter-athlete" class="form-input">
                <option value="">Tutti</option>
                ${athletesOptions}
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Solo Gare</label>
            <select id="filter-race" class="form-input">
                <option value="">Tutte</option>
                <option value="true">Solo gare</option>
                <option value="false">Solo allenamenti</option>
            </select>
        </div>
        `,
        [
            {
                label: 'Chiudi',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Applica',
                class: 'btn-primary',
                onclick: 'applyActivityFilter()'
            }
        ]
    );
};

window.applyActivityFilter = async function() {
    const athleteId = document.getElementById('filter-athlete').value;
    const isRace = document.getElementById('filter-race').value;
    
    const filters = {};
    if (athleteId) filters.athlete_id = parseInt(athleteId);
    if (isRace) filters.is_race = isRace === 'true';
    
    try {
        showLoading();
        const activities = await api.getActivities(filters);
        
        const tableHtml = createTable(
            [
                { key: 'id', label: 'ID' },
                { key: 'athlete_name', label: 'Atleta' },
                { key: 'title', label: 'Titolo' },
                { key: 'activity_date', label: 'Data', format: formatDate },
                { key: 'distance_km', label: 'Distanza (km)', format: v => formatNumber(v, 1) },
                { key: 'duration_minutes', label: 'Durata', format: formatDuration },
                {
                    key: 'actions',
                    label: 'Azioni',
                    format: (_, row) => `
                        <button class="btn btn-danger" onclick="deleteActivityConfirm(${row.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    `
                }
            ],
            activities
        );
        
        document.getElementById('activities-table').innerHTML = tableHtml;
        document.querySelector('.modal-overlay').remove();
        showToast(`Trovate ${activities.length} attività`, 'info');
        
    } catch (error) {
        showToast('Errore nel filtraggio: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};
