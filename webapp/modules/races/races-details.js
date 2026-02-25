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
                        <button class="tab-btn active" onclick="switchRaceTab('details')">📋 Dettagli</button>
                        <button class="tab-btn" onclick="switchRaceTab('riders')">🚴 Riders (${raceAthletes.length})</button>
                        <button class="tab-btn" onclick="switchRaceTab('metrics')">📊 Metrics</button>
                        <button class="tab-btn" onclick="switchRaceTab('route'); initRouteTab();">🗺️ Route</button>
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
window.switchRaceTab = function(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

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
            <div class="form-group">
                <label class="form-label">Data *</label>
                <input type="date" id="detail-date" class="form-input" value="${race.race_date}" required>
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
            
            <div style="border-top: 2px solid #e0e0e0; margin: 20px 0; padding-top: 20px;">
                <h4>📊 Traccia Gara (GPX/FIT/TCX)</h4>
                <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                    <label class="btn btn-secondary" style="margin: 0; cursor: pointer;">
                        📁 Importa Traccia
                        <input type="file" id="gpx-file-input" accept=".gpx,.fit,.tcx" 
                               style="display: none;" onchange="handleGpxImport(event)">
                    </label>
                    <span id="gpx-filename" style="color: #666;">Nessun file importato</span>
                    <button type="button" class="btn btn-danger btn-sm" id="gpx-delete-btn" style="display: none;" onclick="deleteRaceGpx()">
                        🗑️ Elimina Traccia
                    </button>
                </div>
                <div id="map-container" style="width: 100%; height: 400px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9;">
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999;">
                        Importa un file GPX per visualizzare la mappa
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Note</label>
                <textarea id="detail-notes" class="form-input" rows="3">${race.notes || ''}</textarea>
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
 * Save race changes
 */
window.saveRaceChanges = async function() {
    const name = document.getElementById('detail-name')?.value.trim();
    const raceDate = document.getElementById('detail-date')?.value;
    const distance = parseFloat(document.getElementById('detail-distance')?.value);
    const speed = parseFloat(document.getElementById('detail-speed')?.value);

    if (!name || !raceDate || !distance || !speed) {
        showToast('Compila i campi obbligatori', 'warning');
        return;
    }

    // Calculate predicted KJ if there are athletes
    let predictedKj = null;
    const raceAthletes = window.currentRaceData?.athletes || [];
    if (raceAthletes.length > 0) {
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
        race_date: raceDate,
        distance_km: distance,
        category: document.getElementById('detail-category')?.value,
        gender: document.getElementById('detail-gender')?.value,
        elevation_m: document.getElementById('detail-elevation')?.value ? parseFloat(document.getElementById('detail-elevation').value) : null,
        avg_speed_kmh: speed,
        predicted_duration_minutes: (distance / speed) * 60,
        predicted_kj: predictedKj,
        notes: document.getElementById('detail-notes')?.value || null,
        // Save GPX trace data if available
        route_file: window.gpxTraceData ? JSON.stringify(window.gpxTraceData) : null
    };

    try {
        showLoading();
        await api.updateRace(currentRaceId, data);
        showToast('✅ Gara aggiornata con successo', 'success');
        setTimeout(() => loadRaces(), 500);
    } catch (error) {
        showToast('Errore nell\'aggiornamento: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
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