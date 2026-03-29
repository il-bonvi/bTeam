/**
 * Races Main Module - Primary race management interface
 * Handles race listing, table display, and basic CRUD operations
 */

// Declare global state variables if not already declared
if (typeof currentRaceId === 'undefined') {
    window.currentRaceId = null;
    window.currentRaceData = null;
    window.gpxTraceData = null;
    window.tvList = [];
    window.gpmList = [];
}

/**
 * Show athlete-selection dialog before pushing a race to Intervals.icu.
 * Shared by both the races list and the race detail page.
 */
window.showPushRaceDialog = function(race) {
    const athletes = race.athletes || [];
    if (athletes.length === 0) {
        showToast('Nessun atleta iscritto a questa gara', 'warning');
        return;
    }

    const rows = [...athletes].reverse().map(a => {
        const name = `${a.first_name || ''} ${a.last_name || ''}`.trim() || `Atleta #${a.id}`;
        const hasKey = !!a.has_api_key;
        return `<label style="display:flex;align-items:center;gap:10px;padding:8px 4px;
                              border-bottom:1px solid #f0f0f0;
                              cursor:${hasKey ? 'pointer' : 'not-allowed'};
                              ${hasKey ? '' : 'opacity:0.45;'}">
            <input type="checkbox" name="push-athlete" value="${a.id}"
                   ${hasKey ? 'checked' : 'disabled'}
                   style="width:18px;height:18px;accent-color:#3b82f6;flex-shrink:0;">
            <span>${name}</span>
            ${hasKey
                ? '<span style="margin-left:auto;font-size:11px;color:#22c55e;">✓ API key</span>'
                : '<span style="margin-left:auto;font-size:11px;color:#ef4444;">✗ no API key</span>'}
        </label>`;
    }).join('');

    const stagesNote = race.num_stages > 1
        ? `<p style="margin:0 0 12px;color:#666;font-size:13px;">📋 Corsa a tappe: ${race.num_stages} tappe per atleta</p>`
        : '';

    const modal = createModal(
        `🚀 Push "${race.name}" su Intervals.icu`,
        `${stagesNote}
        <p style="margin:0 0 10px;font-size:14px;">Seleziona gli atleti a cui fare il push:</p>
        <div style="border:1px solid #e0e0e0;border-radius:6px;overflow:hidden;">
            <label style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                          background:#f5f5f5;cursor:pointer;font-weight:600;">
                <input type="checkbox" id="push-select-all" checked
                       style="width:18px;height:18px;accent-color:#3b82f6;flex-shrink:0;">
                <span>Seleziona tutti</span>
            </label>
            <div style="padding:0 12px;max-height:280px;overflow-y:auto;">${rows}</div>
        </div>`,
        [
            { label: 'Annulla', class: 'btn-secondary', onclick: 'this.closest(".modal-overlay").remove()' },
            { label: '🚀 Push selezionati', class: 'btn-success', onclick: '__pushSelected()' }
        ]
    );

    // "Select all" toggle
    modal.querySelector('#push-select-all').addEventListener('change', function() {
        modal.querySelectorAll('input[name="push-athlete"]:not([disabled])').forEach(c => c.checked = this.checked);
    });
    // Keep "select all" in sync with individual checkboxes
    modal.querySelectorAll('input[name="push-athlete"]').forEach(cb => {
        cb.addEventListener('change', () => {
            const all = [...modal.querySelectorAll('input[name="push-athlete"]:not([disabled])')];
            modal.querySelector('#push-select-all').checked = all.every(c => c.checked);
        });
    });

    // Attach push action (defined on window to be reachable from eval'd onclick)
    window.__pushSelected = async function() {
        const checked = [...modal.querySelectorAll('input[name="push-athlete"]:checked')]
            .map(c => parseInt(c.value));
        if (checked.length === 0) {
            showToast('Seleziona almeno un atleta', 'warning');
            return;
        }
        modal.remove();
        delete window.__pushSelected;
        try {
            showLoading();
            const result = await api.pushRace(race.id, checked);
            if (!result.success) {
                showToast('⚠️ ' + result.message, 'warning');
            } else {
                showToast(`✅ Gara pushata a ${result.athletes_processed} atleta/i`, 'success');
            }
        } catch (err) {
            showToast('❌ Errore: ' + (err.message || err), 'error');
        } finally {
            hideLoading();
        }
    };
};

