/**
 * Races Details Module - Race details modal with tabs
 * Handles race detail viewing/editing with Details, Riders, and Metrics tabs
 */

/**
 * View race details in full page (not modal)
 */
window.viewRaceDetails = async function(raceId) {
    window.currentRaceId = raceId;
    await window.renderRaceDetailsPage(raceId);
};

/**
 * Render race details page in full screen
 */
window.renderRaceDetailsPage = async function(raceId) {
    const contentArea = document.getElementById('content-area');
    window.currentRaceId = raceId;
    window.gpxTraceData = null;
    window.stageGpxData = null;  // Initialize for stage GPX data
    window.tvList = [];
    window.gpmList = [];

    // Nasconde la top-bar per massimizzare lo spazio nel dettaglio gara
    document.querySelector('.top-bar')?.style.setProperty('display', 'none');

    try {
        showLoading();
        const [race, allAthletes] = await Promise.all([
            api.getRace(raceId),
            api.getAthletes()
        ]);

        window.currentRaceData = race;

        // Load GPX trace data if available
        if (race.route_file) {
            try {
                window.gpxTraceData = JSON.parse(race.route_file);
            } catch (e) {
                console.warn('Could not parse GPX data:', e);
            }
        }

        const raceAthletes = race.athletes || [];

        contentArea.innerHTML = `
            <style>
                #content-area { padding: 0; }
                .race-details-container { 
                    display: flex; 
                    flex-direction: column; 
                    min-height: 100vh; 
                    position: relative;
                }
                .race-header { 
                    padding: 20px; 
                    border-bottom: 2px solid #e0e0e0; 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    flex-shrink: 0;
                }
                .race-title { margin: 0; }
                .tabs-container { 
                    display: flex; 
                    flex-direction: column; 
                    flex: 1; 
                    min-height: 0;
                }
                .tabs-header { 
                    display: flex; 
                    border-bottom: 2px solid #e0e0e0; 
                    margin: 0; 
                    background: #fafafa;
                    flex-shrink: 0;
                }
                .tab-btn { 
                    background: none; 
                    border: none; 
                    padding: 12px 20px; 
                    cursor: pointer; 
                    font-size: 16px; 
                    border-bottom: 3px solid transparent; 
                    transition: all 0.3s;
                    color: #666;
                }
                .tab-btn:hover { background: #f0f0f0; }
                .tab-btn.active { border-bottom-color: #3b82f6; color: #3b82f6; font-weight: bold; }
                .tabs-content { 
                    flex: 1; 
                    overflow-y: auto; 
                    padding: 20px; 
                }
                .tab-pane { display: none; }
                .tab-pane.active { display: block; }
                .data-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                .data-table th, .data-table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                .data-table th { background: #f5f5f5; font-weight: bold; }
                .data-table tr:hover { background: #f9f9f9; }
            </style>
            <div class="race-details-container">
                <div class="race-header">
                    <h2 class="race-title">📋 ${race.name}</h2>
                    <div style="display:flex; gap:8px; align-items:center;">
                        <button class="btn btn-primary" onclick="saveRaceChanges()">
                            💾 Salva
                        </button>
                        <button class="btn btn-success" onclick="pushRaceToIntervals(${race.id})">
                            🚀 Push Intervals
                        </button>
                        <button id="export-route-btn" class="btn btn-secondary" onclick="exportRouteHTML(window.currentRaceData?.name || 'Route', window.gpxTraceData)" title="Esporta percorso come HTML standalone" ${window.gpxTraceData ? '' : 'disabled style="opacity:0.4;cursor:not-allowed;"'}>
                            <i class="bi bi-download"></i> Export Route
                        </button>
                        <button class="btn btn-secondary" onclick="loadRaces()">
                            ← Indietro
                        </button>
                    </div>
                </div>
                <div class="tabs-container">
                    <div class="tabs-header">
                        <button class="tab-btn active" onclick="switchRaceTab(event, 'details')">📋 Dettagli</button>
                        <button class="tab-btn" onclick="switchRaceTab(event, 'riders')">🚴 Riders (${raceAthletes.length})</button>
                        <button class="tab-btn" onclick="switchRaceTab(event, 'metrics')">📊 Metrics</button>
                        ${race.num_stages > 1 ? `<button class="tab-btn" onclick="switchRaceTab(event, 'stages'); initStagesTab();">🎯 Tappe (${race.num_stages})</button>` : ''}
                        <button class="tab-btn" onclick="switchRaceTab(event, 'route'); initRouteTab();">🗺️ Route</button>
                    </div>
                    <div class="tabs-content">
                        <div id="tab-details" class="tab-pane active">
                            ${buildDetailsTab(race)}
                        </div>
                        <div id="tab-riders" class="tab-pane">
                            ${buildRidersTab(race, allAthletes)}
                        </div>
                        <div id="tab-metrics" class="tab-pane">
                            ${buildMetricsTab(race)}
                        </div>
                        ${race.num_stages > 1 ? `<div id="tab-stages" class="tab-pane">
                            ${buildStagesTab(race)}
                        </div>` : ''}
                        <div id="tab-route" class="tab-pane">
                            ${buildRouteTab(race)}
                        </div>
                    </div>
                </div>
            </div>
        `;

        setTimeout(() => {
            updateDetailCategories();
            updateDetailPredictions();

            // Load and display GPX map if available
            if (window.gpxTraceData && window.gpxTraceData.coordinates) {
                displayGpxMap(window.gpxTraceData.coordinates);
                const mapContainer = document.getElementById('map-container');
                if (mapContainer) {
                    mapContainer.style.display = 'block';
                }
                const filenameDisplay = document.getElementById('gpx-filename');
                if (filenameDisplay) {
                    filenameDisplay.textContent = '✅ Traccia caricata';
                    filenameDisplay.style.color = '#22C55E';
                }
                const deleteBtn = document.getElementById('gpx-delete-btn');
                if (deleteBtn) {
                    deleteBtn.style.display = 'inline-block';
                }
            }
        }, 100);

    } catch (error) {
        contentArea.innerHTML = `<div class="card"><p style="color: red;">Errore nel caricamento: ${error.message}</p></div>`;
        console.error(error);
    } finally {
        hideLoading();
    }
};

