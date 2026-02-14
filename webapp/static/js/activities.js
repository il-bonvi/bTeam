/**
 * Activities Module - Frontend
 * Multi-athlete dashboard with filtering capabilities
 */

// Global state
window.currentAthleteFilter = null; // null = all athletes, number = specific athlete ID
window.selectedActivityIds = new Set();

window.renderActivitiesPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    try {
        showLoading();
        const [activities, athletes] = await Promise.all([
            api.getActivities({ limit: 500 }),
            api.getAthletes()
        ]);
        
        window.availableAthletes = athletes;
        window.athleteNameMap = new Map(
            athletes.map(a => [a.id, `${a.first_name} ${a.last_name}`])
        );
        window.allActivities = activities;
        
        // Filter activities if athlete filter is active
        const filteredActivities = window.currentAthleteFilter 
            ? activities.filter(a => a.athlete_id === window.currentAthleteFilter)
            : activities;
        
        renderActivitiesDashboard(filteredActivities, athletes, contentArea);
        
    } catch (error) {
        showToast('Errore nel caricamento delle attività', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

function renderActivitiesDashboard(filteredActivities, athletes, contentArea) {
    // Calculate stats
    const totalActivities = filteredActivities.length;
    const totalDistance = filteredActivities.reduce((sum, a) => sum + (a.distance_km || 0), 0);
    const totalDuration = filteredActivities.reduce((sum, a) => sum + (a.duration_minutes || 0), 0);
    const totalTSS = filteredActivities.reduce((sum, a) => sum + (a.tss || 0), 0);
    const avgWatts = filteredActivities.filter(a => a.avg_watts).reduce((sum, a) => sum + a.avg_watts, 0) / filteredActivities.filter(a => a.avg_watts).length || 0;
    
    // Get active athlete filter name
    const activeAthleteName = window.currentAthleteFilter 
        ? athletes.find(a => a.id === window.currentAthleteFilter)?.first_name + ' ' + athletes.find(a => a.id === window.currentAthleteFilter)?.last_name
        : 'Tutti gli atleti';
    
    contentArea.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 Dashboard Attività</h3>
                <button class="btn btn-primary" onclick="showCreateActivityDialog()">
                    <i class="bi bi-plus"></i> Nuova Attività
                </button>
            </div>
            <div class="card-body">
                <!-- Stats Summary -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                    <div class="stat-card">
                        <div class="stat-label">Totale Attività</div>
                        <div class="stat-value">${totalActivities}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Distanza Totale</div>
                        <div class="stat-value">${Math.round(totalDistance)} km</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Durata Totale</div>
                        <div class="stat-value">${Math.round(totalDuration / 60)} h</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">TSS Totale</div>
                        <div class="stat-value">${Math.round(totalTSS)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Potenza Media</div>
                        <div class="stat-value">${avgWatts > 0 ? Math.round(avgWatts) + 'W' : '-'}</div>
                    </div>
                </div>
                
                <!-- Athlete Filter Pills -->
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="margin-bottom: 0.5rem; font-size: 0.875rem; color: var(--text-secondary);">
                        Filtra per Atleta: <strong style="color: var(--primary-color);">${activeAthleteName}</strong>
                    </h4>
                    <div class="athlete-filter-pills">
                        <button class="filter-pill ${window.currentAthleteFilter === null ? 'active' : ''}" onclick="setAthleteFilter(null)">
                            <i class="bi bi-people-fill"></i> Tutti
                        </button>
                        ${athletes.map(athlete => `
                            <button class="filter-pill ${window.currentAthleteFilter === athlete.id ? 'active' : ''}" 
                                    onclick="setAthleteFilter(${athlete.id})">
                                ${athlete.first_name} ${athlete.last_name}
                            </button>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Bulk Actions Bar -->
                <div id="bulk-actions" style="display: none; margin-bottom: 1rem; padding: 1rem; background: #f0f8ff; border-radius: 5px; border-left: 4px solid var(--info-color);">
                    <strong>Selezionate: <span id="selected-count">0</span> attività</strong>
                    <div style="margin-top: 0.5rem; display: flex; gap: 0.5rem;">
                        <button class="btn btn-danger btn-sm" onclick="bulkDeleteActivities()">
                            <i class="bi bi-trash"></i> Elimina Selezionate
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="clearActivitySelection()">
                            <i class="bi bi-x"></i> Annulla Selezione
                        </button>
                    </div>
                </div>
                
                <!-- Activities Table -->
                <div id="activities-table">
                    ${renderActivitiesTable(filteredActivities)}
                </div>
            </div>
        </div>
    `;
}

function renderActivitiesTable(activities) {
    if (activities.length === 0) {
        return '<p style="text-align: center; padding: 2rem; color: #666;">Nessuna attività trovata</p>';
    }
    
    let tableHtml = '<div class="table-container"><table><thead><tr>';
    tableHtml += '<th style="width: 40px;"><input type="checkbox" id="select-all-activities" onchange="toggleAllActivities()"></th>';
    tableHtml += '<th>Atleta</th><th>Titolo</th><th>Data</th><th>Tipo</th><th>Distanza</th><th>Durata</th><th>TSS</th><th>Potenza</th><th>Fonte</th><th>Azioni</th>';
    tableHtml += '</tr></thead><tbody>';
    
    activities.forEach(activity => {
        const checkbox = `<input type="checkbox" class="activity-checkbox" value="${activity.id}" onchange="updateActivitySelection()">`;
        const date = formatDate(activity.activity_date);
        const distance = activity.distance_km ? formatNumber(activity.distance_km, 1) + ' km' : '-';
        const duration = formatDuration(activity.duration_minutes);
        const tss = activity.tss ? formatNumber(activity.tss, 0) : '-';
        const watts = activity.avg_watts ? formatNumber(activity.avg_watts, 0) + 'W' : '-';
        const source = activity.source || 'manual';
        const athleteName = (window.athleteNameMap && window.athleteNameMap.get(activity.athlete_id))
            || activity.athlete_name
            || 'Unknown';
        
        tableHtml += `
            <tr>
                <td style="text-align: center;">${checkbox}</td>
                <td><strong>${athleteName}</strong></td>
                <td>${activity.title}</td>
                <td>${date}</td>
                <td>${activity.activity_type || '-'}</td>
                <td>${distance}</td>
                <td>${duration}</td>
                <td>${tss}</td>
                <td>${watts}</td>
                <td><span class="badge badge-${source}">${source}</span></td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteActivityConfirm(${activity.id})" title="Elimina">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableHtml += '</tbody></table></div>';
    return tableHtml;
}

window.setAthleteFilter = function(athleteId) {
    window.currentAthleteFilter = athleteId;
    window.selectedActivityIds.clear(); // Clear selections when changing filter
    renderActivitiesPage();
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
    createModal(
        '⚠️ Conferma Eliminazione',
        '<p>Sei sicuro di voler eliminare questa attività? L\'azione non può essere annullata.</p>',
        [
            {
                label: 'Annulla',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Elimina',
                class: 'btn-danger',
                onclick: `deleteActivityExecute(${activityId})`
            }
        ]
    );
};

window.deleteActivityExecute = async function(activityId) {
    try {
        showLoading();
        await api.deleteActivity(activityId);
        showToast('Attività eliminata con successo', 'success');
        document.querySelector('.modal-overlay')?.remove();
        window.renderActivitiesPage();
    } catch (error) {
        showToast('Errore nell\'eliminazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
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
                            <i class="bi bi-trash"></i>
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

/**
 * Handle selection of individual activity
 */
window.updateActivitySelection = function() {
    const checkboxes = document.querySelectorAll('.activity-checkbox:checked');
    window.selectedActivityIds = new Set(Array.from(checkboxes).map(cb => parseInt(cb.value)));
    
    const bulkActions = document.getElementById('bulk-actions');
    const selectedCount = document.getElementById('selected-count');
    
    if (window.selectedActivityIds.size > 0) {
        bulkActions.style.display = 'block';
        selectedCount.textContent = window.selectedActivityIds.size;
    } else {
        bulkActions.style.display = 'none';
        selectedCount.textContent = '0';
    }
};

/**
 * Toggle all activities checkbox
 */
window.toggleAllActivities = function() {
    const selectAllCheckbox = document.getElementById('select-all-activities');
    const allCheckboxes = document.querySelectorAll('.activity-checkbox');
    
    allCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    
    window.updateActivitySelection();
};

/**
 * Clear activity selection
 */
window.clearActivitySelection = function() {
    window.selectedActivityIds.clear();
    document.getElementById('select-all-activities').checked = false;
    document.querySelectorAll('.activity-checkbox').forEach(cb => cb.checked = false);
    document.getElementById('bulk-actions').style.display = 'none';
};

/**
 * Bulk delete selected activities
 */
window.bulkDeleteActivities = function() {
    const count = window.selectedActivityIds.size;
    if (count === 0) {
        showToast('Nessuna attività selezionata', 'warning');
        return;
    }
    
    createModal(
        '⚠️ Conferma Eliminazione Multipla',
        `<p>Sei sicuro di voler eliminare <strong>${count}</strong> attività? L'azione non può essere annullata.</p>`,
        [
            {
                label: 'Annulla',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: `Elimina ${count} Attività`,
                class: 'btn-danger',
                onclick: 'bulkDeleteActivitiesExecute()'
            }
        ]
    );
};

/**
 * Execute bulk delete
 */
window.bulkDeleteActivitiesExecute = async function() {
    const ids = Array.from(window.selectedActivityIds);
    
    try {
        showLoading();
        let deleted = 0;
        
        for (const id of ids) {
            try {
                await api.deleteActivity(id);
                deleted++;
            } catch (error) {
                console.error(`Errore eliminazione attività ${id}:`, error);
            }
        }
        
        showToast(`✅ Eliminate ${deleted} su ${ids.length} attività`, 'success');
        document.querySelector('.modal-overlay')?.remove();
        window.renderActivitiesPage();
    } catch (error) {
        showToast('Errore nell\'eliminazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};
