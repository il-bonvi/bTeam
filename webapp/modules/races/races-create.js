/**
 * Races Create Module - Race creation dialog and form
 * Handles new race creation with predictions and category management
 */

// Store bonvi route link when loaded
window.bonviRouteLink = null;
// Store stage links for multi-stage races
window.bonviStageLinks = [];
// Store per-stage data (distance, elevation, date) fetched from bonvi
window.bonviStagesData = [];

/**
 * Show create race dialog with form
 */
window.showCreateRaceDialog = function() {
    const today = new Date().toISOString().split('T')[0];

    // Reset bonvi global state for a fresh dialog
    window.bonviRouteLink = null;
    window.bonviStageLinks = [];
    window.bonviStagesData = [];
    // stages-bonvi-summary is inside the modal, re-created fresh each time — no reset needed

    createModal(
        '✨ Crea Nuova Gara',
        `
        <!-- Bonvi Database Link Section - FIRST POSITION -->
        <div class="form-group" style="border: 2px dashed #3b82f6; padding: 15px; border-radius: 8px; margin: 0 0 15px 0;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <i class="bi bi-link-45deg" style="color: #3b82f6; font-size: 18px;"></i>
                <label class="form-label" style="margin: 0;">🔗 Carica da Bonvi Race Database</label>
            </div>
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <input type="url" id="bonvi-link" class="form-input" placeholder="Es: https://il-bonvi.github.io/bonvi-race-database/gare/nonantola-2026-DJ/" style="flex: 1;">
                <button type="button" onclick="loadFromBonviDatabase()" class="btn btn-primary" style="width: auto; padding: 10px 20px;">
                    📥 Carica
                </button>
                <a id="bonvi-view-link" href="#" target="_blank" style="display: none; padding: 10px 20px; background: #e0e7ff; color: #3b82f6; border-radius: 5px; text-decoration: none; align-self: center;">
                    🔗 Apri
                </a>
            </div>
            <div id="bonvi-loading" style="display: none; margin-top: 10px; padding: 10px; background: #e0f2fe; border-radius: 5px; color: #0369a1;">
                ⏳ Caricamento in corso...
            </div>
            <div id="bonvi-success" style="display: none; margin-top: 10px; padding: 10px; background: #dcfce7; border-radius: 5px; color: #166534;">
                ✅ Dati caricati con successo
            </div>
            <div id="bonvi-error" style="display: none; margin-top: 10px; padding: 10px; background: #fee2e2; border-radius: 5px; color: #b91c1c;"></div>
        </div>

        <!-- Stage details section – populated automatically after bonvi load -->
        <div id="stages-bonvi-summary" style="display:none; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; margin-bottom: 15px; background: #f0fdf4;">
            <div style="font-weight: 600; color: #166534; margin-bottom: 8px;">📋 Tappe caricate</div>
            <table id="stages-bonvi-table" style="width:100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="background:#dcfce7; text-align:left;">
                        <th style="padding:5px 8px;">Tappa</th>
                        <th style="padding:5px 8px;">Data</th>
                        <th style="padding:5px 8px;">Distanza</th>
                        <th style="padding:5px 8px;">Dislivello</th>
                        <th style="padding:5px 8px;">Vel. km/h</th>
                        <th style="padding:5px 8px;">Link</th>
                    </tr>
                </thead>
                <tbody id="stages-bonvi-tbody"></tbody>
            </table>
        </div>

        <div class="form-group">
            <label class="form-label">Nome Gara *</label>
            <input type="text" id="race-name" class="form-input" required>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div class="form-group">
                <label class="form-label">Data Inizio *</label>
                <input type="date" id="race-date-start" class="form-input" value="${today}" required onchange="syncCreateRaceDateEnd()">
            </div>
            <div class="form-group">
                <label class="form-label">Data Fine *</label>
                <input type="date" id="race-date-end" class="form-input" value="${today}" required onchange="validateCreateRaceDateEnd()">
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">N. Tappe *</label>
            <input type="number" id="race-num-stages" class="form-input" min="1" value="1" required>
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
    const genderSelect = document.getElementById('race-gender');
    const gender = genderSelect?.value || 'Femminile';
    const categorySelect = document.getElementById('race-category');
    
    const categories = {
        'Femminile': ['Allieve', 'Junior', 'Junior 1NC', 'Junior 2NC', 'Junior (OPEN)', 'OPEN'],
        'Maschile': ['U23']
    };
    
    const categoryList = categories[gender] || [...categories.Femminile, ...categories.Maschile];
    categorySelect.innerHTML = categoryList.map(cat => 
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
    const raceDateStart = document.getElementById('race-date-start').value;
    const raceDateEnd = document.getElementById('race-date-end').value;
    const distance = parseFloat(document.getElementById('race-distance').value);
    const speed = parseFloat(document.getElementById('race-speed').value);
    
    if (!name || !raceDateStart || !raceDateEnd || !distance || !speed) {
        showToast('Compila i campi obbligatori', 'warning');
        return;
    }
    
    if (new Date(raceDateEnd) < new Date(raceDateStart)) {
        showToast('La data fine deve essere successiva o uguale alla data inizio', 'warning');
        return;
    }
    
    const data = {
        name: name,
        race_date_start: raceDateStart,
        race_date_end: raceDateEnd,
        num_stages: parseInt(document.getElementById('race-num-stages').value) || 1,
        distance_km: distance,
        category: document.getElementById('race-category').value,
        gender: document.getElementById('race-gender').value,
        elevation_m: document.getElementById('race-elevation').value ? parseFloat(document.getElementById('race-elevation').value) : null,
        avg_speed_kmh: speed,
        predicted_duration_minutes: (distance / speed) * 60,
        predicted_kj: null, // Will be calculated when athletes are added
        notes: document.getElementById('race-notes').value || null,
        // Save bonvi route link if available
        route_link: window.bonviRouteLink || null,
        // Save auto-generated stage links
        stage_links: window.bonviStageLinks || [],
        // Per-stage details fetched from bonvi (distance, elevation, date)
        stages_data: window.bonviStagesData.length > 0 ? window.bonviStagesData : null
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

/**
 * Load race data from Bonvi Race Database
 */
window.loadFromBonviDatabase = async function() {
    const link = document.getElementById('bonvi-link').value.trim();
    
    if (!link) {
        showToast('Inserisci il link della gara', 'warning');
        return;
    }
    
    const loadingEl = document.getElementById('bonvi-loading');
    const successEl = document.getElementById('bonvi-success');
    const errorEl = document.getElementById('bonvi-error');
    const viewLink = document.getElementById('bonvi-view-link');
    
    // Reset feedback elements
    loadingEl.style.display = 'block';
    successEl.style.display = 'none';
    errorEl.style.display = 'none';
    viewLink.style.display = 'inline-block';
    viewLink.href = link;
    
    try {
        const response = await fetch('/api/races/load-from-bonvi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ link: link })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Errore nel caricamento dei dati');
        }
        
        const data = await response.json();

        // Populate form fields based on link_type
        const linkType = data.link_type || 'single_day';

        if (linkType === 'single_stage') {
            // User pasted a single-stage link in the create dialog – inform them
            loadingEl.style.display = 'none';
            errorEl.style.display = 'block';
            errorEl.textContent = '⚠️ Hai incollato il link di una singola tappa. Usa il link della corsa a tappe completa (senza -S1-, -S2- ecc.) per creare la gara, poi aggiungi i link delle tappe nella scheda Tappe.';
            return;
        }

        if (data.name) {
            document.getElementById('race-name').value = data.name;
        }

        if (linkType === 'stage_race') {
            // Stage race: populate all fields
            if (data.race_date_start) {
                document.getElementById('race-date-start').value = data.race_date_start;
                document.getElementById('race-date-end').value = data.race_date_end || data.race_date_start;
            }
            if (data.num_stages) {
                document.getElementById('race-num-stages').value = data.num_stages;
            }
            if (data.distance_km) {
                document.getElementById('race-distance').value = data.distance_km;
            }
            if (data.elevation_m) {
                document.getElementById('race-elevation').value = data.elevation_m;
            }
            if (data.route_link) {
                window.bonviRouteLink = data.route_link;
            }
            if (data.stage_links && Array.isArray(data.stage_links)) {
                window.bonviStageLinks = data.stage_links;
            }
            if (data.stages_data && Array.isArray(data.stages_data)) {
                window.bonviStagesData = data.stages_data;
            }
            updateCreateRacePredictions();

            // Populate stages table in dialog
            const stagesSummaryEl = document.getElementById('stages-bonvi-summary');
            const stagesTbody = document.getElementById('stages-bonvi-tbody');
            if (stagesSummaryEl && stagesTbody && data.stages_data && data.stages_data.length > 0) {
                stagesTbody.innerHTML = data.stages_data.map((s, idx) => {
                    const dist = s.distance_km ? `${s.distance_km} km` : '--';
                    const elev = s.elevation_m ? `+${s.elevation_m} m` : '--';
                    const dt = s.stage_date || '--';
                    const linkHtml = s.route_link
                        ? `<a href="${s.route_link}" target="_blank" style="color:#2563eb; font-size:12px;">🔗 Apri</a>`
                        : '--';
                    const errHtml = s.fetch_error
                        ? `<span style="color:#b91c1c;font-size:11px;"> ⚠️ ${s.fetch_error}</span>`
                        : '';
                    const speedVal = s.avg_speed_kmh || '';
                    return `<tr style="border-top:1px solid #bbf7d0;">
                        <td style="padding:5px 8px; font-weight:600;">T${s.stage_number}</td>
                        <td style="padding:5px 8px;">${dt}</td>
                        <td style="padding:5px 8px;">${dist}</td>
                        <td style="padding:5px 8px;">${elev}${errHtml}</td>
                        <td style="padding:5px 8px;">
                            <input type="number" step="0.1" min="0" placeholder="km/h"
                                value="${speedVal}"
                                style="width:65px; padding:2px 4px; border:1px solid #bbf7d0; border-radius:4px; font-size:12px;"
                                oninput="window.bonviStagesData[${idx}].avg_speed_kmh = this.value ? parseFloat(this.value) : null">
                        </td>
                        <td style="padding:5px 8px;">${linkHtml}</td>
                    </tr>`;
                }).join('');
                stagesSummaryEl.style.display = 'block';
            }

            // Build per-stage summary
            let stagesSummary = '';
            if (data.stages_data && data.stages_data.length > 0) {
                stagesSummary = '<br><small style="color:#166534;">'
                    + data.stages_data.map(s => {
                        const dist = s.distance_km ? `${s.distance_km} km` : '--';
                        const elev = s.elevation_m ? `+${s.elevation_m} m` : '--';
                        const dt = s.stage_date ? ` (${s.stage_date})` : '';
                        return `T${s.stage_number}: ${dist}, ${elev}${dt}`;
                    }).join(' &nbsp;|&nbsp; ')
                    + '</small>';
            }

            loadingEl.style.display = 'none';
            successEl.style.display = 'block';
            const dateRange = data.race_date_start
                ? ` · ${data.race_date_start}` + (data.race_date_end && data.race_date_end !== data.race_date_start ? ` → ${data.race_date_end}` : '')
                : '';
            const totDist = data.distance_km ? ` · ${data.distance_km} km` : '';
            const totElev = data.elevation_m ? ` · +${data.elevation_m} m` : '';
            successEl.innerHTML = `✅ Corsa a tappe caricata: <strong>${data.name || '--'}</strong>${dateRange}${totDist}${totElev}${stagesSummary}`;
            setTimeout(() => { successEl.style.display = 'none'; }, 10000);
            return;
        }

        // --- single_day ---
        if (data.distance_km) {
            document.getElementById('race-distance').value = data.distance_km;
        }
        if (data.elevation_m) {
            document.getElementById('race-elevation').value = data.elevation_m;
        }
        if (data.race_date_start) {
            document.getElementById('race-date-start').value = data.race_date_start;
            document.getElementById('race-date-end').value = data.race_date_start;
        }
        if (data.avg_speed_kmh) {
            document.getElementById('race-speed').value = data.avg_speed_kmh;
        }
        if (data.route_link) {
            // Save the route link to be used when creating the race
            window.bonviRouteLink = data.route_link;
        }
        
        // Update predictions
        updateCreateRacePredictions();
        
        // Show success message
        loadingEl.style.display = 'none';
        successEl.style.display = 'block';
        const nameText = data.name ? data.name : '--';
        const distText = data.distance_km ? `${data.distance_km} km` : '--';
        const elevText = data.elevation_m ? `+${data.elevation_m} m` : '--';
        const dateText = data.race_date_start ? data.race_date_start : '--';
        successEl.innerHTML = `✅ Gara caricata: <strong>${nameText}</strong><br>${distText}, ${elevText}, ${dateText}<br><small style="color: #666;">Velocità media: inserisci manualmente da bonvi-race-database</small>`;
        
        // Hide success after 5 seconds
        setTimeout(() => {
            successEl.style.display = 'none';
        }, 5000);
        
    } catch (error) {
        loadingEl.style.display = 'none';
        errorEl.style.display = 'block';
        errorEl.textContent = '❌ ' + error.message;
        showToast('Errore: ' + error.message, 'error');
    }
};

/**
 * Sync end date when start date changes - only if end date becomes invalid
 */
window.syncCreateRaceDateEnd = function() {
    const startDate = document.getElementById('race-date-start').value;
    const endDate = document.getElementById('race-date-end').value;
    
    // Only sync if end date is before start date
    if (new Date(endDate) < new Date(startDate)) {
        document.getElementById('race-date-end').value = startDate;
    }
};

/**
 * Validate that end date is not before start date
 */
window.validateCreateRaceDateEnd = function() {
    const startDate = document.getElementById('race-date-start').value;
    const endDate = document.getElementById('race-date-end').value;
    
    if (new Date(endDate) < new Date(startDate)) {
        document.getElementById('race-date-end').value = startDate;
        showToast('La data fine non può essere prima della data inizio', 'warning');
    }
};