/**
 * Switch between race detail tabs
 */
window.switchRaceTab = function(evt, tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    evt.target.classList.add('active');

    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');
};

/**
 * Build details tab content
 */
function buildDetailsTab(race) {
    return `
        <div style="padding: 15px;">
            <div class="form-group">
                <label class="form-label">Nome Gara *</label>
                <input type="text" id="detail-name" class="form-input" value="${race.name}" required>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="form-group">
                    <label class="form-label">Data Inizio *</label>
                    <input type="date" id="detail-date-start" class="form-input" value="${race.race_date_start}" required onchange="syncDetailRaceDateEnd()">
                </div>
                <div class="form-group">
                    <label class="form-label">Data Fine *</label>
                    <input type="date" id="detail-date-end" class="form-input" value="${race.race_date_end}" required onchange="validateDetailRaceDateEnd()">
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">N. Tappe *</label>
                <input type="number" id="detail-num-stages" class="form-input" min="1" value="${race.num_stages || 1}" required>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="form-group">
                    <label class="form-label">Genere</label>
                    <select id="detail-gender" class="form-input" onchange="updateDetailCategories()">
                        <option value="Femminile" ${race.gender === 'Femminile' ? 'selected' : ''}>Femminile</option>
                        <option value="Maschile" ${race.gender === 'Maschile' ? 'selected' : ''}>Maschile</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Categoria</label>
                    <select id="detail-category" class="form-input">
                        <option value="${race.category}">${race.category}</option>
                    </select>
                </div>
            </div>
            ${race.num_stages <= 1 ? `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="form-group">
                    <label class="form-label">Distanza (km) *</label>
                    <input type="number" id="detail-distance" class="form-input" step="0.1" 
                           value="${race.distance_km}" oninput="updateDetailPredictions()" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Dislivello (m)</label>
                    <input type="number" id="detail-elevation" class="form-input" 
                           value="${race.elevation_m || ''}">
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Velocità Media Prevista (km/h) *</label>
                <input type="number" id="detail-speed" class="form-input" step="0.1" 
                       value="${race.avg_speed_kmh || 25}" oninput="updateDetailPredictions()" required>
            </div>
            ` : ''}
            
            ${race.num_stages <= 1 ? `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                <div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">
                    <strong style="color: #4ade80;">⏱ Durata prevista:</strong>
                    <span id="detail-duration-preview">${race.predicted_duration_minutes ? formatDuration(race.predicted_duration_minutes) : '--'}</span>
                </div>
                <div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">
                    <strong style="color: #60a5fa;">⚡ KJ previsti (media):</strong>
                    <span id="detail-kj-preview">${race.predicted_kj ? Math.round(race.predicted_kj) : '--'}</span>
                </div>
            </div>
            ` : `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                <div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">
                    <strong style="color: #666;">📌 Statistiche per tappa:</strong>
                    <span style="color: #666;">Visualizzabili nella tab Tappe</span>
                </div>
            </div>
            `}
            
            ${race.num_stages <= 1 ? `
            <div class="form-group">
                <label class="form-label">Link BRD</label>
                <input type="url" id="detail-route-link" class="form-input" placeholder="https://il-bonvi.github.io/bonvi-race-database/gare/..."
                       value="${race.route_link || ''}">
            </div>
            
            <div style="border-top: 2px solid #e0e0e0; margin: 20px 0; padding-top: 20px;">
                <h4>📊 Traccia Gara (GPX/FIT/TCX)</h4>
                ${race.route_file ? `
                    <!-- GPX imported -->
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                        <span id="gpx-filename" style="color: #22C55E; font-weight: bold;">✅ Traccia caricata</span>
                        <button type="button" class="btn btn-danger btn-sm" id="gpx-delete-btn" onclick="deleteRaceGpx()">
                            🗑️ Elimina Traccia
                        </button>
                    </div>
                    <div id="map-container" style="width: 100%; height: 400px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9;">
                        <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">
                            Mappa GPX
                        </div>
                    </div>
                ` : race.route_link ? `
                    <!-- Bonvi link available but no GPX -->
                    <div style="padding: 15px; background: #e0f2fe; border: 2px dashed #0284c7; border-radius: 8px; margin-bottom: 10px;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                            <span style="font-size: 20px;">🗺️</span>
                            <span style="color: #0369a1; font-weight: 500;">Percorso disponibile su Bonvi Race Database</span>
                        </div>
                        <a href="${race.route_link}" target="_blank" class="btn btn-primary" style="display: inline-block;">
                            🔗 Apri Percorso su Bonvi
                        </a>
                        <p style="margin: 10px 0 0 0; font-size: 0.9rem; color: #0369a1;">Puoi comunque importare un file GPX per visualizzare la mappa qui.</p>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                        <label class="btn btn-secondary" style="margin: 0; cursor: pointer;">
                            📁 Importa GPX (opzionale)
                            <input type="file" id="gpx-file-input" accept=".gpx,.fit,.tcx" 
                                   style="display: none;" onchange="handleGpxImport(event)">
                        </label>
                    </div>
                ` : `
                    <!-- No GPX, no bonvi link -->
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                        <label class="btn btn-secondary" style="margin: 0; cursor: pointer;">
                            📁 Importa Traccia
                            <input type="file" id="gpx-file-input" accept=".gpx,.fit,.tcx" 
                                   style="display: none;" onchange="handleGpxImport(event)">
                        </label>
                        <span id="gpx-filename" style="color: #666;">Nessun file importato</span>
                    </div>
                    <div id="map-container" style="width: 100%; height: 400px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9;">
                        <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">
                            Importa un file GPX per visualizzare la mappa
                        </div>
                    </div>
                `}
            </div>
            ` : ''}
            
            <div class="form-group">
                <label class="form-label">Note</label>
                <textarea id="detail-notes" class="form-input" rows="3">${race.notes || ''}</textarea>
            </div>
        </div>
    `;
}

