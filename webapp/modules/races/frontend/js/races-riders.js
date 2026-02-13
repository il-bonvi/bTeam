/**
 * Races Riders Module - Rider management for races
 * Handles adding/removing athletes, updating KJ values and objectives
 */

/**
 * Build riders tab content
 */
function buildRidersTab(race, allAthletes) {
    const raceAthletes = race.athletes || [];
    
    return `
        <div style="padding: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4>🚴 Atleti Partecipanti</h4>
                <button class="btn btn-primary" onclick="showAddRidersDialog()">
                    <i class="fas fa-plus"></i> Aggiungi Atleti
                </button>
            </div>
            
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
    const distance = currentRaceData.distance_km;
    const speed = currentRaceData.avg_speed_kmh || 25;
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
            <td>${rider.first_name} ${rider.last_name}</td>
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
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `;
}

/**
 * Calculate total KJ for all riders
 */
function calculateTotalRidersKJ() {
    const raceAthletes = currentRaceData?.athletes || [];
    if (raceAthletes.length === 0) return '--';
    
    const distance = currentRaceData.distance_km;
    const speed = currentRaceData.avg_speed_kmh || 25;
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
    const raceAthletes = currentRaceData?.athletes || [];
    const distance = parseFloat(document.getElementById('detail-distance')?.value) || currentRaceData.distance_km;
    const speed = parseFloat(document.getElementById('detail-speed')?.value) || currentRaceData.avg_speed_kmh || 25;
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
        const raceAthletes = currentRaceData?.athletes || [];
        const raceAthleteIds = raceAthletes.map(ra => ra.id);
        
        const availableAthletes = allAthletes.filter(a => !raceAthleteIds.includes(a.id));
        
        if (availableAthletes.length === 0) {
            showToast('Tutti gli atleti sono già stati aggiunti alla gara', 'info');
            return;
        }
        
        createModal(
            'Aggiungi Atleti alla Gara',
            `
            <div style="max-height: 400px; overflow-y: auto;">
                <table class="data-table" style="width: 100%;">
                    <thead>
                        <tr>
                            <th style="width: 40px;"><input type="checkbox" id="select-all-riders" onchange="toggleAllRiders()"></th>
                            <th>Nome</th>
                            <th>Squadra</th>
                            <th>Peso</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${availableAthletes.map(athlete => `
                            <tr>
                                <td><input type="checkbox" class="rider-checkbox" value="${athlete.id}"></td>
                                <td>${athlete.first_name} ${athlete.last_name}</td>
                                <td>${athlete.team_name || '-'}</td>
                                <td>${athlete.weight_kg || '-'} kg</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label class="form-label">Obiettivo predefinito per atleti selezionati</label>
                <select id="default-objective" class="form-input">
                    <option value="A" style="background-color: #4ade80;">A - Priorità Alta (Podio)</option>
                    <option value="B" style="background-color: #60a5fa;">B - Priorità Media (Top 10)</option>
                    <option value="C" selected style="background-color: #fbbf24;">C - Priorità Bassa (Finire)</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">kJ/h/kg predefinito per atleti selezionati</label>
                <input type="number" id="default-kj" class="form-input" value="10.0" step="0.1" min="0.5" max="50">
            </div>
            `,
            [
                {
                    label: 'Annulla',
                    class: 'btn-secondary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                },
                {
                    label: '✓ Aggiungi Selezionati',
                    class: 'btn-primary',
                    onclick: 'addSelectedRiders()'
                }
            ]
        );
    } catch (error) {
        showToast('Errore nel caricamento degli atleti', 'error');
    }
};

/**
 * Toggle all rider checkboxes
 */
window.toggleAllRiders = function() {
    const selectAll = document.getElementById('select-all-riders').checked;
    document.querySelectorAll('.rider-checkbox').forEach(cb => {
        cb.checked = selectAll;
    });
};

/**
 * Add selected riders to race
 */
window.addSelectedRiders = async function() {
    const selectedCheckboxes = document.querySelectorAll('.rider-checkbox:checked');
    const objective = document.getElementById('default-objective').value;
    const kjPerHourPerKg = parseFloat(document.getElementById('default-kj').value) || 10.0;
    
    if (selectedCheckboxes.length === 0) {
        showToast('Seleziona almeno un atleta', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        for (const checkbox of selectedCheckboxes) {
            const athleteId = parseInt(checkbox.value);
            await api.addAthleteToRace(currentRaceId, {
                athlete_id: athleteId,
                kj_per_hour_per_kg: kjPerHourPerKg,
                objective: objective
            });
        }
        
        showToast(`✅ ${selectedCheckboxes.length} atleta/i aggiunto/i alla gara`, 'success');
        document.querySelector('.modal-overlay').remove();
        
        // Refresh race details
        viewRaceDetails(currentRaceId);
        
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
    const athlete = currentRaceData.athletes.find(a => a.id === athleteId);
    if (athlete) {
        athlete.kj_per_hour_per_kg = parseFloat(newKj);
        refreshRidersKJ();
    }
};

/**
 * Update rider objective (A/B/C)
 */
window.updateRiderObjective = function(athleteId, newObjective) {
    const athlete = currentRaceData.athletes.find(a => a.id === athleteId);
    if (athlete) {
        athlete.objective = newObjective;
        
        // Update the select background color
        const selectElement = event.target;
        const objectiveColors = {
            'A': '#4ade80', // green
            'B': '#60a5fa', // blue  
            'C': '#fbbf24'  // yellow
        };
        selectElement.style.backgroundColor = objectiveColors[newObjective] || '#f3f4f6';
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
        
        // Update local data
        currentRaceData.athletes = currentRaceData.athletes.filter(a => a.id !== athleteId);
        
        // Refresh race details
        viewRaceDetails(currentRaceId);
        
    } catch (error) {
        showToast('Errore nella rimozione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};