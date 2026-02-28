/**
 * Races Riders Module - Rider management for races
 * Handles adding/removing athletes, updating KJ values and objectives
 */

/**
 * Build riders tab content
 */
function buildRidersTab(race, allAthletes) {
    const raceAthletes = (race.athletes || []).sort((a, b) => {
        const lastNameA = (a.last_name || '').toLowerCase();
        const lastNameB = (b.last_name || '').toLowerCase();
        if (lastNameA !== lastNameB) {
            return lastNameA.localeCompare(lastNameB);
        }
        return (a.first_name || '').toLowerCase().localeCompare((b.first_name || '').toLowerCase());
    });
    
    return `
        <div style="padding: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4>🚴 Atleti Partecipanti</h4>
                <button class="btn btn-primary" onclick="showAddRidersDialog()">
                    <i class="bi bi-plus"></i> Aggiungi Atleti
                </button>
            </div>

            <div id="add-riders-panel" style="display: none; margin-bottom: 15px; padding: 12px; border: 1px solid #e5e7eb; border-radius: 6px; background: #fafafa;"></div>
            
            <table id="riders-table" class="data-table" style="width: 100%;">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Squadra</th>
                        <th>Peso (kg)</th>
                        <th>kJ/h/kg</th>
                        <th>KJ Previsti</th>
                        <th>Obiettivo</th>
                        <th>Azioni</th>
                    </tr>
                </thead>
                <tbody>
                    ${raceAthletes.length === 0 ? `
                        <tr><td colspan="7" style="text-align: center; padding: 20px; color: #999;">
                            Nessun atleta registrato. Clicca "Aggiungi Atleti" per iniziare.
                        </td></tr>
                    ` : raceAthletes.map(ra => buildRiderRow(ra)).join('')}
                </tbody>
            </table>
            
            <div style="margin-top: 15px; padding: 10px; background: #f0f0f0; border-radius: 5px;">
                <strong style="color: #60a5fa;">⚡ KJ Totali Stimati:</strong>
                <span id="riders-kj-total">${calculateTotalRidersKJ()}</span>
            </div>
        </div>
    `;
}

/**
 * Build individual rider row
 */
function buildRiderRow(rider) {
    const distance = window.currentRaceData.distance_km;
    const speed = window.currentRaceData.avg_speed_kmh || 25;
    const durationHours = distance / speed;
    
    const weight = rider.weight_kg || 70;
    const kjPerHourPerKg = rider.kj_per_hour_per_kg || 10.0;
    const predictedKj = Math.round(kjPerHourPerKg * weight * durationHours);
    
    const objectiveColors = {
        'A': '#4ade80', // green
        'B': '#60a5fa', // blue  
        'C': '#fbbf24'  // yellow
    };
    
    return `
        <tr>
            <td>${rider.last_name} ${rider.first_name}</td>
            <td>${rider.team_name || '-'}</td>
            <td>${weight}</td>
            <td>
                <input type="number" class="form-input" style="width: 80px;" 
                       value="${kjPerHourPerKg}" step="0.1" min="0.5" max="50"
                       onchange="updateRiderKj(${rider.id}, this.value)">
            </td>
            <td id="rider-kj-${rider.id}">${predictedKj}</td>
            <td>
                <select class="form-input" style="width: 70px; background-color: ${objectiveColors[rider.objective] || '#f3f4f6'};" 
                        onchange="updateRiderObjective(${rider.id}, this.value)">
                    <option value="A" ${rider.objective === 'A' ? 'selected' : ''}>A</option>
                    <option value="B" ${rider.objective === 'B' ? 'selected' : ''}>B</option>
                    <option value="C" ${rider.objective === 'C' ? 'selected' : ''}>C</option>
                </select>
            </td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="removeRiderFromRace(${rider.id})" title="Rimuovi atleta">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `;
}

/**
 * Calculate total KJ for all riders
 */
