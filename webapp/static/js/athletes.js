/**
 * Athletes Module - Frontend
 * Multi-athlete dashboard with individual athlete detail views
 */

// Global state
window.currentAthleteView = null; // null = dashboard, number = athlete ID

window.renderAthletesPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    console.log('[ATHLETES] renderAthletesPage started. currentAthleteView:', window.currentAthleteView);
    
    try {
        showLoading();
        const [athletes, teams] = await Promise.all([
            api.getAthletes(),
            api.getTeams()
        ]);
        
        console.log('[ATHLETES] Loaded', athletes.length, 'athletes');
        
        // Store globally
        window.availableTeams = teams;
        window.allAthletes = athletes;
        
        // Render based on current view
        if (window.currentAthleteView === null) {
            console.log('[ATHLETES] Rendering dashboard view');
            renderAthletesDashboard(athletes, contentArea);
        } else {
            console.log('[ATHLETES] Rendering detail view for athlete', window.currentAthleteView);
            renderAthleteDetail(window.currentAthleteView, athletes, contentArea);
        }
        
    } catch (error) {
        console.error('[ATHLETES] Error:', error);
        showToast('Errore nel caricamento degli atleti', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

function renderAthletesDashboard(athletes, contentArea) {
    // Create stats summary
    const totalAthletes = athletes.length;
    const maleCount = athletes.filter(a => a.gender === 'Maschile').length;
    const femaleCount = athletes.filter(a => a.gender === 'Femminile').length;
    const avgFtp = athletes.filter(a => a.cp).reduce((sum, a) => sum + a.cp, 0) / athletes.filter(a => a.cp).length || 0;
    
    contentArea.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 Dashboard Atleti</h3>
                <button class="btn btn-primary" onclick="showCreateAthleteDialog()">
                    <i class="bi bi-plus"></i> Nuovo Atleta
                </button>
            </div>
            <div class="card-body">
                <!-- Summary Stats -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                    <div class="stat-card">
                        <div class="stat-label">Totale Atleti</div>
                        <div class="stat-value">${totalAthletes}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">👨 Maschile</div>
                        <div class="stat-value">${maleCount}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">👩 Femminile</div>
                        <div class="stat-value">${femaleCount}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">FTP Medio</div>
                        <div class="stat-value">${avgFtp > 0 ? Math.round(avgFtp) + 'W' : '-'}</div>
                    </div>
                </div>
                
                <!-- Athletes Grid -->
                <h4 style="margin-bottom: 1rem;">Atleti</h4>
                <div id="athletes-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">
                    ${athletes.map(athlete => createAthleteCard(athlete)).join('')}
                </div>
            </div>
        </div>
    `;
}

function createAthleteCard(athlete) {
    const initials = `${athlete.first_name[0] || ''}${athlete.last_name[0] || ''}`;
    const genderIcon = athlete.gender === 'Maschile' ? '👨' : athlete.gender === 'Femminile' ? '👩' : '🧑';
    
    return `
        <div class="athlete-card" onclick="showAthleteDetail(${athlete.id})" style="cursor: pointer;">
            <div class="athlete-card-header">
                <div class="athlete-avatar">${initials}</div>
                <div class="athlete-info">
                    <div class="athlete-name">${athlete.first_name} ${athlete.last_name}</div>
                    <div class="athlete-team">${genderIcon} ${athlete.team_name || 'Nessuna squadra'}</div>
                </div>
            </div>
            <div class="athlete-card-body">
                <div class="athlete-stat-row">
                    <span class="athlete-stat-label">FTP:</span>
                    <span class="athlete-stat-value">${athlete.cp ? Math.round(athlete.cp) + 'W' : '-'}</span>
                </div>
                <div class="athlete-stat-row">
                    <span class="athlete-stat-label">W':</span>
                    <span class="athlete-stat-value">${athlete.w_prime ? Math.round(athlete.w_prime) + 'J' : '-'}</span>
                </div>
                <div class="athlete-stat-row">
                    <span class="athlete-stat-label">Peso:</span>
                    <span class="athlete-stat-value">${athlete.weight_kg ? athlete.weight_kg + 'kg' : '-'}</span>
                </div>
                <div class="athlete-stat-row">
                    <span class="athlete-stat-label">W/kg:</span>
                    <span class="athlete-stat-value">${athlete.cp && athlete.weight_kg ? (athlete.cp / athlete.weight_kg).toFixed(1) : '-'}</span>
                </div>
            </div>
            <div class="athlete-card-footer">
                <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); editAthlete(${athlete.id})" title="Modifica">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-info btn-sm" onclick="event.stopPropagation(); syncAthleteMetrics(${athlete.id})" title="Metriche">
                    <i class="bi bi-arrow-repeat"></i>
                </button>
                <button class="btn btn-success btn-sm" onclick="event.stopPropagation(); syncAthleteFullSync(${athlete.id}, '${athlete.first_name} ${athlete.last_name}')" title="Attività + Wellness">
                    <i class="bi bi-download"></i>
                </button>
                <button class="btn btn-danger btn-sm" onclick="event.stopPropagation(); deleteAthleteConfirm(${athlete.id})" title="Elimina">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `;
}

window.showAthleteDetail = async function(athleteId) {
    window.currentAthleteView = athleteId;
    await renderAthletesPage();
};

window.backToAthletesDashboard = function() {
    window.currentAthleteView = null;
    renderAthletesPage();
};

async function renderAthleteDetail(athleteId, athletes, contentArea) {
    const athlete = athletes.find(a => a.id === athleteId);
    if (!athlete) {
        showToast('Atleta non trovato', 'error');
        window.currentAthleteView = null;
        return renderAthletesPage();
    }
    
    // Load athlete activities
    try {
        const activities = await api.getActivities({ athlete_id: athleteId, limit: 50 });
        
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <button class="btn btn-secondary" onclick="backToAthletesDashboard()">
                            <i class="bi bi-arrow-left"></i> Dashboard
                        </button>
                        <h3 class="card-title">${athlete.first_name} ${athlete.last_name}</h3>
                    </div>
                    <button class="btn btn-primary" onclick="editAthlete(${athlete.id})">
                        <i class="bi bi-pencil"></i> Modifica
                    </button>
                </div>
                <div class="card-body">
                    <!-- Athlete Info Section -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 2rem; padding: 1rem; background: #f5f5f5; border-radius: 8px;">
                        <div>
                            <strong>Squadra:</strong> ${athlete.team_name || '-'}
                        </div>
                        <div>
                            <strong>Genere:</strong> ${athlete.gender || '-'}
                        </div>
                        <div>
                            <strong>Peso:</strong> ${athlete.weight_kg ? athlete.weight_kg + ' kg' : '-'}
                        </div>
                        <div>
                            <strong>Altezza:</strong> ${athlete.height_cm ? athlete.height_cm + ' cm' : '-'}
                        </div>
                        <div>
                            <strong>FTP/CP:</strong> ${athlete.cp ? Math.round(athlete.cp) + ' W' : '-'}
                        </div>
                        <div>
                            <strong>W':</strong> ${athlete.w_prime ? Math.round(athlete.w_prime) + ' J' : '-'}
                        </div>
                        <div>
                            <strong>W/kg:</strong> ${athlete.cp && athlete.weight_kg ? (athlete.cp / athlete.weight_kg).toFixed(2) : '-'}
                        </div>
                        <div>
                            <strong>Data Nascita:</strong> ${athlete.birth_date || '-'}
                        </div>
                    </div>
                    
                    <!-- Tabs -->
                    <div class="tabs">
                        <button class="tab-button active" onclick="switchAthleteTab('activities')">
                            Attività (${activities.length})
                        </button>
                        <button class="tab-button" onclick="switchAthleteTab('stats')">
                            Statistiche
                        </button>
                        <button class="tab-button" onclick="switchAthleteTab('sync')">
                            Sincronizzazione
                        </button>
                    </div>
                    
                    <!-- Tab Content -->
                    <div id="athlete-tab-content">
                        ${renderActivitiesTab(activities)}
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        showToast('Errore caricamento attività', 'error');
        console.error(error);
    }
}

function renderActivitiesTab(activities) {
    if (activities.length === 0) {
        return '<p style="text-align: center; padding: 2rem; color: #666;">Nessuna attività registrata</p>';
    }
    
    let html = '<div class="table-container"><table><thead><tr>';
    html += '<th>Data</th><th>Titolo</th><th>Tipo</th><th>Distanza</th><th>Durata</th><th>TSS</th><th>Potenza</th><th>Fonte</th>';
    html += '</tr></thead><tbody>';
    
    activities.forEach(activity => {
        const date = formatDate(activity.activity_date);
        const distance = activity.distance_km ? formatNumber(activity.distance_km, 1) + ' km' : '-';
        const duration = formatDuration(activity.duration_minutes);
        const tss = activity.tss ? formatNumber(activity.tss, 0) : '-';
        const watts = activity.avg_watts ? formatNumber(activity.avg_watts, 0) + 'W' : '-';
        
        html += `
            <tr>
                <td>${date}</td>
                <td>${activity.title}</td>
                <td>${activity.activity_type || '-'}</td>
                <td>${distance}</td>
                <td>${duration}</td>
                <td>${tss}</td>
                <td>${watts}</td>
                <td><span class="badge">${activity.source || 'manual'}</span></td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    return html;
}

window.switchAthleteTab = function(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    const athleteId = window.currentAthleteView;
    const athlete = window.allAthletes.find(a => a.id === athleteId);
    
    const tabContent = document.getElementById('athlete-tab-content');
    
    if (tabName === 'activities') {
        // Already loaded, just re-fetch if needed
        api.getActivities({ athlete_id: athleteId, limit: 50 }).then(activities => {
            tabContent.innerHTML = renderActivitiesTab(activities);
        });
    } else if (tabName === 'stats') {
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <h4>Statistiche Atleta</h4>
                <p style="color: #666;">Statistiche dettagliate in arrivo...</p>
            </div>
        `;
    } else if (tabName === 'sync') {
        tabContent.innerHTML = `
            <div style="padding: 2rem;">
                <h4>Sincronizzazione Intervals.icu</h4>
                
                <!-- Metriche -->
                <div style="margin-top: 1.5rem; padding: 1rem; background: #f0f8ff; border-radius: 8px;">
                    <h5 style="margin-bottom: 0.75rem; color: #3b82f6;">📊 Metriche</h5>
                    <button class="btn btn-primary" onclick="syncAthleteMetrics(${athleteId})">
                        <i class="bi bi-arrow-repeat"></i> Sincronizza Metriche
                    </button>
                    <p style="margin-top: 0.5rem; font-size: 0.875rem; color: #666;">Power data, FTP, soglie...</p>
                </div>
                
                <!-- Attività + Wellness -->
                <div style="margin-top: 1.5rem; padding: 1rem; background: #f0fdf4; border-radius: 8px;">
                    <h5 style="margin-bottom: 0.75rem; color: #10b981;">🏃 Attività e Wellness</h5>
                    <button class="btn btn-success" onclick="syncAthleteFullSync(${athleteId}, '${athlete.first_name} ${athlete.last_name}')">
                        <i class="bi bi-download"></i> Sincronizza Tutto (31 giorni)
                    </button>
                    <p style="margin-top: 0.5rem; font-size: 0.875rem; color: #666;">Attività + Wellness ultimi 31 giorni</p>
                </div>
                
                <!-- API Key Status -->
                <div style="margin-top: 1.5rem; padding: 1rem; background: ${athlete.api_key ? 'rgba(72, 187, 120, 0.1)' : 'rgba(245, 101, 101, 0.1)'}; border-radius: 8px;">
                    <p><strong>API Key:</strong> ${athlete.api_key ? '✅ Configurata' : '❌ Non configurata'}</p>
                    ${!athlete.api_key ? `
                        <button class="btn btn-warning btn-sm" onclick="editAthleteApiKeyQuick(${athleteId})" style="margin-top: 0.5rem;">
                            <i class="bi bi-pencil"></i> Aggiungi API Key
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }
};

window.showCreateAthleteDialog = function() {
    const teamsOptions = window.availableTeams.map(t => 
        `<option value="${t.id}">${t.name}</option>`
    ).join('');
    
    createModal(
        'Nuovo Atleta',
        `
        <div class="form-group">
            <label class="form-label">Nome <span style="color: red;">*</span></label>
            <input type="text" id="athlete-first-name" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Cognome <span style="color: red;">*</span></label>
            <input type="text" id="athlete-last-name" class="form-input" required>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
                <label class="form-label">Data di Nascita</label>
                <input type="date" id="athlete-birth-date" class="form-input">
            </div>
            <div class="form-group">
                <label class="form-label">Genere</label>
                <select id="athlete-gender" class="form-input">
                    <option value="">Seleziona</option>
                    <option value="Maschile">Maschile</option>
                    <option value="Femminile">Femminile</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">Squadra</label>
            <select id="athlete-team" class="form-input">
                <option value="">Nessuna squadra</option>
                ${teamsOptions}
            </select>
        </div>
        <div style="border-top: 2px solid #e0e0e0; margin-top: 1rem; padding-top: 1rem; margin-bottom: 1rem;">
            <p style="color: #666; font-size: 0.9rem; margin: 0 0 1rem 0;">
                <strong>Nota:</strong> Gli altri dati (peso, altezza, FC max, FTP) possono essere sincronizzati direttamente da Intervals.icu
            </p>
            <div class="form-group">
                <label class="form-label">API Key Intervals.icu <span style="color: #999;">(opzionale)</span></label>
                <div style="display: flex; gap: 8px;">
                    <input type="password" id="athlete-api-key" class="form-input" placeholder="Da: intervals.icu/settings" style="flex: 1;">
                    <button type="button" class="btn btn-secondary" onclick="toggleApiKeyVisibility('athlete-api-key')" style="padding: 8px 12px;">
                        👁️
                    </button>
                </div>
                <small style="color: #666;">Consente la sincronizzazione automatica di attività e metriche</small>
            </div>
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
                onclick: 'createAthlete()'
            }
        ]
    );
};