/**
 * Build stages tab content - only shown for multi-stage races
 */
function buildStagesTab(race) {
    let stageOptionsHtml = '';
    for (let i = 1; i <= race.num_stages; i++) {
        stageOptionsHtml += `<option value="${i}">Tappa ${i} di ${race.num_stages}</option>`;
    }
    
    return `
        <div style="padding: 15px;">
            <div class="form-group">
                <label class="form-label">Seleziona Tappa</label>
                <select id="stages-stage-selector" class="form-input" onchange="loadStagesTabData()">
                    ${stageOptionsHtml}
                </select>
            </div>

            <div id="stages-details-container" style="background: #f9f9f9; padding: 15px; border-radius: 5px; border: 1px solid #e0e0e0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                    <div class="form-group">
                        <label class="form-label">Distanza (km)</label>
                        <input type="number" id="stages-stage-distance" class="form-input" step="0.1" placeholder="km"
                               oninput="updateStagesPredictions(); scheduleStageAutoSave();">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Dislivello (m)</label>
                        <input type="number" id="stages-stage-elevation" class="form-input" step="1" placeholder="m"
                               oninput="updateStagesPredictions(); scheduleStageAutoSave();">
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Data Tappa</label>
                    <input type="date" id="stages-stage-date" class="form-input" onchange="scheduleStageAutoSave();">
                </div>

                <div class="form-group">
                    <label class="form-label">Link BRD</label>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <input type="url" id="stages-route-link" class="form-input"
                            placeholder="Es: …/bizkaikoloreak-S1-2025-DJ/ (singola tappa)"
                            style="flex: 1;" onchange="scheduleStageAutoSave();">
                        <button type="button" onclick="loadStageFromBonvi()" class="btn btn-primary"
                                style="white-space: nowrap; padding: 10px 14px;">📥 Carica BRD</button>
                    </div>
                    <div id="stages-bonvi-loading" style="display: none; margin-top: 6px; padding: 6px 10px; background: #e0f2fe; border-radius: 5px; color: #0369a1;">⏳ Caricamento...</div>
                    <div id="stages-bonvi-success" style="display: none; margin-top: 6px; padding: 6px 10px; background: #dcfce7; border-radius: 5px; color: #166534;"></div>
                    <div id="stages-bonvi-error"   style="display: none; margin-top: 6px; padding: 6px 10px; background: #fee2e2; border-radius: 5px; color: #b91c1c;"></div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Note Tappa</label>
                    <textarea id="stages-stage-notes" class="form-input" rows="2"
                              placeholder="Note specifiche per questa tappa"
                              oninput="scheduleStageAutoSave();"></textarea>
                </div>
            </div>
            
            <div style="border-top: 2px solid #e0e0e0; margin: 20px 0; padding-top: 20px;">
                <h4>⚡ Statistiche Tappa</h4>
                <div class="form-group">
                    <label class="form-label">Velocità Media Prevista (km/h) *</label>
                    <input type="number" id="stages-speed" class="form-input" step="0.1" 
                           placeholder="25" oninput="updateStagesPredictions()" required>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                    <div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">
                        <strong style="color: #4ade80;">⏱ Durata prevista:</strong>
                        <span id="stages-duration-preview">--</span>
                    </div>
                    <div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">
                        <strong style="color: #60a5fa;">⚡ KJ previsti:</strong>
                        <span id="stages-kj-preview">--</span>
                    </div>
                </div>
            </div>
            
            <div style="border-top: 2px solid #e0e0e0; margin: 20px 0; padding-top: 20px;">
                <h4>📊 Traccia Tappa (GPX/FIT/TCX)</h4>
                <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                    <label class="btn btn-secondary" style="margin: 0; cursor: pointer;">
                        📁 Importa Traccia Tappa
                        <input type="file" id="stages-gpx-file-input" accept=".gpx,.fit,.tcx" 
                               style="display: none;" onchange="handleStagesGpxImport(event)">
                    </label>
                    <span id="stages-gpx-filename" style="color: #666;">Nessun file</span>
                    <button type="button" class="btn btn-danger btn-sm" id="stages-gpx-delete-btn" style="display: none;" onclick="deleteStagesGpx()">
                        🗑️ Elimina Traccia
                    </button>
                </div>
                <div id="stages-map-container" style="width: 100%; height: 400px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9;">
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">
                        Seleziona una tappa e importa il file GPX per visualizzare la mappa
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Delete GPX trace from race
 */
window.deleteRaceGpx = function() {
    window.gpxTraceData = null;

    const filenameDisplay = document.getElementById('gpx-filename');
    if (filenameDisplay) {
        filenameDisplay.textContent = 'Nessun file importato';
        filenameDisplay.style.color = '#666';
    }

    const deleteBtn = document.getElementById('gpx-delete-btn');
    if (deleteBtn) {
        deleteBtn.style.display = 'none';
    }

    const mapContainer = document.getElementById('map-container');
    if (mapContainer) {
        mapContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">
                Importa un file GPX per visualizzare la mappa
            </div>
        `;
    }

    const exportBtn = document.getElementById('export-route-btn');
    if (exportBtn) {
        exportBtn.disabled = true;
        exportBtn.style.opacity = '0.4';
        exportBtn.style.cursor = 'not-allowed';
    }

    const iframe = document.getElementById('route-visualizer-iframe');
    if (iframe) {
        iframe.dataset.loaded = 'false';
    }

    showToast('✅ Traccia eliminata', 'success');
};