/**
 * Main function to render the races page
 * Shows races table with actions
 */
window.renderRacesPage = async function() {
    const contentArea = document.getElementById('content-area');

    // Se c'è una gara selezionata, mostra i dettagli
    if (window.currentRaceView !== null && window.currentRaceView !== undefined) {
        await window.renderRaceDetailsPage(window.currentRaceView);
        return;
    }

    // Ripristina la top-bar quando si torna alla lista gare
    document.querySelector('.top-bar')?.style.setProperty('display', '');

    try {
        showLoading();
        const races = await api.getRaces();

        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Gestione Gare</h3>
                    <button class="btn btn-primary" onclick="showCreateRaceDialog()">
                        <i class="bi bi-plus"></i> Nuova Gara
                    </button>
                </div>
                <div id="races-table"></div>
            </div>
        `;

        // Build HTML table with expandable multi-stage races
        let tableHtml = `
            <table class="table table-striped" style="margin-bottom: 0;">
                <thead>
                    <tr>
                        <th style="width: 50px;"></th>
                        <th>ID</th>
                        <th>Nome Gara</th>
                        <th>Periodo</th>
                        <th>Distanza (km)</th>
                        <th>Categoria</th>
                        <th>Genere</th>
                        <th>Dislivello (m)</th>
                        <th>Durata</th>
                        <th>KJ</th>
                        <th>Azioni</th>
                    </tr>
                </thead>
                <tbody>
        `;

        for (const race of races) {
            const isMultiStage = race.num_stages && race.num_stages > 1;
            const raceId = race.id;
            const start = formatDate(race.race_date_start);
            const end = formatDate(race.race_date_end);
            const dateRange = start === end ? start : `${start} → ${end}`;
            const stages = race.stages || [];

            // Parent race row
            tableHtml += `
                <tr class="race-row" data-race-id="${raceId}">
                    <td style="text-align: center;">
                        ${isMultiStage ? `
                            <button class="btn-expand" onclick="window.toggleStages(${raceId})" style="
                                background: none;
                                border: none;
                                font-size: 1.2rem;
                                cursor: pointer;
                                padding: 0;
                                width: 30px;
                                height: 30px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                            ">
                                ▶
                            </button>
                        ` : ''}
                    </td>
                    <td>${raceId}</td>
                    <td><strong>${race.name}${isMultiStage ? ` <span style="color: #999;">(${race.num_stages} tappe)</span>` : ''}</strong></td>
                    <td>${dateRange}</td>
                    <td>${race.distance_km ? formatNumber(race.distance_km, 1) : '-'}</td>
                    <td>${race.category || '-'}</td>
                    <td>${race.gender || '-'}</td>
                    <td>${race.elevation_m ? formatNumber(race.elevation_m, 0) : '-'}</td>
                    <td>${isMultiStage ? `<strong>${race.num_stages} tappe</strong>` : (race.predicted_duration_minutes ? formatDuration(race.predicted_duration_minutes) : '-')}</td>
                    <td>${race.predicted_kj ? formatNumber(race.predicted_kj, 0) : '-'}</td>
                    <td>
                        <div style="display:flex; gap:4px; align-items:center; flex-wrap:nowrap;">
                            <button class="btn btn-secondary btn-sm" onclick="viewRaceDetails(${raceId})" title="Visualizza dettagli">
                                <i class="bi bi-eye"></i> Dettagli
                            </button>
                            <button class="btn btn-info btn-sm" onclick="pushRaceToIntervals(${raceId})" title="Push su Intervals.icu">
                                <i class="bi bi-cloud-arrow-up"></i> Intervals
                            </button>
                            ${!isMultiStage ? `
                            <button class="btn btn-warning btn-sm" onclick="window.openRaceActivitySelector(${raceId})" title="Seleziona attività Intervals">
                                <i class="bi bi-target"></i> Attività
                            </button>
                            ` : ''}
                            <button class="btn btn-danger btn-sm" onclick="deleteRaceConfirm(${raceId})" title="Elimina gara">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;

            // Stage rows (hidden by default if multi-stage)
            if (isMultiStage) {
                for (const stage of stages) {
                    const stageDate = stage.stage_date ? formatDate(stage.stage_date) : '—';
                    tableHtml += `
                        <tr class="stage-row" data-race-id="${raceId}" style="display:none; background: #f9f9f9;">
                            <td style="padding-left: 50px;"></td>
                            <td>—</td>
                            <td><em>Tappa ${stage.stage_number}</em></td>
                            <td>${stageDate}</td>
                            <td>${stage.distance_km ? formatNumber(stage.distance_km, 1) : '-'}</td>
                            <td>—</td>
                            <td>—</td>
                            <td>${stage.elevation_m ? formatNumber(stage.elevation_m, 0) : '-'}</td>
                            <td>—</td>
                            <td>—</td>
                            <td>
                                <div style="display:flex; gap:4px; align-items:center; flex-wrap:nowrap;">
                                    <button class="btn btn-secondary btn-sm" onclick="viewRaceDetails(${raceId})" title="Visualizza dettagli">
                                        <i class="bi bi-eye"></i> Dettagli
                                    </button>
                                    <button class="btn btn-warning btn-sm" onclick="window.openRaceActivitySelector(${raceId}, ${stage.stage_number})" title="Seleziona attività Intervals">
                                        <i class="bi bi-target"></i> Attività
                                    </button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteRaceConfirm(${raceId})" title="Elimina gara">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                }
            }
        }

        tableHtml += `
                </tbody>
            </table>
        `;

        document.getElementById('races-table').innerHTML = tableHtml;

    } catch (error) {
        showToast('Errore nel caricamento delle gare', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

/**
 * Toggle visibility of stage rows for multi-stage races
 */
window.toggleStages = function(raceId) {
    const stageRows = document.querySelectorAll(`tr.stage-row[data-race-id="${raceId}"]`);
    const toggleBtn = document.querySelector(`tr.race-row[data-race-id="${raceId}"] .btn-expand`);
    
    if (!stageRows.length) return;
    
    const isVisible = stageRows[0].style.display !== 'none';
    
    stageRows.forEach(row => {
        row.style.display = isVisible ? 'none' : 'table-row';
    });
    
    // Rotate arrow icon
    if (toggleBtn) {
        toggleBtn.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(90deg)';
        toggleBtn.style.transition = 'transform 0.2s ease';
    }
};

/**
 * Format duration from minutes to human readable
 */
function formatDuration(minutes) {
    if (!minutes) return '-';
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}m`;
}

/**
 * Delete race with confirmation dialog
 */
window.deleteRaceConfirm = function(raceId) {
    createModal(
        '⚠️ Conferma Eliminazione',
        '<p>Sei sicuro di voler eliminare questa gara? L\'azione non può essere annullata.</p>',
        [
            {
                label: 'Annulla',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Elimina',
                class: 'btn-danger',
                onclick: `deleteRace(${raceId})`
            }
        ]
    );
};

/**
 * Delete race API call
 */
window.deleteRace = async function(raceId) {
    try {
        showLoading();
        await api.deleteRace(raceId);
        showToast('Gara eliminata con successo', 'success');

        // Close modal and refresh
        document.querySelector('.modal-overlay')?.remove();
        renderRacesPage();

    } catch (error) {
        showToast('Errore nell\'eliminazione della gara', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

/**
 * Push race to Intervals.icu for all enrolled athletes
 */
window.pushRaceToIntervals = async function(raceId) {
    let race;
    try {
        showLoading();
        race = await api.getRace(raceId);
    } catch (err) {
        showToast('Errore nel caricamento della gara: ' + err.message, 'error');
        return;
    } finally {
        hideLoading();
    }

    showPushRaceDialog(race);
};