/**
 * Teams Module - Frontend
 */

window.renderTeamsPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    try {
        showLoading();
        const teams = await api.getTeams();
        
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Gestione Squadre</h3>
                    <button class="btn btn-primary" onclick="showCreateTeamDialog()">
                        <i class="fas fa-plus"></i> Nuova Squadra
                    </button>
                </div>
                <div id="teams-table"></div>
            </div>
        `;
        
        // Render teams table
        const tableHtml = createTable(
            [
                { key: 'id', label: 'ID' },
                { key: 'name', label: 'Nome Squadra' },
                { key: 'created_at', label: 'Data Creazione', format: formatDateTime },
                {
                    key: 'actions',
                    label: 'Azioni',
                    format: (_, row) => `
                        <button class="btn btn-secondary" onclick="editTeam(${row.id})">
                            <i class="fas fa-edit"></i> Modifica
                        </button>
                        <button class="btn btn-danger" onclick="deleteTeamConfirm(${row.id})">
                            <i class="fas fa-trash"></i> Elimina
                        </button>
                    `
                }
            ],
            teams
        );
        
        document.getElementById('teams-table').innerHTML = tableHtml;
        
    } catch (error) {
        showToast('Errore nel caricamento delle squadre', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

window.showCreateTeamDialog = function() {
    createModal(
        'Nuova Squadra',
        `
        <div class="form-group">
            <label class="form-label">Nome Squadra</label>
            <input type="text" id="team-name" class="form-input" placeholder="Es. Team Pro" required>
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
                onclick: 'createTeam()'
            }
        ]
    );
};

window.createTeam = async function() {
    const name = document.getElementById('team-name').value.trim();
    
    if (!name) {
        showToast('Inserisci un nome per la squadra', 'warning');
        return;
    }
    
    try {
        showLoading();
        await api.createTeam({ name });
        showToast('Squadra creata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderTeamsPage();
    } catch (error) {
        showToast('Errore nella creazione della squadra: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.editTeam = async function(teamId) {
    try {
        const team = await api.getTeam(teamId);
        
        createModal(
            'Modifica Squadra',
            `
            <div class="form-group">
                <label class="form-label">Nome Squadra</label>
                <input type="text" id="team-name-edit" class="form-input" value="${team.name}" required>
            </div>
            `,
            [
                {
                    label: 'Annulla',
                    class: 'btn-secondary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                },
                {
                    label: 'Salva',
                    class: 'btn-primary',
                    onclick: `updateTeam(${teamId})`
                }
            ]
        );
    } catch (error) {
        showToast('Errore nel caricamento dei dati', 'error');
    }
};

window.updateTeam = async function(teamId) {
    const name = document.getElementById('team-name-edit').value.trim();
    
    if (!name) {
        showToast('Inserisci un nome per la squadra', 'warning');
        return;
    }
    
    try {
        showLoading();
        await api.updateTeam(teamId, { name });
        showToast('Squadra aggiornata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderTeamsPage();
    } catch (error) {
        showToast('Errore nell\'aggiornamento: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.deleteTeamConfirm = function(teamId) {
    confirmDialog(
        'Sei sicuro di voler eliminare questa squadra? Questa azione non può essere annullata.',
        async () => {
            try {
                showLoading();
                await api.deleteTeam(teamId);
                showToast('Squadra eliminata con successo', 'success');
                window.renderTeamsPage();
            } catch (error) {
                showToast('Errore nell\'eliminazione: ' + error.message, 'error');
            } finally {
                hideLoading();
            }
        }
    );
};