function calculateTotalRidersKJ() {
    const raceAthletes = window.currentRaceData?.athletes || [];
    if (raceAthletes.length === 0) return '--';
    
    const distance = window.currentRaceData.distance_km;
    const speed = window.currentRaceData.avg_speed_kmh || 25;
    const durationHours = distance / speed;
    
    let totalKj = 0;
    raceAthletes.forEach(ra => {
        const weight = ra.weight_kg || 70;
        const kjPerHourPerKg = ra.kj_per_hour_per_kg || 10.0;
        totalKj += kjPerHourPerKg * weight * durationHours;
    });
    
    return Math.round(totalKj);
}

/**
 * Refresh riders KJ values when race parameters change
 */
window.refreshRidersKJ = function() {
    const raceAthletes = window.currentRaceData?.athletes || [];
    const distance = parseFloat(document.getElementById('detail-distance')?.value) || window.currentRaceData.distance_km;
    const speed = parseFloat(document.getElementById('detail-speed')?.value) || window.currentRaceData.avg_speed_kmh || 25;
    const durationHours = distance / speed;
    
    let totalKj = 0;
    raceAthletes.forEach(ra => {
        const weight = ra.weight_kg || 70;
        const kjPerHourPerKg = ra.kj_per_hour_per_kg || 10.0;
        const predictedKj = Math.round(kjPerHourPerKg * weight * durationHours);
        
        const kjCell = document.getElementById(`rider-kj-${ra.id}`);
        if (kjCell) {
            kjCell.textContent = predictedKj;
        }
        
        totalKj += kjPerHourPerKg * weight * durationHours;
    });
    
    const totalCell = document.getElementById('riders-kj-total');
    if (totalCell) {
        totalCell.textContent = Math.round(totalKj);
    }
};

/**
 * Show dialog to add riders to race
 */
