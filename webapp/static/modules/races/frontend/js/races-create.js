/**
 * Races Create Module - Race creation dialog and form
 * Handles new race creation with predictions and category management
 */

/**
 * Show create race dialog with form
 */
window.showCreateRaceDialog = function() {
    const today = new Date().toISOString().split('T')[0];
    
    createModal(
        '✨ Crea Nuova Gara',
        `
        <div class="form-group">
            <label class="form-label">Nome Gara *</label>
            <input type="text" id="race-name" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Data *</label>
            <input type="date" id="race-date" class="form-input" value="${today}" required>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div class="form-group">
                <label class="form-label">Genere</label>
                <select id="race-gender" class="form-input" onchange="updateCategories()">
                    <option value="Femminile">Femminile</option>
                    <option value="Maschile">Maschile</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Categoria</label>
                <select id="race-category" class="form-input"></select>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div class="form-group">
                <label class="form-label">Distanza (km) *</label>
                <input type="number" id="race-distance" class="form-input" step="0.1" value="100" 
                       oninput="updateCreateRacePredictions()" required>
            </div>
            <div class="form-group">
                <label class="form-label">Dislivello (m)</label>
                <input type="number" id="race-elevation" class="form-input" step="1" value="500">
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">Velocità Media Prevista (km/h) *</label>
            <input type="number" id="race-speed" class="form-input" step="0.1" value="25" 
                   oninput="updateCreateRacePredictions()" required>
        </div>
        
        <!-- GPX Import Section -->
        <div class="form-group" style="border: 2px dashed #ccc; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <i class="bi bi-map" style="color: #3b82f6; font-size: 18px;"></i>
                <label class="form-label" style="margin: 0;">Import traccia GPX/FIT/TCX (Optional)</label>
            </div>
            <input type="file" id="gpx-file" accept=".gpx,.fit,.tcx" onchange="handleGpxImport()" style="margin-bottom: 10px;">
            <div id="gpx-preview" style="display: none; padding: 10px; background: #f0f8ff; border-radius: 5px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <div><strong>📍 Distanza:</strong> <span id="gpx-distance">--</span></div>
                    <div><strong>⛰️ Dislivello:</strong> <span id="gpx-elevation">--</span></div>
                </div>
                <div id="gpx-map" style="height: 200px; border-radius: 5px; margin-top: 10px;"></div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
            <div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">
                <strong style="color: #4ade80;">⏱ Durata prevista:</strong>
                <span id="create-duration-preview">--</span>
            </div>
            <div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">
                <strong style="color: #60a5fa;">⚡ KJ previsti (media):</strong>
                <span id="create-kj-preview">--</span>
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">Note</label>
            <textarea id="race-notes" class="form-input" rows="3"></textarea>
        </div>
        `,
        [
            {
                label: 'Annulla',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: '✓ Crea Gara',
                class: 'btn-primary',
                onclick: 'createRace()'
            }
        ]
    );
    
    setTimeout(() => {
        updateCategories();
        updateCreateRacePredictions();
    }, 100);
};

/**
 * Update categories based on selected gender
 */
window.updateCategories = function() {
    const gender = document.getElementById('race-gender').value;
    const categorySelect = document.getElementById('race-category');
    
    const categories = {
        'Femminile': ['Allieve', 'Junior', 'Junior 1NC', 'Junior 2NC', 'Junior (OPEN)', 'OPEN'],
        'Maschile': ['U23']
    };
    
    categorySelect.innerHTML = categories[gender].map(cat => 
        `<option value="${cat}">${cat}</option>`
    ).join('');
};

/**
 * Update race predictions (duration and KJ)
 */
window.updateCreateRacePredictions = async function() {
    const distance = parseFloat(document.getElementById('race-distance').value) || 0;
    const speed = parseFloat(document.getElementById('race-speed').value) || 0;
    
    if (speed <= 0 || distance <= 0) {
        document.getElementById('create-duration-preview').textContent = '--';
        document.getElementById('create-kj-preview').textContent = '--';
        return;
    }
    
    const durationMinutes = (distance / speed) * 60;
    const hours = Math.floor(durationMinutes / 60);
    const minutes = Math.round(durationMinutes % 60);
    document.getElementById('create-duration-preview').textContent = `${hours}h ${minutes}m`;
    
    try {
        const athletes = await api.getAthletes();
        if (athletes && athletes.length > 0) {
            let totalKj = 0;
            const durationHours = durationMinutes / 60;
            
            athletes.forEach(athlete => {
                const weight = athlete.weight_kg || 70;
                const kjPerHourPerKg = athlete.kj_per_hour_per_kg || 10.0;
                totalKj += kjPerHourPerKg * weight * durationHours;
            });
            
            const avgKj = totalKj / athletes.length;
            document.getElementById('create-kj-preview').textContent = Math.round(avgKj);
        } else {
            document.getElementById('create-kj-preview').textContent = '--';
        }
    } catch (error) {
        console.error('Error calculating KJ:', error);
        document.getElementById('create-kj-preview').textContent = '--';
    }
};

/**
 * Create new race API call
 */
window.createRace = async function() {
    const name = document.getElementById('race-name').value.trim();
    const raceDate = document.getElementById('race-date').value;
    const distance = parseFloat(document.getElementById('race-distance').value);
    const speed = parseFloat(document.getElementById('race-speed').value);
    
    if (!name || !raceDate || !distance || !speed) {
        showToast('Compila i campi obbligatori', 'warning');
        return;
    }
    
    const data = {
        name: name,
        race_date: raceDate,
        distance_km: distance,
        category: document.getElementById('race-category').value,
        gender: document.getElementById('race-gender').value,
        elevation_m: document.getElementById('race-elevation').value ? parseFloat(document.getElementById('race-elevation').value) : null,
        avg_speed_kmh: speed,
        predicted_duration_minutes: (distance / speed) * 60,
        predicted_kj: null, // Will be calculated when athletes are added
        notes: document.getElementById('race-notes').value || null,
        // Save GPX trace data if available
        route_file: window.gpxTraceData ? JSON.stringify(window.gpxTraceData) : null
    };
    
    try {
        showLoading();
        await api.createRace(data);
        showToast('✅ Gara creata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderRacesPage();
    } catch (error) {
        showToast('Errore nella creazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};