window.createAthlete = async function() {
    const firstName = document.getElementById('athlete-first-name').value.trim();
    const lastName = document.getElementById('athlete-last-name').value.trim();
    
    if (!firstName || !lastName) {
        showToast('Inserisci nome e cognome', 'warning');
        return;
    }
    
    const data = {
        first_name: firstName,
        last_name: lastName,
        birth_date: document.getElementById('athlete-birth-date').value || null,
        gender: document.getElementById('athlete-gender').value || null,
        team_id: document.getElementById('athlete-team').value ? parseInt(document.getElementById('athlete-team').value) : null,
        api_key: document.getElementById('athlete-api-key').value.trim() || null
    };
    
    try {
        showLoading();
        await api.createAthlete(data);
        showToast('Atleta creato con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderAthletesPage();
    } catch (error) {
        showToast('Errore nella creazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.editAthlete = async function(athleteId) {
    try {
        const athlete = await api.getAthlete(athleteId);
        
        const teamsOptions = window.availableTeams.map(t => 
            `<option value="${t.id}" ${t.id === athlete.team_id ? 'selected' : ''}>${t.name}</option>`
        ).join('');
        
        createModal(
            'Modifica Atleta',
            `
            <div class="form-group">
                <label class="form-label">Nome</label>
                <input type="text" id="athlete-first-name-edit" class="form-input" value="${athlete.first_name}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Cognome</label>
                <input type="text" id="athlete-last-name-edit" class="form-input" value="${athlete.last_name}" required>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label class="form-label">Data di Nascita</label>
                    <input type="date" id="athlete-birth-date-edit" class="form-input" value="${athlete.birth_date || ''}">
                </div>
                <div class="form-group">
                    <label class="form-label">Genere</label>
                    <select id="athlete-gender-edit" class="form-input">
                        <option value="">Seleziona</option>
                        <option value="Maschile" ${athlete.gender === 'Maschile' ? 'selected' : ''}>Maschile</option>
                        <option value="Femminile" ${athlete.gender === 'Femminile' ? 'selected' : ''}>Femminile</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Squadra</label>
                <select id="athlete-team-edit" class="form-input">
                    <option value="">Nessuna squadra</option>
                    ${teamsOptions}
                </select>
            </div>
            <div style="border-top: 2px solid #e0e0e0; margin-top: 1rem; padding-top: 1rem;">
                <h4>Sincronizzazione Intervals.icu</h4>
                <div class="form-group">
                    <label class="form-label">API Key Intervals.icu</label>
                    <div style="display: flex; gap: 8px;">
                        <input type="password" id="athlete-api-key-edit" class="form-input" value="${athlete.api_key || ''}" placeholder="Da: intervals.icu/settings" style="flex: 1;">
                        <button type="button" class="btn btn-secondary" onclick="toggleApiKeyVisibility('athlete-api-key-edit')" style="padding: 8px 12px;">
                            👁️
                        </button>
                    </div>
                    <small style="color: #666;">Consente la sincronizzazione di attività, metriche e dati di wellness</small>
                </div>
            </div>
            <div style="margin-top: 1rem; padding: 1rem; background: #f0f4f8; border-radius: 4px;">
                <p style="margin: 0; color: #15803d; font-size: 0.9rem;">
                    <strong>💡 Suggerimento:</strong> Usa il bottone <strong>"Sincronizza Metriche"</strong> nel profilo atleta per aggiornare automaticamente peso, altezza, FTP e FC max da Intervals.icu
                </p>
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
                    onclick: `updateAthlete(${athleteId})`
                }
            ]
        );
    } catch (error) {
        showToast('Errore nel caricamento dei dati', 'error');
    }
};

window.updateAthlete = async function(athleteId) {
    const data = {
        first_name: document.getElementById('athlete-first-name-edit').value.trim(),
        last_name: document.getElementById('athlete-last-name-edit').value.trim(),
        birth_date: document.getElementById('athlete-birth-date-edit').value || null,
        gender: document.getElementById('athlete-gender-edit').value || null,
        team_id: document.getElementById('athlete-team-edit').value ? parseInt(document.getElementById('athlete-team-edit').value) : null,
        api_key: document.getElementById('athlete-api-key-edit').value.trim() || null
    };
    
    try {
        showLoading();
        await api.updateAthlete(athleteId, data);
        showToast('Atleta aggiornato con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderAthletesPage();
    } catch (error) {
        showToast('Errore nell\'aggiornamento: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.deleteAthleteConfirm = function(athleteId) {
    createModal(
        '⚠️ Conferma Eliminazione',
        '<p>Sei sicuro di voler eliminare questo atleta? Verranno eliminate anche tutte le sue attività.</p>',
        [
            {
                label: 'Annulla',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Elimina Atleta',
                class: 'btn-danger',
                onclick: `deleteAthleteExecute(${athleteId})`
            }
        ]
    );
};

window.deleteAthleteExecute = async function(athleteId) {
    try {
        showLoading();
        await api.deleteAthlete(athleteId);
        showToast('Atleta eliminato con successo', 'success');
        document.querySelector('.modal-overlay')?.remove();
        window.renderAthletesPage();
    } catch (error) {
        showToast('Errore nell\'eliminazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

/**
 * Toggle API key visibility
 */
window.toggleApiKeyVisibility = function(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';
};

/**
 * Sync athlete metrics from Intervals.icu
 */
window.syncAthleteMetrics = async function(athleteId) {
    try {
        const athlete = await api.getAthlete(athleteId);
        
        if (!athlete.api_key) {
            showToast('L\'atleta non ha una API key configurata', 'warning');
            return;
        }
        
        showLoading();
        const result = await api.syncAthleteMetrics(athleteId, athlete.api_key);
        
        // Build detailed sync message
        const synced = result.synced_fields || {};
        const messages = [];
        if (synced.weight_kg) messages.push(`Peso: ${synced.weight_kg.toFixed(1)} kg`);
        if (synced.height_cm) messages.push(`Altezza: ${synced.height_cm.toFixed(0)} cm`);
        if (synced.cp) messages.push(`FTP: ${synced.cp.toFixed(0)} W`);
        if (synced.ecp) messages.push(`eCP: ${synced.ecp.toFixed(0)} W`);
        if (synced.w_prime) messages.push(`W': ${synced.w_prime.toFixed(0)} J`);
        if (synced.ew_prime) messages.push(`eW': ${synced.ew_prime.toFixed(0)} J`);
        if (synced.max_hr) messages.push(`FC Max: ${synced.max_hr.toFixed(0)} bpm`);
        
        const message = messages.length > 0 
            ? `Metriche sincronizzate!\\n${messages.join('\\n')}`
            : 'Nessun dato disponibile da sincronizzare';
        
        showToast(message, messages.length > 0 ? 'success' : 'warning');
        window.renderAthletesPage();
    } catch (error) {
        showToast('Errore nella sincronizzazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

/**
 * Sync athlete activities from Intervals.icu
 */
window.syncAthleteActivities = async function(athleteId) {
    try {
        const athlete = await api.getAthlete(athleteId);
        
        if (!athlete.api_key) {
            showToast('L\'atleta non ha una API key configurata. Modificalo per aggiungerne una.', 'warning');
            return;
        }
        
        // Ask for number of days
        const days = prompt('Quanti giorni di attività vuoi sincronizzare?', '30');
        if (!days || isNaN(days)) return;
        
        showLoading();
        const result = await api.syncActivities(athleteId, athlete.api_key, parseInt(days));
        
        const message = result.message || `Sincronizzate ${result.imported || 0} attività, saltate ${result.skipped || 0} duplicati`;
        showToast(message, 'success');
        
        // Refresh athlete detail view if we're on it
        if (window.currentAthleteView === athleteId) {
            window.renderAthletesPage();
        }
    } catch (error) {
        showToast('Errore sync attività: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

/**
 * Sync athlete activities + wellness from Intervals.icu in one shot
 */
window.syncAthleteFullSync = async function(athleteId, athleteName) {
    try {
        const athlete = await api.getAthlete(athleteId);
        
        if (!athlete.api_key) {
            showToast('L\'atleta non ha una API key configurata', 'warning');
            editAthleteApiKeyQuick(athleteId);
            return;
        }
        
        showLoading();
        const daysBack = 31;
        
        // Sync activities
        const activitiesResult = await api.syncActivities({
            athlete_id: athleteId,
            api_key: athlete.api_key,
            days_back: daysBack,
            include_intervals: true
        });
        
        // Sync wellness
        const wellnessResult = await api.syncWellness({
            athlete_id: athleteId,
            api_key: athlete.api_key,
            days_back: daysBack
        });
        
        hideLoading();
        
        // Show comprehensive success modal
        createModal(
            `✅ Sincronizzazione Completata - ${athleteName}`,
            `
            <div style="padding: 1rem;">
                <div style="margin-bottom: 1.5rem; padding: 1rem; background: #f0fdf4; border-radius: 6px;">
                    <h4 style="color: #10b981; margin-bottom: 0.5rem;">📊 Attività</h4>
                    <p>${activitiesResult.message || `Importate ${activitiesResult.imported || 0} su ${activitiesResult.total || 0} attività`}</p>
                </div>
                <div style="padding: 1rem; background: #f0f8ff; border-radius: 6px;">
                    <h4 style="color: #3b82f6; margin-bottom: 0.5rem;">❤️ Wellness</h4>
                    <p>${wellnessResult.message || `Importati ${wellnessResult.imported || 0} record wellness`}</p>
                </div>
            </div>
            `,
            [
                {
                    label: 'OK',
                    class: 'btn-primary',
                    onclick: 'this.closest(".modal-overlay").remove(); window.renderAthletesPage();'
                }
            ]
        );
    } catch (error) {
        hideLoading();
        showToast('Errore sincronizzazione: ' + error.message, 'error');
    }
};

/**
 * Edit athlete API key from detail view
 */
window.editAthleteApiKeyQuick = async function(athleteId) {
    try {
        const athlete = await api.getAthlete(athleteId);
        
        createModal(
            `API Key Intervals.icu - ${athlete.first_name} ${athlete.last_name}`,
            `
            <p style="margin-bottom: 1rem;">Inserisci la tua API key di Intervals.icu</p>
            <div class="form-group">
                <label class="form-label">API Key</label>
                <div style="display: flex; gap: 8px;">
                    <input type="password" id="athlete-api-key-input" class="form-input" value="${athlete.api_key || ''}" 
                           placeholder="Da: intervals.icu/settings" style="flex: 1;">
                    <button type="button" class="btn btn-secondary" onclick="toggleApiKeyVisibility('athlete-api-key-input')" style="padding: 8px 12px;">
                        👁️
                    </button>
                </div>
                <small><a href="https://intervals.icu/settings" target="_blank" style="color: #3b82f6;">Ottieni la tua API key</a></small>
            </div>
            `,
            [
                {
                    label: 'Annulla',
                    class: 'btn-secondary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                },
                {
                    label: '💾 Salva',
                    class: 'btn-primary',
                    onclick: `saveAthleteApiKeyQuick(${athleteId})`
                }
            ]
        );
    } catch (error) {
        showToast('Errore nel caricamento', 'error');
    }
};

/**
 * Save athlete API key from quick edit
 */
window.saveAthleteApiKeyQuick = async function(athleteId) {
    const apiKey = document.getElementById('athlete-api-key-input').value.trim();
    
    if (!apiKey) {
        showToast('L\'API key non può essere vuota', 'warning');
        return;
    }
    
    try {
        showLoading();
        await api.updateAthlete(athleteId, { api_key: apiKey });
        showToast('API key salvata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderAthletesPage();
    } catch (error) {
        showToast('Errore nel salvataggio: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