window.showAddRidersDialog = async function() {
    try {
        const allAthletes = await api.getAthletes();
        const raceAthletes = window.currentRaceData?.athletes || [];
        const raceAthleteIds = raceAthletes.map(ra => ra.id);
        
        const availableAthletes = allAthletes.filter(a => !raceAthleteIds.includes(a.id));
        window.availableRaceAthletes = availableAthletes;
        
        if (availableAthletes.length === 0) {
            showToast('Tutti gli atleti sono già stati aggiunti alla gara', 'info');
            return;
        }
        
        const panel = document.getElementById('add-riders-panel');
        if (!panel) {
            showToast('Errore apertura pannello atleti', 'error');
            return;
        }

        // Sort available athletes by last name, then first name
        const sortedAthletes = availableAthletes.sort((a, b) => {
            const lastNameA = (a.last_name || '').toLowerCase();
            const lastNameB = (b.last_name || '').toLowerCase();
            if (lastNameA !== lastNameB) {
                return lastNameA.localeCompare(lastNameB);
            }
            return (a.first_name || '').toLowerCase().localeCompare((b.first_name || '').toLowerCase());
        });

        // Extract unique teams and categories for filter
        const teams = [...new Set(sortedAthletes.map(a => a.team_name).filter(t => t))].sort();
        const categories = [...new Set(sortedAthletes.map(a => a.category).filter(c => c))].sort();
        const genders = [...new Set(sortedAthletes.map(a => a.gender).filter(g => g))].sort();

        // If race has a gender, auto-select it (no "Tutti" option for gender)
        const raceGender = window.currentRaceData?.gender;
        const preselectedGender = (raceGender === 'M' || raceGender === 'F') ? raceGender : '';

        panel.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <strong>Aggiungi Atleti alla Gara</strong>
                <button class="btn btn-secondary btn-sm" onclick="hideAddRidersPanel()">Chiudi</button>
            </div>
            
            <div style="display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 150px;">
                    <label style="display: block; font-size: 12px; font-weight: bold; margin-bottom: 4px;">Genere</label>
                    <select id="filter-gender" class="form-input" onchange="applyAthletesFilter()" style="width: 100%;">
                        ${preselectedGender ? `
                            <option value="${preselectedGender}" selected>${preselectedGender === 'M' ? 'Maschio' : 'Femmina'}</option>
                        ` : `
                            <option value="">Tutti</option>
                            <option value="M">Maschio</option>
                            <option value="F">Femmina</option>
                        `}
                    </select>
                </div>
                <div style="flex: 1; min-width: 150px;">
                    <label style="display: block; font-size: 12px; font-weight: bold; margin-bottom: 4px;">Squadra</label>
                    <select id="filter-team" class="form-input" onchange="applyAthletesFilter()" style="width: 100%;">
                        <option value="">Tutte</option>
                        ${teams.map(t => `<option value="${t}">${t}</option>`).join('')}
                    </select>
                </div>
                <div style="flex: 1; min-width: 150px;">
                    <label style="display: block; font-size: 12px; font-weight: bold; margin-bottom: 4px;">Categoria</label>
                    <select id="filter-category" class="form-input" onchange="applyAthletesFilter()" style="width: 100%;">
                        <option value="">Tutte</option>
                        ${categories.length > 0 ? categories.map(c => `<option value="${c}">${c}</option>`).join('') : '<option value="" disabled>Nessuna categoria disponibile</option>'}
                    </select>
                </div>
            </div>

            <div style="max-height: 300px; overflow-y: auto;">
                <table class="data-table" style="width: 100%;">
                    <thead>
                        <tr>
                            <th style="width: 40px;"><input type="checkbox" id="select-all-riders" onchange="toggleAllRiders()"></th>
                            <th>Nome</th>
                            <th>Squadra</th>
                            <th>Peso</th>
                            <th>kJ/h/kg</th>
                        </tr>
                    </thead>
                    <tbody id="riders-filter-tbody">
                        ${sortedAthletes.map(athlete => `
                            <tr class="rider-row" data-team="${athlete.team_name || ''}" data-category="${athlete.category || ''}" data-gender="${athlete.gender || ''}">
                                <td><input type="checkbox" class="rider-checkbox" value="${athlete.id}"></td>
                                <td>${athlete.last_name} ${athlete.first_name}</td>
                                <td>${athlete.team_name || '-'}</td>
                                <td>${athlete.weight_kg || '-'} kg</td>
                                <td>${athlete.kj_per_hour_per_kg || '10.0'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label class="form-label">Obiettivo predefinito per atleti selezionati</label>
                <select id="default-objective" class="form-input">
                    <option value="A" style="background-color: #d000b8;">A</option>
                    <option value="B" style="background-color: #60fa68;">B</option>
                    <option value="C" selected style="background-color: #249afb;">C</option>
                </select>
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="btn btn-secondary" onclick="hideAddRidersPanel()">Annulla</button>
                <button class="btn btn-primary" onclick="addSelectedRiders()">✓ Aggiungi Selezionati</button>
            </div>
        `;

        panel.style.display = 'block';
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Apply gender filter automatically if race has a gender specified
        if (preselectedGender) {
            setTimeout(() => applyAthletesFilter(), 100);
        }
    } catch (error) {
        showToast('Errore nel caricamento degli atleti', 'error');
    }
};

window.hideAddRidersPanel = function() {
    const panel = document.getElementById('add-riders-panel');
    if (panel) {
        panel.innerHTML = '';
        panel.style.display = 'none';
    }
};

/**
 * Apply filters to athletes table
 */
window.applyAthletesFilter = function() {
    const filterGender = document.getElementById('filter-gender')?.value || '';
    const filterTeam = document.getElementById('filter-team')?.value || '';
    const filterCategory = document.getElementById('filter-category')?.value || '';
    
    const rows = document.querySelectorAll('.rider-row');
    let visibleCount = 0;
    
    rows.forEach(row => {
        const rowGender = row.getAttribute('data-gender');
        const rowTeam = row.getAttribute('data-team');
        const rowCategory = row.getAttribute('data-category');
        
        const matchGender = !filterGender || rowGender === filterGender;
        const matchTeam = !filterTeam || rowTeam === filterTeam;
        const matchCategory = !filterCategory || rowCategory === filterCategory;
        
        const shouldShow = matchGender && matchTeam && matchCategory;
        row.style.display = shouldShow ? '' : 'none';
        
        if (shouldShow) visibleCount++;
    });
    
    // Uncheck "select all" if filters applied
    const selectAll = document.getElementById('select-all-riders');
    if (selectAll) {
        selectAll.checked = false;
    }
};

/**
 * Toggle all rider checkboxes (only visible ones after filters)
 */
window.toggleAllRiders = function() {
    const selectAll = document.getElementById('select-all-riders').checked;
    // Only select checkboxes in visible rows
    document.querySelectorAll('.rider-row:not([style*="display: none"]) .rider-checkbox').forEach(cb => {
        cb.checked = selectAll;
    });
};

/**
 * Add selected riders to race
 */
window.addSelectedRiders = async function() {
    const selectedCheckboxes = document.querySelectorAll('.rider-checkbox:checked');
    const objective = document.getElementById('default-objective').value;
    
    if (selectedCheckboxes.length === 0) {
        showToast('Seleziona almeno un atleta', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        for (const checkbox of selectedCheckboxes) {
            const athleteId = parseInt(checkbox.value);
            const athlete = window.availableRaceAthletes?.find(a => a.id === athleteId);
            // Each athlete uses their personal kJ/h/kg value
            const athleteKj = athlete?.kj_per_hour_per_kg || 10.0;
            await api.addAthleteToRace(currentRaceId, {
                athlete_id: athleteId,
                kj_per_hour_per_kg: athleteKj,
                objective: objective
            });
        }
        
        showToast(`✅ ${selectedCheckboxes.length} atleta/i aggiunto/i alla gara`, 'success');
        hideAddRidersPanel();
        
        // Refresh only the riders table instead of reloading entire dialog
        refreshRidersTable(currentRaceId);
        
    } catch (error) {
        showToast('Errore nell\'aggiunta degli atleti: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

/**
 * Update rider KJ per hour per kg value
 */
window.updateRiderKj = function(athleteId, newKj) {
    const athlete = window.currentRaceData.athletes.find(a => a.id === athleteId);
    if (athlete) {
        athlete.kj_per_hour_per_kg = parseFloat(newKj);
        refreshRidersKJ();
    }
};

/**
 * Update rider objective (A/B/C)
 */
window.updateRiderObjective = async function(athleteId, newObjective) {
    const selectElement = event.target;
    const athlete = window.currentRaceData.athletes.find(a => a.id === athleteId);
    if (athlete) {
        try {
            // Save to backend
            await api.updateAthleteInRace(window.currentRaceId, athleteId, {
                athlete_id: athleteId,
                kj_per_hour_per_kg: athlete.kj_per_hour_per_kg,
                objective: newObjective
            });
            
            // Update local data
            athlete.objective = newObjective;
            
            // Update the select background color
            const objectiveColors = {
                'A': '#4ade80', // green
                'B': '#60a5fa', // blue  
                'C': '#fbbf24'  // yellow
            };
            selectElement.style.backgroundColor = objectiveColors[newObjective] || '#f3f4f6';
        } catch (error) {
            showToast('Errore nel salvataggio dell\'obiettivo: ' + error.message, 'error');
        }
    }
};

/**
 * Refresh riders table content without reloading entire dialog
 */
window.refreshRidersTable = async function(raceId) {
    try {
        // Reload race data from server
        window.currentRaceData = await api.getRace(raceId);
        const raceAthletes = window.currentRaceData.athletes || [];
        const ridersTableBody = document.querySelector('#riders-table tbody');
        
        if (!ridersTableBody) return;
        
        // Update table content
        if (raceAthletes.length === 0) {
            ridersTableBody.innerHTML = `
                <tr><td colspan="7" style="text-align: center; padding: 20px; color: #999;">
                    Nessun atleta registrato. Clicca "Aggiungi Atleti" per iniziare.
                </td></tr>
            `;
        } else {
            ridersTableBody.innerHTML = raceAthletes.map(ra => buildRiderRow(ra)).join('');
        }
        
        // Update KJ totals
        refreshRidersKJ();
    } catch (error) {
        showToast('Errore nel refresh della tabella atleti', 'error');
    }
};

/**
 * Remove rider from race
 */
window.removeRiderFromRace = async function(athleteId) {
    if (!confirm('Rimuovere questo atleta dalla gara?')) return;
    
    try {
        showLoading();
        await api.removeAthleteFromRace(currentRaceId, athleteId);
        showToast('✅ Atleta rimosso dalla gara', 'success');
        
        // Refresh only the riders table instead of reloading entire dialog
        refreshRidersTable(window.currentRaceId);
        
    } catch (error) {
        showToast('Errore nella rimozione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};