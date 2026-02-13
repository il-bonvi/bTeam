/**
 * Races Details Module - Race details modal with tabs
 * Handles race detail viewing/editing with Details, Riders, and Metrics tabs
 */

/**
 * View race details in modal with three tabs
 */
window.viewRaceDetails = async function(raceId) {
    currentRaceId = raceId;
    gpxTraceData = null;
    tvList = [];
    gpmList = [];
    
    try {
        showLoading();
        const [race, allAthletes] = await Promise.all([
            api.getRace(raceId),
            api.getAthletes()
        ]);
        
        currentRaceData = race;
        const raceAthletes = race.athletes || [];
        
        const modalContent = `
            <style>
                .tabs-container { display: flex; flex-direction: column; height: 100%; }
                .tabs-header { display: flex; border-bottom: 2px solid #e0e0e0; margin-bottom: 15px; }
                .tab-btn { 
                    background: none; border: none; padding: 10px 20px; cursor: pointer; 
                    font-size: 16px; border-bottom: 3px solid transparent; transition: all 0.3s;
                }
                .tab-btn:hover { background: #f5f5f5; }
                .tab-btn.active { border-bottom-color: #3b82f6; color: #3b82f6; font-weight: bold; }
                .tabs-content { flex: 1; overflow-y: auto; }
                .tab-pane { display: none; }
                .tab-pane.active { display: block; }
                .data-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                .data-table th, .data-table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                .data-table th { background: #f5f5f5; font-weight: bold; }
                .data-table tr:hover { background: #f9f9f9; }
            </style>
            <div class="tabs-container">
                <div class="tabs-header">
                    <button class="tab-btn active" onclick="switchRaceTab('details')">📋 Dettagli</button>
                    <button class="tab-btn" onclick="switchRaceTab('riders')">🚴 Riders (${raceAthletes.length})</button>
                    <button class="tab-btn" onclick="switchRaceTab('metrics')">📊 Metrics</button>
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
                </div>
            </div>
        `;
        
        createModal(
            `📋 ${race.name}`,
            modalContent,
            [
                {
                    label: 'Annulla',
                    class: 'btn-secondary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                },
                {
                    label: '💾 Salva Modifiche',
                    class: 'btn-primary',
                    onclick: 'saveRaceChanges()'
                }
            ],
            'xlarge'
        );
        
        setTimeout(() => {
            updateDetailCategories();
            updateDetailPredictions();
        }, 100);
        
    } catch (error) {
        showToast('Errore nel caricamento dei dettagli', 'error');
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
                    <select id="detail-category" class="form-input"></select>
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
                    <input type="number" id="detail-elevation" class="form-input" step="1" 
                           value="${race.elevation_m || 0}">
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
                    <span id="detail-duration-preview">${formatDuration(race.predicted_duration_minutes)}</span>
                </div>
                <div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">
                    <strong style="color: #60a5fa;">⚡ KJ previsti:</strong>
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
 * Update detail categories based on gender
 */
window.updateDetailCategories = function() {
    const gender = document.getElementById('detail-gender')?.value;
    const categorySelect = document.getElementById('detail-category');
    if (!gender || !categorySelect) return;
    
    const currentCategory = currentRaceData?.category || '';
    
    const categories = {
        'Femminile': ['Allieve', 'Junior', 'Junior 1NC', 'Junior 2NC', 'Junior (OPEN)', 'OPEN'],
        'Maschile': ['U23']
    };
    
    categorySelect.innerHTML = categories[gender].map(cat => 
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
    
    const raceAthletes = currentRaceData?.athletes || [];
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
    
    const data = {
        name: name,
        race_date: raceDate,
        distance_km: distance,
        category: document.getElementById('detail-category')?.value,
        gender: document.getElementById('detail-gender')?.value,
        elevation_m: document.getElementById('detail-elevation')?.value ? parseFloat(document.getElementById('detail-elevation').value) : null,
        avg_speed_kmh: speed,
        notes: document.getElementById('detail-notes')?.value || null
    };
    
    try {
        showLoading();
        await api.updateRace(currentRaceId, data);
        showToast('✅ Gara aggiornata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderRacesPage();
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