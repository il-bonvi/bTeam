/**
 * Races Module - Frontend
 */

window.renderRacesPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    try {
        showLoading();
        const races = await api.getRaces();
        
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Gestione Gare</h3>
                    <button class="btn btn-primary" onclick="showCreateRaceDialog()">
                        <i class="fas fa-plus"></i> Nuova Gara
                    </button>
                </div>
                <div id="races-table"></div>
            </div>
        `;
        
        // Render races table
        const tableHtml = createTable(
            [
                { key: 'id', label: 'ID' },
                { key: 'name', label: 'Nome Gara' },
                { key: 'race_date', label: 'Data', format: formatDate },
                { key: 'distance_km', label: 'Distanza (km)' },
                { key: 'category', label: 'Categoria' },
                { key: 'elevation_m', label: 'Dislivello (m)', format: v => v ? formatNumber(v, 0) : '-' },
                {
                    key: 'actions',
                    label: 'Azioni',
                    format: (_, row) => `
                        <button class="btn btn-secondary" onclick="viewRaceDetails(${row.id})">
                            <i class="fas fa-eye"></i> Dettagli
                        </button>
                        <button class="btn btn-danger" onclick="deleteRaceConfirm(${row.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    `
                }
            ],
            races
        );
        
        document.getElementById('races-table').innerHTML = tableHtml;
        
    } catch (error) {
        showToast('Errore nel caricamento delle gare', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

window.showCreateRaceDialog = function() {
    const modal = createModal(
        'Nuova Gara',
        `
        <div class="form-group">
            <label class="form-label">Nome Gara</label>
            <input type="text" id="race-name" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Data</label>
            <input type="date" id="race-date" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Distanza (km)</label>
            <input type="number" id="race-distance" class="form-input" step="0.1" required>
        </div>
        <div class="form-group">
            <label class="form-label">Categoria</label>
            <input type="text" id="race-category" class="form-input" placeholder="Es. Elite, U23">
        </div>
        <div class="form-group">
            <label class="form-label">Genere</label>
            <select id="race-gender" class="form-input">
                <option value="">Seleziona</option>
                <option value="Maschile">Maschile</option>
                <option value="Femminile">Femminile</option>
                <option value="Misto">Misto</option>
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Dislivello (m)</label>
            <input type="number" id="race-elevation" class="form-input" step="1">
        </div>
        <div class="form-group">
            <label class="form-label">Velocità Media Prevista (km/h)</label>
            <input type="number" id="race-speed" class="form-input" step="0.1">
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
                label: 'Crea',
                class: 'btn-primary',
                onclick: 'createRace()'
            }
        ]
    );
};

window.createRace = async function() {
    const name = document.getElementById('race-name').value.trim();
    const raceDate = document.getElementById('race-date').value;
    const distance = document.getElementById('race-distance').value;
    
    if (!name || !raceDate || !distance) {
        showToast('Compila i campi obbligatori', 'warning');
        return;
    }
    
    const data = {
        name: name,
        race_date: raceDate,
        distance_km: parseFloat(distance),
        category: document.getElementById('race-category').value || null,
        gender: document.getElementById('race-gender').value || null,
        elevation_m: document.getElementById('race-elevation').value ? parseFloat(document.getElementById('race-elevation').value) : null,
        avg_speed_kmh: document.getElementById('race-speed').value ? parseFloat(document.getElementById('race-speed').value) : null,
        notes: document.getElementById('race-notes').value || null
    };
    
    try {
        showLoading();
        await api.createRace(data);
        showToast('Gara creata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderRacesPage();
    } catch (error) {
        showToast('Errore nella creazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.viewRaceDetails = async function(raceId) {
    try {
        showLoading();
        const [race, athletes] = await Promise.all([
            api.getRace(raceId),
            api.getAthletes()
        ]);
        
        const raceAthletes = race.athletes || [];
        const availableAthletes = athletes.filter(a => 
            !raceAthletes.some(ra => ra.id === a.id)
        );
        
        const modal = createModal(
            `Dettagli Gara: ${race.name}`,
            `
            <div class="form-group">
                <strong>Data:</strong> ${formatDate(race.race_date)}
            </div>
            <div class="form-group">
                <strong>Distanza:</strong> ${race.distance_km} km
            </div>
            <div class="form-group">
                <strong>Categoria:</strong> ${race.category || '-'}
            </div>
            <div class="form-group">
                <strong>Dislivello:</strong> ${race.elevation_m ? race.elevation_m + ' m' : '-'}
            </div>
            <hr>
            <h4>Atleti Partecipanti (${raceAthletes.length})</h4>
            ${raceAthletes.length > 0 ? `
                <ul>
                    ${raceAthletes.map(a => `<li>${a.name}</li>`).join('')}
                </ul>
            ` : '<p>Nessun atleta registrato</p>'}
            
            ${availableAthletes.length > 0 ? `
                <hr>
                <div class="form-group">
                    <label class="form-label">Aggiungi Atleta</label>
                    <select id="add-athlete-select" class="form-input">
                        <option value="">Seleziona atleta</option>
                        ${availableAthletes.map(a => 
                            `<option value="${a.id}">${a.first_name} ${a.last_name}</option>`
                        ).join('')}
                    </select>
                </div>
                <button class="btn btn-primary" onclick="addAthleteToRace(${raceId})">
                    <i class="fas fa-plus"></i> Aggiungi
                </button>
            ` : ''}
            `,
            [
                {
                    label: 'Chiudi',
                    class: 'btn-secondary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                }
            ]
        );
        
    } catch (error) {
        showToast('Errore nel caricamento dei dettagli', 'error');
    } finally {
        hideLoading();
    }
};

window.addAthleteToRace = async function(raceId) {
    const athleteId = document.getElementById('add-athlete-select').value;
    
    if (!athleteId) {
        showToast('Seleziona un atleta', 'warning');
        return;
    }
    
    try {
        showLoading();
        await api.addAthleteToRace(raceId, {
            athlete_id: parseInt(athleteId),
            kj_per_hour_per_kg: 10.0,
            objective: 'C'
        });
        showToast('Atleta aggiunto alla gara', 'success');
        document.querySelector('.modal-overlay').remove();
        viewRaceDetails(raceId);
    } catch (error) {
        showToast('Errore nell\'aggiunta: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.deleteRaceConfirm = function(raceId) {
    confirmDialog(
        'Sei sicuro di voler eliminare questa gara?',
        async () => {
            try {
                showLoading();
                await api.deleteRace(raceId);
                showToast('Gara eliminata con successo', 'success');
                window.renderRacesPage();
            } catch (error) {
                showToast('Errore nell\'eliminazione: ' + error.message, 'error');
            } finally {
                hideLoading();
            }
        }
    );
};