/**
 * Update detail categories based on gender
 */
window.updateDetailCategories = function() {
    const genderSelect = document.getElementById('detail-gender');
    const gender = genderSelect?.value || 'Femminile';
    const categorySelect = document.getElementById('detail-category');
    if (!categorySelect) return;

    const currentCategory = window.currentRaceData?.category || '';

    const categories = {
        'Femminile': ['Allieve', 'Junior', 'Junior 1NC', 'Junior 2NC', 'Junior (OPEN)', 'OPEN'],
        'Maschile': ['U23']
    };

    let categoryList = categories[gender] || [...categories.Femminile, ...categories.Maschile];
    if (currentCategory && !categoryList.includes(currentCategory)) {
        categoryList = [currentCategory, ...categoryList];
    }
    categorySelect.innerHTML = categoryList.map(cat =>
        `<option value="${cat}" ${cat === currentCategory ? 'selected' : ''}>${cat}</option>`
    ).join('');
};

/**
 * Update detail predictions when form data changes
 */
window.updateDetailPredictions = function() {
    const distanceEl = document.getElementById('detail-distance');
    const speedEl = document.getElementById('detail-speed');
    if (!distanceEl || !speedEl) return;

    const distance = parseFloat(distanceEl.value) || 0;
    const speed = parseFloat(speedEl.value) || 0;

    const durationPreview = document.getElementById('detail-duration-preview');
    const kjPreview = document.getElementById('detail-kj-preview');

    if (!durationPreview || !kjPreview) return;

    if (speed <= 0 || distance <= 0) {
        durationPreview.textContent = '--';
        kjPreview.textContent = '--';
        return;
    }

    const durationMinutes = (distance / speed) * 60;
    durationPreview.textContent = formatDuration(durationMinutes);

    const raceAthletes = window.currentRaceData?.athletes || [];
    if (raceAthletes.length > 0) {
        let totalKj = 0;
        const durationHours = durationMinutes / 60;

        raceAthletes.forEach(ra => {
            const weight = ra.weight_kg || 70;
            const kjPerHourPerKg = ra.kj_per_hour_per_kg || 10.0;
            totalKj += kjPerHourPerKg * weight * durationHours;
        });

        const avgKj = totalKj / raceAthletes.length;
        kjPreview.textContent = Math.round(avgKj);
    } else {
        kjPreview.textContent = '--';
    }

    // Update riders table if visible
    if (document.getElementById('riders-table')) {
        refreshRidersKJ();
    }
};

/**
 * Refresh race details from server without navigating away
 */
window.refreshRaceDetails = async function(raceId) {
    try {
        // Reload race data from API
        const race = await api.getRace(raceId);
        window.currentRaceData = race;
        
        // Update form fields with latest data
        document.getElementById('detail-name').value = race.name || '';
        document.getElementById('detail-date-start').value = race.race_date_start || '';
        document.getElementById('detail-date-end').value = race.race_date_end || '';
        document.getElementById('detail-num-stages').value = race.num_stages || 1;
        const detailDistanceInput = document.getElementById('detail-distance');
        if (detailDistanceInput) {
            detailDistanceInput.value = race.distance_km || '';
        }
        const detailSpeedInput = document.getElementById('detail-speed');
        if (detailSpeedInput) {
            detailSpeedInput.value = race.avg_speed_kmh || '';
        }
        document.getElementById('detail-category').value = race.category || 'C';
        document.getElementById('detail-gender').value = race.gender || '';
        document.getElementById('detail-elevation').value = race.elevation_m || '';
        document.getElementById('detail-notes').value = race.notes || '';
        
        // Refresh riders table
        const ridersTableBody = document.querySelector('#riders-table tbody');
        if (ridersTableBody && race.athletes && race.athletes.length > 0) {
            ridersTableBody.innerHTML = race.athletes.map(ra => buildRiderRow(ra)).join('');
        }
        
        // Refresh KJ totals
        refreshRidersKJ();
        
        // Load first stage data if multi-stage race
        if (race.num_stages > 1) {
            setTimeout(() => {
                const stageSelector = document.getElementById('detail-stage-selector');
                if (stageSelector) {
                    stageSelector.value = '1';
                    loadStageSelectorData();
                }
            }, 100);
        }
    } catch (error) {
        console.error('Error refreshing race details:', error);
    }
};

/**
 * Save race changes
 */
