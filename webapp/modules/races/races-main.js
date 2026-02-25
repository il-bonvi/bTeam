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
 * Main function to render the races page
 * Shows races table with actions
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
                        <i class="bi bi-plus"></i> Nuova Gara
                    </button>
                </div>
                <div id="races-table"></div>
            </div>
        `;
        
        const tableHtml = createTable(
            [
                { key: 'id', label: 'ID' },
                { key: 'name', label: 'Nome Gara' },
                { key: 'race_date', label: 'Data', format: formatDate },
                { key: 'distance_km', label: 'Distanza (km)', format: v => formatNumber(v, 1) },
                { key: 'category', label: 'Categoria' },
                { key: 'gender', label: 'Genere' },
                { key: 'elevation_m', label: 'Dislivello (m)', format: v => v ? formatNumber(v, 0) : '-' },
                { key: 'predicted_duration_minutes', label: 'Durata', format: v => v ? formatDuration(v) : '-' },
                { key: 'predicted_kj', label: 'KJ', format: v => v ? formatNumber(v, 0) : '-' },
                {
                    key: 'actions',
                    label: 'Azioni',
                    format: (_, row) => `
                        <button class="btn btn-secondary btn-sm" onclick="viewRaceDetails(${row.id})" style="margin-right: 5px;">
                            <i class="bi bi-eye"></i> Dettagli
                        </button>
                        <button class="btn btn-info btn-sm" onclick="pushRaceToIntervals(${row.id})" style="margin-right: 5px;">
                            <i class="bi bi-cloud-arrow-up"></i> Intervals
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteRaceConfirm(${row.id})">
                            <i class="bi bi-trash"></i>
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
    try {
        showLoading();
        const result = await api.pushRace(raceId);
        
        if (!result.success) {
            showToast('⚠️ ' + result.message, 'warning');
        } else {
            const msg = result.athletes_processed > 0 
                ? `✅ Gara pushata a ${result.athletes_processed} atleta/i` 
                : `⚠️ ${result.message}`;
            showToast(msg, 'success');
        }
        
        // Refresh races list if needed
        await loadRaces();
        
    } catch (error) {
        let errorMsg = 'Errore sconosciuto';
        if (error instanceof Error) {
            errorMsg = error.message;
        } else if (typeof error === 'string') {
            errorMsg = error;
        } else if (error && typeof error === 'object') {
            errorMsg = JSON.stringify(error);
        }
        showToast('❌ Errore: ' + errorMsg, 'error');
        console.error('Full error:', error);
    } finally {
        hideLoading();
    }
};