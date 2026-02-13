/**
 * Races Main Module - Primary race management interface
 * Handles race listing, table display, and basic CRUD operations
 */

let currentRaceId = null;
let currentRaceData = null;

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
                        <i class="fas fa-plus"></i> Nuova Gara
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
                            <i class="fas fa-eye"></i> Dettagli
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteRaceConfirm(${row.id})">
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
    const modal = createModal(
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