window.saveRaceChanges = async function() {
    const name = document.getElementById('detail-name')?.value.trim();
    const raceDateStart = document.getElementById('detail-date-start')?.value;
    const raceDateEnd = document.getElementById('detail-date-end')?.value;
    const numStages = parseInt(document.getElementById('detail-num-stages')?.value) || 1;
    
    // Distance and speed are only required for single-stage races
    let distance = null;
    let speed = null;
    
    if (numStages <= 1) {
        distance = parseFloat(document.getElementById('detail-distance')?.value);
        speed = parseFloat(document.getElementById('detail-speed')?.value);
        
        if (!distance || !speed) {
            showToast('Compila i campi obbligatori: Distanza e Velocità Media', 'warning');
            return;
        }
    } else {
        // For multi-stage races, try to get distance from stages
        distance = document.getElementById('detail-distance')?.value ? parseFloat(document.getElementById('detail-distance').value) : null;
        speed = document.getElementById('detail-speed')?.value ? parseFloat(document.getElementById('detail-speed').value) : 25;
    }

    if (!name || !raceDateStart || !raceDateEnd) {
        showToast('Compila i campi obbligatori: Nome, Date Inizio e Fine', 'warning');
        return;
    }

    if (new Date(raceDateEnd) < new Date(raceDateStart)) {
        showToast('La data fine deve essere successiva o uguale alla data inizio', 'warning');
        return;
    }

    // Calculate predicted KJ if there are athletes
    let predictedKj = null;
    const raceAthletes = window.currentRaceData?.athletes || [];
    if (raceAthletes.length > 0 && distance && speed) {
        let totalKj = 0;
        const durationHours = (distance / speed);

        raceAthletes.forEach(ra => {
            const weight = ra.weight_kg || 70;
            const kjPerHourPerKg = ra.kj_per_hour_per_kg || 10.0;
            totalKj += kjPerHourPerKg * weight * durationHours;
        });

        predictedKj = totalKj / raceAthletes.length;
    }

    const data = {
        name: name,
        race_date_start: raceDateStart,
        race_date_end: raceDateEnd,
        num_stages: numStages,
        distance_km: distance,
        category: document.getElementById('detail-category')?.value,
        gender: document.getElementById('detail-gender')?.value,
        elevation_m: document.getElementById('detail-elevation')?.value ? parseFloat(document.getElementById('detail-elevation').value) : null,
        avg_speed_kmh: speed,
        predicted_duration_minutes: (distance && speed) ? (distance / speed) * 60 : null,
        predicted_kj: predictedKj,
        notes: document.getElementById('detail-notes')?.value || null,
        route_link: document.getElementById('detail-route-link')?.value?.trim() || null,
        // Save GPX trace data if available
        route_file: window.gpxTraceData ? JSON.stringify(window.gpxTraceData) : null
    };

    try {
        showLoading();
        await api.updateRace(currentRaceId, data);
        showToast('✅ Gara aggiornata con successo', 'success');
        // Reload current race data without navigating away
        await refreshRaceDetails(currentRaceId);
    } catch (error) {
        showToast('Errore nell\'aggiornamento: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

/**
 * Sync end date when start date changes - only if end date becomes invalid
 */
window.syncDetailRaceDateEnd = function() {
    const startDate = document.getElementById('detail-date-start').value;
    const endDate = document.getElementById('detail-date-end').value;
    
    // Only sync if end date is before start date
    if (new Date(endDate) < new Date(startDate)) {
        document.getElementById('detail-date-end').value = startDate;
    }
};

/**
 * Validate that end date is not before start date
 */
window.validateDetailRaceDateEnd = function() {
    const startDate = document.getElementById('detail-date-start').value;
    const endDate = document.getElementById('detail-date-end').value;
    
    if (new Date(endDate) < new Date(startDate)) {
        document.getElementById('detail-date-end').value = startDate;
        showToast('La data fine non può essere prima della data inizio', 'warning');
    }
};

/**
 * Load and display the selected stage data
 */
window.loadStageSelectorData = async function() {
    try {
        const stageNumber = parseInt(document.getElementById('detail-stage-selector').value);
        const raceId = window.currentRaceId;
        
        // Get all stages for this race
        const stages = await api.getStages(raceId);
        
        // Find the stage with matching stage_number
        const stage = stages.find(s => s.stage_number === stageNumber);
        
        if (stage) {
            // Populate form fields with stage data
            document.getElementById('detail-stage-distance').value = stage.distance_km || '';
            document.getElementById('detail-stage-elevation').value = stage.elevation_m || '';
            document.getElementById('detail-stage-notes').value = stage.notes || '';
            
            // Store current stage ID for saving
            window.currentStageId = stage.id;
            
            // Load GPX data if available
            window.stageGpxData = null;
            if (stage.route_file) {
                try {
                    window.stageGpxData = JSON.parse(stage.route_file);
                    document.getElementById('stage-gpx-filename').textContent = '✅ Traccia caricata';
                    document.getElementById('stage-gpx-filename').style.color = '#22C55E';
                    document.getElementById('stage-gpx-delete-btn').style.display = 'inline-block';
                } catch (e) {
                    console.warn('Could not parse stage GPX data:', e);
                    document.getElementById('stage-gpx-filename').textContent = 'File GPX non valido';
                    document.getElementById('stage-gpx-filename').style.color = '#ef4444';
                }
            } else {
                document.getElementById('stage-gpx-filename').textContent = 'Nessun file';
                document.getElementById('stage-gpx-filename').style.color = '#666';
                document.getElementById('stage-gpx-delete-btn').style.display = 'none';
            }
        } else {
            // Stage not found, reset form
            document.getElementById('detail-stage-distance').value = '';
            document.getElementById('detail-stage-elevation').value = '';
            document.getElementById('detail-stage-notes').value = '';
            window.stageGpxData = null;
            document.getElementById('stage-gpx-filename').textContent = 'Nessun file';
            document.getElementById('stage-gpx-filename').style.color = '#666';
            document.getElementById('stage-gpx-delete-btn').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading stage data:', error);
        showToast('Errore nel caricamento della tappa: ' + error.message, 'error');
    }
};

/**
 * Save individual stage data
 */
window.saveStageData = async function() {
    try {
        if (!window.currentStageId) {
            showToast('Nessuna tappa selezionata', 'warning');
            return;
        }
        
        const stageData = {
            distance_km: document.getElementById('detail-stage-distance').value 
                ? parseFloat(document.getElementById('detail-stage-distance').value) 
                : null,
            elevation_m: document.getElementById('detail-stage-elevation').value 
                ? parseInt(document.getElementById('detail-stage-elevation').value)
                : null,
            notes: document.getElementById('detail-stage-notes').value || null,
            route_link: document.getElementById('detail-stage-route-link')?.value || null,
            route_file: window.stageGpxData ? JSON.stringify(window.stageGpxData) : null
        };
        
        // Remove null values to avoid overwriting existing data unnecessarily
        Object.keys(stageData).forEach(key => 
            stageData[key] === null && delete stageData[key]
        );
        
        showLoading();
        await api.updateStage(window.currentRaceId, window.currentStageId, stageData);
        showToast('✅ Tappa aggiornata con successo', 'success');
        
        // Reload race details to reflect changes
        await refreshRaceDetails(window.currentRaceId);
    } catch (error) {
        showToast('Errore nel salvataggio della tappa: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

/**
 * Handle GPX import for stage
 */
window.handleStageGpxImport = async function(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
        showLoading();
        const text = await file.text();
        
        // Parse based on file type
        let gpxData = null;
        if (file.name.endsWith('.gpx')) {
            gpxData = parseGPXFile(text);
        } else if (file.name.endsWith('.fit')) {
            showToast('FIT files non sono ancora supportati. Per favore usa GPX o TCX.', 'warning');
            return;
        } else if (file.name.endsWith('.tcx')) {
            gpxData = parseTCXFile(text);
        } else {
            throw new Error('Formato file non supportato. Usa .gpx, .fit, o .tcx');
        }

        if (gpxData && gpxData.coordinates) {
            window.stageGpxData = gpxData;
            document.getElementById('stage-gpx-filename').textContent = '✅ ' + file.name;
            document.getElementById('stage-gpx-filename').style.color = '#22C55E';
            document.getElementById('stage-gpx-delete-btn').style.display = 'inline-block';
            // Auto-fill distance and elevation fields
            if (gpxData.totalDistance > 0) {
                document.getElementById('detail-stage-distance').value = gpxData.totalDistance.toFixed(1);
            }
            if (gpxData.elevationGain > 0) {
                document.getElementById('detail-stage-elevation').value = Math.round(gpxData.elevationGain);
            }
            showToast('📁 File ' + file.name + ' caricato con successo', 'success');
        } else {
            throw new Error('Non è stato possibile estrarre i dati di coordinate dal file');
        }
    } catch (error) {
        showToast('Errore nell\'importazione: ' + error.message, 'error');
        window.stageGpxData = null;
        document.getElementById('stage-gpx-filename').textContent = 'Errore caricamento';
        document.getElementById('stage-gpx-filename').style.color = '#ef4444';
        document.getElementById('stage-gpx-delete-btn').style.display = 'none';
    } finally {
        hideLoading();
        event.target.value = ''; // Reset file input
    }
};

/**
 * Delete GPX trace from current stage
 */
window.deleteStageGpx = function() {
    window.stageGpxData = null;
    document.getElementById('stage-gpx-filename').textContent = 'Nessun file';
    document.getElementById('stage-gpx-filename').style.color = '#666';
    document.getElementById('stage-gpx-delete-btn').style.display = 'none';
    showToast('Traccia tappa rimossa', 'info');
};

/**
 * Initialize Stages tab - load first stage data when tab is opened
 */
window.initStagesTab = async function() {
    try {
        // Load first stage by default
        const selector = document.getElementById('stages-stage-selector');
        if (selector) {
            selector.value = '1';
            await loadStagesTabData();
        }
    } catch (error) {
        console.error('Error initializing stages tab:', error);
    }
};

/**
 * Load stage data for the Stages tab (auto-saves previous stage first)
 */
window.loadStagesTabData = async function() {
    try {
        const stageNumber = parseInt(document.getElementById('stages-stage-selector').value);
        const raceId = window.currentRaceId;

        // Auto-save currently loaded stage before switching
        if (window.currentStagesTabStageId) {
            try { await _autoSaveStage(window.currentStagesTabStageId); } catch (e) { console.warn('Auto-save failed:', e); }
            window.currentStagesTabStageId = null;
        }
        
        // Get all stages for this race
        const stages = await api.getStages(raceId);
        
        // Find the stage with matching stage_number
        const stage = stages.find(s => s.stage_number === stageNumber);
        
        if (stage) {
            // Populate form fields with stage data
            document.getElementById('stages-stage-distance').value = stage.distance_km || '';
            document.getElementById('stages-stage-elevation').value = stage.elevation_m || '';
            document.getElementById('stages-stage-notes').value = stage.notes || '';
            document.getElementById('stages-stage-date').value = stage.stage_date || '';
            document.getElementById('stages-route-link').value = stage.route_link || '';
            // Load speed from database if available, otherwise use default
            document.getElementById('stages-speed').value = stage.avg_speed_kmh || '25';
            
            // Store current stage ID for saving
            window.currentStagesTabStageId = stage.id;
            
            // Load GPX data if available
            window.stagesGpxData = null;
            if (stage.route_file) {
                try {
                    window.stagesGpxData = JSON.parse(stage.route_file);
                    document.getElementById('stages-gpx-filename').textContent = '✅ Traccia caricata';
                    document.getElementById('stages-gpx-filename').style.color = '#22C55E';
                    document.getElementById('stages-gpx-delete-btn').style.display = 'inline-block';
                    
                    // Display the map for this stage
                    if (window.stagesGpxData.coordinates) {
                        displayGpxMap(window.stagesGpxData.coordinates, 'stages-map-container');
                    }
                } catch (e) {
                    console.warn('Could not parse stage GPX data:', e);
                    document.getElementById('stages-gpx-filename').textContent = 'File GPX non valido';
                    document.getElementById('stages-gpx-filename').style.color = '#ef4444';
                }
            } else {
                document.getElementById('stages-gpx-filename').textContent = 'Nessun file';
                document.getElementById('stages-gpx-filename').style.color = '#666';
                document.getElementById('stages-gpx-delete-btn').style.display = 'none';
                // Clear map
                const mapContainer = document.getElementById('stages-map-container');
                if (mapContainer && mapContainer.style.height !== '0px') {
                    mapContainer.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">Nessun file GPX per questa tappa</div>';
                }
            }
            
            // Update predictions after loading stage data
            updateStagesPredictions();
        } else {
            // Stage not found, reset form
            document.getElementById('stages-stage-distance').value = '';
            document.getElementById('stages-stage-elevation').value = '';
            document.getElementById('stages-stage-notes').value = '';
            window.stagesGpxData = null;
            document.getElementById('stages-gpx-filename').textContent = 'Nessun file';
            document.getElementById('stages-gpx-filename').style.color = '#666';
            document.getElementById('stages-gpx-delete-btn').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading stage data:', error);
        showToast('Errore nel caricamento della tappa: ' + error.message, 'error');
    }
};

/**
 * Internal helper: collect current stage form data and send to API (silent, no toast).
 */
async function _autoSaveStage(stageId) {
    if (!stageId || !window.currentRaceId) return;
    const stageData = {
        distance_km: document.getElementById('stages-stage-distance').value
            ? parseFloat(document.getElementById('stages-stage-distance').value) : null,
        elevation_m: document.getElementById('stages-stage-elevation').value
            ? parseInt(document.getElementById('stages-stage-elevation').value) : null,
        notes: document.getElementById('stages-stage-notes').value || null,
        stage_date: document.getElementById('stages-stage-date').value || null,
        route_link: document.getElementById('stages-route-link').value || null,
        avg_speed_kmh: document.getElementById('stages-speed').value
            ? parseFloat(document.getElementById('stages-speed').value) : null,
        route_file: window.stagesGpxData ? JSON.stringify(window.stagesGpxData) : null
    };
    // Keep route_link even if null so it can be cleared; drop other nulls
    Object.keys(stageData).forEach(key => {
        if (key !== 'route_link' && stageData[key] === null) delete stageData[key];
    });
    await api.updateStage(window.currentRaceId, stageId, stageData);
}

/**
 * Save stage data from Stages tab (manual button – shows toast)
 */
window.saveStagesTabData = async function() {
    if (!window.currentStagesTabStageId) {
        showToast('Nessuna tappa selezionata', 'warning');
        return;
    }
    try {
        showLoading();
        await _autoSaveStage(window.currentStagesTabStageId);
        showToast('✅ Tappa aggiornata con successo', 'success');
    } catch (error) {
        showToast('Errore nel salvataggio della tappa: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

/** Debounce timer for auto-save on field change */
let _stageAutoSaveTimer = null;
window.scheduleStageAutoSave = function() {
    clearTimeout(_stageAutoSaveTimer);
    _stageAutoSaveTimer = setTimeout(async () => {
        if (window.currentStagesTabStageId) {
            try { await _autoSaveStage(window.currentStagesTabStageId); }
            catch (e) { console.warn('Auto-save failed:', e); }
        }
    }, 800);
};

/**
 * Load individual stage data from Bonvi Race Database (reads link from stages-route-link field).
 */
window.loadStageFromBonvi = async function() {
    const link = document.getElementById('stages-route-link').value.trim();
    const loadingEl = document.getElementById('stages-bonvi-loading');
    const successEl = document.getElementById('stages-bonvi-success');
    const errorEl = document.getElementById('stages-bonvi-error');

    if (!link) {
        showToast('Inserisci il link della tappa', 'warning');
        return;
    }

    loadingEl.style.display = 'block';
    successEl.style.display = 'none';
    errorEl.style.display = 'none';

    try {
        const response = await fetch('/api/races/load-from-bonvi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ link })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Errore nel caricamento');
        }

        const data = await response.json();

        if (data.link_type === 'stage_race') {
            throw new Error('Hai incollato il link della corsa a tappe completa. Usa il link della singola tappa (con -S1-, -S2- ecc.).');
        }
        if (data.link_type === 'single_day') {
            throw new Error('Hai incollato il link di una gara di un giorno. Usa il link della singola tappa (con -S1-, -S2- ecc.).');
        }

        // link_type === 'single_stage'
        if (data.distance_km) document.getElementById('stages-stage-distance').value = data.distance_km;
        if (data.elevation_m) document.getElementById('stages-stage-elevation').value = data.elevation_m;
        if (data.stage_date) document.getElementById('stages-stage-date').value = data.stage_date;
        document.getElementById('stages-route-link').value = data.route_link || link;

        updateStagesPredictions();

        // Auto-save immediately so data is persisted for this stage
        if (window.currentStagesTabStageId) {
            try { await _autoSaveStage(window.currentStagesTabStageId); } catch (e) { console.warn('Auto-save after bonvi import failed:', e); }
        }

        loadingEl.style.display = 'none';
        successEl.style.display = 'block';
        const dist = data.distance_km ? `${data.distance_km} km` : '--';
        const elev = data.elevation_m ? `+${data.elevation_m} m` : '--';
        const dateStr = data.stage_date || '--';
        successEl.innerHTML = `✅ Tappa ${data.stage_number || ''} caricata: <strong>${data.name || '--'}</strong><br>${dist} · ${elev} · ${dateStr}`;
        setTimeout(() => { successEl.style.display = 'none'; }, 6000);

    } catch (error) {
        loadingEl.style.display = 'none';
        errorEl.style.display = 'block';
        errorEl.textContent = '❌ ' + error.message;
    }
};

/**
 * Handle GPX import for stage in Stages tab
 */
window.handleStagesGpxImport = async function(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
        showLoading();
        const text = await file.text();
        
        // Parse based on file type using existing functions
        let gpxData = null;
        if (file.name.endsWith('.gpx')) {
            gpxData = parseGPXFile(text);
        } else if (file.name.endsWith('.fit')) {
            showToast('FIT files non sono ancora supportati. Per favore usa GPX o TCX.', 'warning');
            return;
        } else if (file.name.endsWith('.tcx')) {
            gpxData = parseTCXFile(text);
        } else {
            throw new Error('Formato file non supportato. Usa .gpx, .fit, o .tcx');
        }

        if (gpxData && gpxData.coordinates) {
            window.stagesGpxData = gpxData;
            document.getElementById('stages-gpx-filename').textContent = '✅ ' + file.name;
            document.getElementById('stages-gpx-filename').style.color = '#22C55E';
            document.getElementById('stages-gpx-delete-btn').style.display = 'inline-block';
            // Auto-fill distance and elevation fields
            if (gpxData.totalDistance > 0) {
                document.getElementById('stages-stage-distance').value = gpxData.totalDistance.toFixed(1);
            }
            if (gpxData.elevationGain > 0) {
                document.getElementById('stages-stage-elevation').value = Math.round(gpxData.elevationGain);
            }
            // Update predictions after loading GPX data
            updateStagesPredictions();
            // Update map
            displayGpxMap(gpxData.coordinates, 'stages-map-container');
            showToast('📁 File ' + file.name + ' caricato con successo', 'success');
        } else {
            throw new Error('Non è stato possibile estrarre i dati di coordinate dal file');
        }
    } catch (error) {
        showToast('Errore nell\'importazione: ' + error.message, 'error');
        window.stagesGpxData = null;
        document.getElementById('stages-gpx-filename').textContent = 'Errore caricamento';
        document.getElementById('stages-gpx-filename').style.color = '#ef4444';
        document.getElementById('stages-gpx-delete-btn').style.display = 'none';
    } finally {
        hideLoading();
        event.target.value = ''; // Reset file input
    }
};

/**
 * Update stage predictions (duration and KJ) based on distance, elevation, and speed
 */
window.updateStagesPredictions = function() {
    const distanceEl = document.getElementById('stages-stage-distance');
    const speedEl = document.getElementById('stages-speed');
    const elevationEl = document.getElementById('stages-stage-elevation');
    
    if (!distanceEl || !speedEl || !elevationEl) return;

    const distance = parseFloat(distanceEl.value) || 0;
    const speed = parseFloat(speedEl.value) || 0;
    const elevation = parseFloat(elevationEl.value) || 0;

    const durationPreview = document.getElementById('stages-duration-preview');
    const kjPreview = document.getElementById('stages-kj-preview');

    if (!durationPreview || !kjPreview) return;

    if (speed <= 0 || distance <= 0) {
        durationPreview.textContent = '--';
        kjPreview.textContent = '--';
        return;
    }

    // Calculate duration
    const durationMinutes = (distance / speed) * 60;
    durationPreview.textContent = formatDuration(durationMinutes);

    // Calculate KJ (same formula as races)
    // KJ = distance * (35 + elevation/distance * 15)
    let kj = distance * 35;
    if (distance > 0) {
        kj += (elevation / distance) * 15 * distance;
    }
    kjPreview.textContent = Math.round(kj);
};

/**
 * Delete GPX trace from current stage in Stages tab
 */
window.deleteStagesGpx = function() {
    window.stagesGpxData = null;
    document.getElementById('stages-gpx-filename').textContent = 'Nessun file';
    document.getElementById('stages-gpx-filename').style.color = '#666';
    document.getElementById('stages-gpx-delete-btn').style.display = 'none';
    // Clear map
    const mapContainer = document.getElementById('stages-map-container');
    if (mapContainer) {
        mapContainer.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">Nessun file GPX per questa tappa</div>';
    }
    showToast('Traccia tappa rimossa', 'info');
};


/**
 * Format duration helper (shared with main)
 */
function formatDuration(minutes) {
    if (!minutes) return '--';
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}m`;
}

/**
 * Push race to Intervals.icu
 */
window.pushRaceToIntervals = async function(raceId) {
    const idToPush = raceId || window.currentRaceId;

    let race;
    try {
        showLoading();
        race = await api.getRace(idToPush);
    } catch (err) {
        showToast('Errore nel caricamento della gara: ' + err.message, 'error');
        return;
    } finally {
        hideLoading();
    }

    showPushRaceDialog(race);
};