/**
 * Athletes Module - Frontend
 * Multi-athlete dashboard with individual athlete detail views
 */

// Global state
window.currentAthleteView = null; // null = dashboard, number = athlete ID
window.athleteFilters = {
    team: null,
    category: null,
    gender: null
};

window.renderAthletesPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    console.log('[ATHLETES] renderAthletesPage started. currentAthleteView:', window.currentAthleteView);
    
    try {
        showLoading();
        const [athletes, teams, categories] = await Promise.all([
            api.getAthletes(),
            api.getTeams(),
            api.getCategories()
        ]);
        
        console.log('[ATHLETES] Loaded', athletes.length, 'athletes');
        
        // Store globally
        window.availableTeams = teams;
        window.availableCategories = categories;
        // Sort athletes alphabetically by last name
        athletes.sort((a, b) => a.last_name.localeCompare(b.last_name, 'it'));
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
    
    // Get unique teams and categories from athletes
    const uniqueTeams = [...new Set(athletes.map(a => a.team_name).filter(t => t))];
    const uniqueCategories = [...new Set(athletes.map(a => a.category_name).filter(c => c))];
    const uniqueGenders = ['Maschile', 'Femminile'];
    
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

                <!-- Filters Section -->
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid #ddd;">
                    <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                        <label style="font-weight: 600;">🔍 Filtri:</label>
                        
                        <select id="team-filter" style="padding: 0.5rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem; cursor: pointer;" onchange="applyAthleteFilters()">
                            <option value="">Tutti i Team</option>
                            ${uniqueTeams.map(team => `<option value="${team}">${team}</option>`).join('')}
                        </select>
                        
                        <select id="category-filter" style="padding: 0.5rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem; cursor: pointer;" onchange="applyAthleteFilters()">
                            <option value="">Tutte le Categorie</option>
                            ${uniqueCategories.map(cat => `<option value="${cat}">${cat}</option>`).join('')}
                        </select>
                        
                        <select id="gender-filter" style="padding: 0.5rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem; cursor: pointer;" onchange="applyAthleteFilters()">
                            <option value="">Tutti i Generi</option>
                            ${uniqueGenders.map(gender => `<option value="${gender}">${gender === 'Maschile' ? '👨 Maschile' : '👩 Femminile'}</option>`).join('')}
                        </select>
                        
                        <button class="btn btn-secondary btn-sm" onclick="clearAthleteFilters()" style="margin-left: auto;">
                            <i class="bi bi-x"></i> Cancella Filtri
                        </button>
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
                    <div class="athlete-team">${genderIcon} ${athlete.team_name || 'Nessuna squadra'} • ${athlete.category_name || 'Nessuna categoria'}</div>
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
                <div class="athlete-stat-row">
                    <span class="athlete-stat-label">kJ/h/kg:</span>
                    <span class="athlete-stat-value">${athlete.kj_per_hour_per_kg ? athlete.kj_per_hour_per_kg.toFixed(1) : '10.0'}</span>
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

window.applyAthleteFilters = function() {
    const teamFilter = document.getElementById('team-filter').value;
    const categoryFilter = document.getElementById('category-filter').value;
    const genderFilter = document.getElementById('gender-filter').value;
    
    // Store filter state
    window.athleteFilters = {
        team: teamFilter,
        category: categoryFilter,
        gender: genderFilter
    };
    
    // Get all athletes
    const allAthletes = window.allAthletes || [];
    
    // Filter athletes based on selected filters
    const filteredAthletes = allAthletes.filter(athlete => {
        if (teamFilter && athlete.team_name !== teamFilter) return false;
        if (categoryFilter && athlete.category_name !== categoryFilter) return false;
        if (genderFilter && athlete.gender !== genderFilter) return false;
        return true;
    });
    
    // Update grid with filtered athletes
    const gridContainer = document.getElementById('athletes-grid');
    if (gridContainer) {
        if (filteredAthletes.length === 0) {
            gridContainer.innerHTML = `
                <div style="grid-column: 1 / -1; padding: 2rem; text-align: center; color: #666;">
                    <p>Nessun atleta corrisponde ai filtri selezionati</p>
                </div>
            `;
        } else {
            gridContainer.innerHTML = filteredAthletes.map(athlete => createAthleteCard(athlete)).join('');
        }
    }
};

window.clearAthleteFilters = function() {
    // Reset filter state
    window.athleteFilters = {
        team: null,
        category: null,
        gender: null
    };
    
    // Reset filter inputs
    document.getElementById('team-filter').value = '';
    document.getElementById('category-filter').value = '';
    document.getElementById('gender-filter').value = '';
    
    // Reset grid to show all athletes
    const allAthletes = window.allAthletes || [];
    const gridContainer = document.getElementById('athletes-grid');
    if (gridContainer) {
        gridContainer.innerHTML = allAthletes.map(athlete => createAthleteCard(athlete)).join('');
    }
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
                    <!-- Tabs -->
                    <div class="tabs">
                        <button class="tab-button active" onclick="switchAthleteTab('activities')">
                            Attività (${activities.length})
                        </button>
                        <button class="tab-button" onclick="switchAthleteTab('stats')">
                            Statistiche
                        </button>
                        <button class="tab-button" onclick="switchAthleteTab('power-curve')">
                            Power Curve
                        </button>
                        <button class="tab-button" onclick="switchAthleteTab('cp')">
                            CP Model
                        </button>
                        <button class="tab-button" onclick="switchAthleteTab('seasons')">
                            Stagioni
                        </button>
                        <button class="tab-button" onclick="switchAthleteTab('sync')">
                            Sincronizzazione
                        </button>
                        <button class="tab-button" onclick="switchAthleteTab('details')">
                            Dettagli
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

window.switchAthleteTab = function(tabName, eventObj) {
    // Track which tab is active to prevent race conditions
    window.currentAthleteActiveTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    
    // If event is available, use it. Otherwise find the button by tabName
    if (eventObj && eventObj.target) {
        eventObj.target.classList.add('active');
    } else {
        // Find and activate the button with matching onclick
        const buttons = document.querySelectorAll('.tab-button');
        buttons.forEach(btn => {
            if (btn.textContent.toLowerCase().includes(tabName.toLowerCase())) {
                btn.classList.add('active');
            }
        });
    }
    
    const athleteId = window.currentAthleteView;
    const athlete = window.allAthletes.find(a => a.id === athleteId);
    
    const tabContent = document.getElementById('athlete-tab-content');
    
    if (tabName === 'activities') {
        // Already loaded, just re-fetch if needed
        api.getActivities({ athlete_id: athleteId, limit: 50 }).then(activities => {
            // Check if this tab is still active - prevent race condition
            if (window.currentAthleteActiveTab !== 'activities') {
                return;
            }
            tabContent.innerHTML = renderActivitiesTab(activities);
        });
    } else if (tabName === 'stats') {
        const athlete = window.allAthletes.find(a => a.id === athleteId);
        renderStatisticsTab(athleteId, athlete, tabContent);
    } else if (tabName === 'power-curve') {
        renderPowerCurveTab(athleteId, athlete, tabContent);
    } else if (tabName === 'cp') {
        renderCPTab(athleteId, athlete, tabContent);
    } else if (tabName === 'seasons') {
        renderSeasonsTab(athleteId, tabContent);
    } else if (tabName === 'details') {
        const athlete = window.allAthletes.find(a => a.id === athleteId);
        const wPerKg = athlete.cp && athlete.weight_kg ? (athlete.cp / athlete.weight_kg).toFixed(2) : '-';
        const teamsOptions = window.availableTeams.map(t => 
            `<option value="${t.id}" ${athlete.team_id === t.id ? 'selected' : ''}>${t.name}</option>`
        ).join('');
        const categoriesOptions = (window.availableCategories || []).map(c => 
            `<option value="${c.id}" ${athlete.category_id === c.id ? 'selected' : ''}>${c.name}</option>`
        ).join('');
        tabContent.innerHTML = `
            <div style="padding: 2rem;">
                <h4>Dettagli Atleta</h4>
                <form id="athlete-details-form" style="margin-top: 1.5rem;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">Squadra</label>
                            <select id="detail-team" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
                                <option value="">-</option>
                                ${teamsOptions}
                            </select>
                        </div>
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">Categoria</label>
                            <select id="detail-category" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
                                <option value="">-</option>
                                ${categoriesOptions}
                            </select>
                        </div>
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">Genere</label>
                            <select id="detail-gender" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
                                <option value="">-</option>
                                <option value="Maschile" ${athlete.gender === 'Maschile' ? 'selected' : ''}>Maschile</option>
                                <option value="Femminile" ${athlete.gender === 'Femminile' ? 'selected' : ''}>Femminile</option>
                            </select>
                        </div>
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">Peso (kg)</label>
                            <input type="number" id="detail-weight" step="0.1" value="${athlete.weight_kg || ''}" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
                        </div>
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">Altezza (cm)</label>
                            <input type="number" id="detail-height" step="0.1" value="${athlete.height_cm || ''}" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
                        </div>
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">FTP/CP (W)</label>
                            <input type="number" id="detail-cp" step="1" value="${athlete.cp || ''}" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
                        </div>
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">W' (J)</label>
                            <input type="number" id="detail-wprime" step="1" value="${athlete.w_prime || ''}" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
                        </div>
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">W/kg (calcolato)</label>
                            <input type="text" value="${wPerKg}" disabled style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; background: #f5f5f5; color: #666;">
                        </div>
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">kJ/h/kg</label>
                            <input type="number" id="detail-kj-per-kg" step="0.1" value="${athlete.kj_per_hour_per_kg || '10.0'}" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
                        </div>
                        <div style="display: flex; flex-direction: column;">
                            <label style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; font-weight: 500;">Data Nascita</label>
                            <input type="date" id="detail-birth-date" value="${athlete.birth_date ? athlete.birth_date.split('T')[0] : ''}" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
                        </div>
                    </div>
                    <div style="margin-top: 2rem; display: flex; gap: 1rem;">
                        <button type="button" class="btn btn-primary" onclick="saveAthleteDetails(${athleteId})">
                            <i class="bi bi-check-circle"></i> Salva Modifiche
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="switchAthleteTab('activities')">
                            <i class="bi bi-x-circle"></i> Annulla
                        </button>
                    </div>
                </form>
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

// ========== POWER CURVE TAB ==========

async function renderPowerCurveTab(athleteId, athlete, tabContent) {
    if (!athlete.api_key) {
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #ffc107; margin-bottom: 1rem;">
                    <i class="bi bi-exclamation-triangle" style="font-size: 2rem; color: #ff9800;"></i>
                    <h4 style="margin-top: 1rem; color: #856404;">API Key Non Configurata</h4>
                    <p style="color: #856404; margin-top: 0.5rem;">
                        Per visualizzare la power curve è necessario configurare l'API key di Intervals.icu per questo atleta.
                    </p>
                    <button class="btn btn-warning" onclick="editAthlete(${athleteId})" style="margin-top: 1rem;">
                        <i class="bi bi-pencil"></i> Configura API Key
                    </button>
                </div>
            </div>
        `;
        return;
    }

    // Show loading state
    tabContent.innerHTML = `
        <div style="padding: 2rem; text-align: center;">
            <div class="spinner" style="margin: 2rem auto;"></div>
            <p style="color: #666; margin-top: 1rem;">Caricamento power curve da Intervals.icu...</p>
        </div>
    `;

    // Initialize cache if needed
    if (!window.athletePowerCurveCache) {
        window.athletePowerCurveCache = {};
    }

    try {
        // Calculate dates for 90-day curve
        const today = new Date();
        const days90ago = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
        const dateStr90 = days90ago.toISOString().split('T')[0];
        const todayStr = today.toISOString().split('T')[0];

        // Create cache key
        const cacheKey = `${athleteId}_powercurve`;
        
        // Check if data is already cached
        let cachedData;
        if (window.athletePowerCurveCache[cacheKey]) {
            console.log('[ATHLETES] Using cached power curve data for athlete', athleteId);
            cachedData = window.athletePowerCurveCache[cacheKey];
        } else {
            console.log('[ATHLETES] Loading fresh power curve data for athlete', athleteId);
            // Fetch seasons and power curves in parallel
            const [seasonsResponse, response90, responseAllTime] = await Promise.all([
                api.getAthleteSeasons(athleteId),
                fetch(`/api/athletes/${athleteId}/power-curve?oldest=${dateStr90}&newest=${todayStr}`),
                fetch(`/api/athletes/${athleteId}/power-curve`)
            ]);

            if (!response90.ok || !responseAllTime.ok) {
                throw new Error(`HTTP error! status: ${response90.status || responseAllTime.status}`);
            }

            const seasons = seasonsResponse;
            const data90d = await response90.json();
            const dataAllTime = await responseAllTime.json();

            // Fetch power curves for each season
            const seasonPowerCurves = {};
            for (const season of seasons) {
                const endDate = season.end_date || todayStr;
                try {
                    const seasonResponse = await fetch(
                        `/api/athletes/${athleteId}/power-curve?oldest=${season.start_date}&newest=${endDate}`
                    );
                    if (seasonResponse.ok) {
                        seasonPowerCurves[season.id] = await seasonResponse.json();
                    }
                } catch (err) {
                    console.warn(`Failed to load power curve for season ${season.id}:`, err);
                }
            }

            cachedData = {
                seasons: seasons,
                data90d: data90d,
                dataAllTime: dataAllTime,
                seasonPowerCurves: seasonPowerCurves
            };
            
            // Cache the loaded data
            window.athletePowerCurveCache[cacheKey] = cachedData;
        }

        const { seasons, data90d, dataAllTime, seasonPowerCurves } = cachedData;

        // Check if this tab is still active - prevent race condition
        if (window.currentAthleteActiveTab !== 'power-curve') {
            return;
        }

        // Store datasets globally
        window.powerCurve90d = data90d;
        window.powerCurveAllTime = dataAllTime;
        window.powerCurveSeasons = seasonPowerCurves;
        window.athleteSeasons = seasons;
        window.selectedPeriod = '90d';
        window.currentAthleteId = athleteId;

        // Build period selector HTML with seasons
        let periodSelectorHtml = `
            <label style="display: flex; align-items: center; gap: 0.5rem;">
                <input type="radio" name="power-period" value="90d" checked onchange="switchPowerCurvePeriod('90d')">
                90 giorni
            </label>
            <label style="display: flex; align-items: center; gap: 0.5rem;">
                <input type="radio" name="power-period" value="allTime" onchange="switchPowerCurvePeriod('allTime')">
                Tutto il tempo
            </label>
        `;

        // Add radio buttons for each season
        seasons.forEach(season => {
            periodSelectorHtml += `
            <label style="display: flex; align-items: center; gap: 0.5rem;">
                <input type="radio" name="power-period" value="season-${season.id}" onchange="switchPowerCurvePeriod('season-${season.id}')">
                ${season.name}
            </label>
            `;
        });

        // Render power curve UI with period selector
        tabContent.innerHTML = `
            <div style="padding: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
                    <h4 style="margin: 0;">📈 Power Curve</h4>
                    <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                        <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
                            <label style="font-weight: 500; white-space: nowrap;">Periodo:</label>
                            ${periodSelectorHtml}
                        </div>
                        <button class="btn btn-secondary btn-sm" onclick="showCustomPeriodPicker(${athleteId})">
                            📅 Custom
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="refreshPowerCurve(${athleteId})">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Main Container: Chart and Table Side-by-Side -->
                <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem;">
                    <!-- Chart Container -->
                    <div id="power-curve-chart" style="width: 100%; height: 500px; background: white; border: 1px solid #e0e0e0; border-radius: 8px;"></div>
                    
                    <!-- Best Efforts Table -->
                    <div style="background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; height: 500px; overflow-y: auto;">
                        <h5 style="margin: 0 0 0.75rem 0; font-size: 0.95rem;">🏆 Migliori Sforzi</h5>
                        <div id="best-efforts-table"></div>
                    </div>
                </div>
            </div>
        `;

        // Render the chart with 90-day data by default
        renderPowerCurveChart(data90d);

    } catch (error) {
        console.error('Error loading power curve:', error);
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <div style="background: #fee; padding: 1.5rem; border-radius: 8px; border: 1px solid #fcc;">
                    <i class="bi bi-x-circle" style="font-size: 2rem; color: #d32f2f;"></i>
                    <h4 style="margin-top: 1rem; color: #c62828;">Errore nel caricamento</h4>
                    <p style="color: #666; margin-top: 0.5rem;">
                        Non è stato possibile caricare la power curve: ${error.message}
                    </p>
                    <button class="btn btn-primary" onclick="refreshPowerCurve(${athleteId})" style="margin-top: 1rem;">
                        <i class="bi bi-arrow-clockwise"></i> Riprova
                    </button>
                </div>
            </div>
        `;
    }
}

// ========== STATISTICS TAB ==========

async function renderStatisticsTab(athleteId, athlete, tabContent) {
    if (!athlete.api_key) {
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #ffc107; margin-bottom: 1rem;">
                    <i class="bi bi-exclamation-triangle" style="font-size: 2rem; color: #ff9800;"></i>
                    <h4 style="margin-top: 1rem; color: #856404;">API Key Non Configurata</h4>
                    <p style="color: #856404; margin-top: 0.5rem;">
                        Per visualizzare le statistiche è necessario configurare l'API key di Intervals.icu per questo atleta.
                    </p>
                </div>
            </div>
        `;
        return;
    }

    // Show loading
    tabContent.innerHTML = `
        <div style="padding: 2rem; text-align: center;">
            <div class="spinner" style="margin: 2rem auto;"></div>
            <p style="color: #666; margin-top: 1rem;">Caricamento statistiche...</p>
        </div>
    `;

    // Initialize cache if needed
    if (!window.athleteStatsCache) {
        window.athleteStatsCache = {};
    }

    try {
        const today = new Date();
        const days90ago = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
        const dateStr90 = days90ago.toISOString().split('T')[0];
        const todayStr = today.toISOString().split('T')[0];

        // Create cache key
        const cacheKey = `${athleteId}_stats`;
        
        // Check if data is already cached
        let cachedData;
        if (window.athleteStatsCache[cacheKey]) {
            console.log('[ATHLETES] Using cached statistics data for athlete', athleteId);
            cachedData = window.athleteStatsCache[cacheKey];
        } else {
            console.log('[ATHLETES] Loading fresh statistics data for athlete', athleteId);
            // Fetch all data in parallel
            const [seasonsResponse, response90, responseAllTime] = await Promise.all([
                api.getAthleteSeasons(athleteId),
                fetch(`/api/athletes/${athleteId}/power-curve?oldest=${dateStr90}&newest=${todayStr}`),
                fetch(`/api/athletes/${athleteId}/power-curve`)
            ]);

            if (!response90.ok || !responseAllTime.ok) {
                throw new Error('Errore nel caricamento dei dati');
            }

            const seasons = seasonsResponse;
            const data90d = await response90.json();
            const dataAllTime = await responseAllTime.json();

            // Fetch power curves for each season
            const seasonPowerCurves = {};
            for (const season of seasons) {
                const endDate = season.end_date || todayStr;
                try {
                    const seasonResponse = await fetch(
                        `/api/athletes/${athleteId}/power-curve?oldest=${season.start_date}&newest=${endDate}`
                    );
                    if (seasonResponse.ok) {
                        seasonPowerCurves[season.id] = await seasonResponse.json();
                    }
                } catch (err) {
                    console.warn(`Failed to load power curve for season ${season.id}:`, err);
                }
            }

            cachedData = {
                seasons: seasons,
                data90d: data90d,
                dataAllTime: dataAllTime,
                seasonPowerCurves: seasonPowerCurves
            };
            
            // Cache the loaded data
            window.athleteStatsCache[cacheKey] = cachedData;
        }

        const { seasons, data90d, dataAllTime, seasonPowerCurves } = cachedData;

        // Get weight for pro kg calculations
        const weight = athlete.weight_kg || 1;

        // Calculate statistics for all periods
        const statistics = [];

        // Default filter parameters for CP calculation
        const valuesPerWindow = 1;
        const minPercentile = 100;  // Start from 100% and auto-search downwards
        const sprintSeconds = 1;

        // 1. Calculate for 90 days
        const stats90d = await calculatePeriodStatistics(
            data90d, 
            'Ultimi 90 giorni', 
            weight, 
            valuesPerWindow, 
            minPercentile, 
            sprintSeconds
        );
        if (stats90d) statistics.push(stats90d);

        // 2. Calculate for each season
        for (const season of seasons) {
            const seasonData = seasonPowerCurves[season.id];
            if (seasonData && seasonData.secs && seasonData.secs.length > 0) {
                const seasonStats = await calculatePeriodStatistics(
                    seasonData,
                    season.name,
                    weight,
                    valuesPerWindow,
                    minPercentile,
                    sprintSeconds
                );
                if (seasonStats) statistics.push(seasonStats);
            }
        }

        // Check if this tab is still active - prevent race condition
        if (window.currentAthleteActiveTab !== 'stats') {
            return;
        }

        // Render statistics table
        renderStatisticsTable(statistics, weight);

    } catch (error) {
        console.error('Error loading statistics:', error);
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <div style="background: #fee; padding: 1.5rem; border-radius: 8px; border: 1px solid #fcc;">
                    <i class="bi bi-x-circle" style="font-size: 2rem; color: #d32f2f;"></i>
                    <h4 style="margin-top: 1rem; color: #c62828;">Errore nel caricamento</h4>
                    <p style="color: #666; margin-top: 0.5rem;">
                        ${error.message}
                    </p>
                </div>
            </div>
        `;
    }
}

// Calculate statistics for a specific period (90d or season)
// Uses centralized calculateCPModel from omnipd.js
async function calculatePeriodStatistics(powerData, periodName, weight, valuesPerWindow, minPercentile, sprintSeconds) {
    try {
        const durations = powerData.secs || [];
        const watts = powerData.watts || [];

        if (!durations || durations.length < 4) {
            return null;
        }

        // Use centralized CP calculation (omnipd.js) - single source of truth
        const cpModel = calculateCPModel(durations, watts, weight);
        
        if (!cpModel) {
            return null;
        }

        // Return result with period name + all CP model data
        return {
            periodName: periodName,
            ...cpModel
        };
    } catch (error) {
        console.warn(`Error calculating statistics for ${periodName}:`, error);
        return null;
    }
}

// Render statistics as a comprehensive table
function renderStatisticsTable(statistics, weight) {
    const tabContent = document.getElementById('athlete-tab-content');

    let html = `
        <div style="padding: 1.5rem;">
            <!-- CP & W' Section -->
            <div style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead style="background: #f8f9fa;">
                        <tr>
                            <th style="padding: 1rem; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">Periodo</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">CP (W)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">CP (W/kg)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">W' (J)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; font-size: 0.9rem;">W'/kg (kJ/kg)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">pMax (W)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">pMax (W/kg)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; font-size: 0.9rem;">RMSE (W)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; font-size: 0.9rem;">Percentile</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; font-size: 0.9rem;">Punti</th>
                        </tr>
                    </thead>
                    <tbody>`;

    statistics.forEach((stat, idx) => {
        const bgColor = idx === 0 ? '#f0f7ff' : (idx % 2 === 0 ? '#f8f9fa' : 'white');
        const w_prime_j = stat.w_prime;
        const w_prime_kg_kj = stat.w_prime_kg;
        const pmax_w = stat.pmax;
        const pmax_kg = stat.pmax_kg;
        
        html += `
            <tr style="background: ${bgColor}; border-bottom: 1px solid #eee;">
                <td style="padding: 1rem; font-weight: ${idx === 0 ? '600' : '500'}; color: ${idx === 0 ? '#667eea' : '#333'};">${stat.periodName}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #667eea;">${stat.cp}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #4facfe;">${stat.cp_kg} <span style="font-size: 0.85rem; color: #666;"></span></td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #667eea;">${w_prime_j}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #4facfe;">${w_prime_kg_kj}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #ff6b6b;">${pmax_w}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #ff6b6b;">${pmax_kg}</td>
                <td style="padding: 1rem; text-align: center; font-size: 0.9rem; color: #999;">${stat.rmse}</td>
                <td style="padding: 1rem; text-align: center; font-size: 0.9rem; color: #666;">${stat.usedPercentile}%</td>
                <td style="padding: 1rem; text-align: center; font-size: 0.9rem; color: #666;">${stat.pointsUsed}</td>
            </tr>
        `;
    });

    html += `
                    </tbody>
                </table>
            </div>

            <!-- MMP Section -->
            <div style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead style="background: #f8f9fa;">
                        <tr>
                            <th style="padding: 1rem; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">Periodo</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">MMP 1s</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">MMP 5s</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">MMP 3'</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">MMP 6'</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">MMP 12'</th>
                        </tr>
                    </thead>
                    <tbody>`;

    statistics.forEach((stat, idx) => {
        const bgColor = idx === 0 ? '#f0f7ff' : (idx % 2 === 0 ? '#f8f9fa' : 'white');
        
        const formatMMP = (watts) => {
            if (watts === null) return '-';
            const perKg = (watts / weight).toFixed(1);
            return `<div style="font-weight: 600; color: #3b82f6;">${Math.round(watts)} W</div><div style="font-size: 0.8rem; color: #666;">${perKg} W/kg</div>`;
        };

        html += `
            <tr style="background: ${bgColor}; border-bottom: 1px solid #eee;">
                <td style="padding: 1rem; font-weight: ${idx === 0 ? '600' : '500'}; color: ${idx === 0 ? '#667eea' : '#333'};">${stat.periodName}</td>
                <td style="padding: 1rem; text-align: center;">${formatMMP(stat.mmp_1s)}</td>
                <td style="padding: 1rem; text-align: center;">${formatMMP(stat.mmp_5s)}</td>
                <td style="padding: 1rem; text-align: center;">${formatMMP(stat.mmp_3m)}</td>
                <td style="padding: 1rem; text-align: center;">${formatMMP(stat.mmp_6m)}</td>
                <td style="padding: 1rem; text-align: center;">${formatMMP(stat.mmp_12m)}</td>
            </tr>
        `;
    });

    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;

    tabContent.innerHTML = html;
}

// ========== CP MODEL TAB ==========

async function renderCPTab(athleteId, athlete, tabContent) {
    if (!athlete.api_key) {
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #ffc107; margin-bottom: 1rem;">
                    <i class="bi bi-exclamation-triangle" style="font-size: 2rem; color: #ff9800;"></i>
                    <h4 style="margin-top: 1rem; color: #856404;">API Key Non Configurata</h4>
                    <p style="color: #856404; margin-top: 0.5rem;">
                        Per calcolare il modello CP è necessario configurare l'API key di Intervals.icu per questo atleta.
                    </p>
                    <button class="btn btn-warning" onclick="editAthlete(${athleteId})" style="margin-top: 1rem;">
                        <i class="bi bi-pencil"></i> Configura API Key
                    </button>
                </div>
            </div>
        `;
        return;
    }

    // Show loading
    tabContent.innerHTML = `
        <div style="padding: 2rem; text-align: center;">
            <div class="spinner" style="margin: 2rem auto;"></div>
            <p style="color: #666; margin-top: 1rem;">Caricamento dati per modello CP...</p>
        </div>
    `;

    // Initialize cache if needed
    if (!window.athleteCPCache) {
        window.athleteCPCache = {};
    }

    try {
        // Calculate dates for 90-day default
        const today = new Date();
        const days90ago = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
        const dateStr90 = days90ago.toISOString().split('T')[0];
        const todayStr = today.toISOString().split('T')[0];

        // Create cache key
        const cacheKey = `${athleteId}_cp`;
        
        // Check if data is already cached
        let cachedData;
        if (window.athleteCPCache[cacheKey]) {
            console.log('[ATHLETES] Using cached CP data for athlete', athleteId);
            cachedData = window.athleteCPCache[cacheKey];
        } else {
            console.log('[ATHLETES] Loading fresh CP data for athlete', athleteId);
            // Fetch seasons and 90-day power curve
            const [seasonsResponse, response90] = await Promise.all([
                api.getAthleteSeasons(athleteId),
                fetch(`/api/athletes/${athleteId}/power-curve?oldest=${dateStr90}&newest=${todayStr}`)
            ]);

            if (!response90.ok) {
                throw new Error(`HTTP error! status: ${response90.status}`);
            }

            const seasons = seasonsResponse;
            const data90d = await response90.json();

            cachedData = {
                seasons: seasons,
                data90d: data90d
            };
            
            // Cache the loaded data
            window.athleteCPCache[cacheKey] = cachedData;
        }

        const { seasons, data90d } = cachedData;

        // Check if this tab is still active - prevent race condition
        if (window.currentAthleteActiveTab !== 'cp') {
            return;
        }

        // Store globally for CP tab
        window.cpDataRaw = { '90d': data90d };
        window.cpSeasons = seasons;
        window.cpCurrentPeriod = '90d';
        window.cpCurrentAthleteId = athleteId;

        // Convert power curve to time/power arrays
        // API returns {secs: [], watts: []} format
        const allTimes = data90d.secs || [];
        const allPowers = data90d.watts || [];

        // Default filter parameters
        const defaultValuesPerWindow = 1;
        const defaultMinPercentile = 80;
        const defaultSprintSeconds = 1;

        // Render UI with controls and placeholders for charts
        tabContent.innerHTML = `
            <div style="padding: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
                    <h4 style="margin: 0;">⚡ Modello omniPD Critical Power</h4>
                </div>

                <!-- Period Selector -->
                <div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
                    <h5 style="margin-bottom: 1rem;">📅 Periodo Dati</h5>
                    <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                        <label style="display: flex; align-items: center; gap: 0.5rem;">
                            <input type="radio" name="cp-period" value="90d" checked onchange="switchCPPeriod('90d')">
                            90 giorni
                        </label>
                        ${seasons.map(s => `
                            <label style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="radio" name="cp-period" value="season-${s.id}" onchange="switchCPPeriod('season-${s.id}')">
                                ${s.name}
                            </label>
                        `).join('')}
                    </div>
                </div>

                <!-- Filter Controls -->
                <div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
                    <h5 style="margin-bottom: 1rem;">⚙️ Filtri Selezione Dati</h5>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                        <div class="input-field">
                            <label>Valori per finestra</label>
                            <input type="number" id="cp-values-per-window" value="${defaultValuesPerWindow}" min="1" onchange="recalculateCP()">
                        </div>
                        <div class="input-field">
                            <label>Percentile minimo (%)</label>
                            <input type="number" id="cp-min-percentile" value="${defaultMinPercentile}" min="0" max="100" onchange="recalculateCP()">
                        </div>
                        <div class="input-field">
                            <label>Durata sprint (s)</label>
                            <input type="number" id="cp-sprint-seconds" value="${defaultSprintSeconds}" min="1" onchange="recalculateCP()">
                        </div>
                        <div class="input-field">
                            <label><input type="checkbox" id="cp-use-long-point-fallback" checked onchange="recalculateCP()"> Punto > 10 min (sì/no)</label>
                        </div>
                    </div>
                </div>

                <!-- Results Stats -->
                <div id="cp-results-stats" style="margin-bottom: 1.5rem;">
                    <!-- Stats will be populated by JS -->
                </div>

                <!-- Charts Grid -->
                <div class="charts-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div id="cp-chart-1" style="grid-column: 1 / -1; width: 100%; height: 600px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></div>
                    <div id="cp-chart-2" style="width: 100%; height: 500px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></div>
                    <div id="cp-chart-3" style="width: 100%; height: 500px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></div>
                </div>
            </div>
        `;

        // Calculate and render with auto-search from 100% percentile
        const useLongPointFallback = 1; // default enabled
        calculateAndRenderCPWithAutoSearch(allTimes, allPowers, defaultValuesPerWindow, defaultSprintSeconds, useLongPointFallback);

    } catch (error) {
        console.error('Error loading CP model:', error);
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <div style="background: #fee; padding: 1.5rem; border-radius: 8px; border: 1px solid #fcc;">
                    <i class="bi bi-x-circle" style="font-size: 2rem; color: #d32f2f;"></i>
                    <h4 style="margin-top: 1rem; color: #c62828;">Errore nel caricamento</h4>
                    <p style="color: #666; margin-top: 0.5rem;">
                        ${error.message}
                    </p>
                </div>
            </div>
        `;
    }
}

// Calculate and render CP model
function calculateAndRenderCP(allTimes, allPowers, valuesPerWindow, minPercentile, sprintSeconds, useLongPointFallback = 1) {
    try {
        // Filter data using same logic as calculateAndRenderCPWithAutoSearch
        let selectedTimes = [];
        let selectedPowers = [];
        
        // Fit all data to get residuals
        const params = curveFit(allTimes, allPowers);
        const predictions = allTimes.map((t) => ompd_power(t, ...params));
        const residuals = allPowers.map((p, i) => p - predictions[i]);

        // Calculate percentile threshold
        const residualsClean = residuals.filter(r => !isNaN(r));
        if (residualsClean.length === 0) {
            showToast('Dati insufficienti dopo il filtraggio. Diminuisci il percentile minimo.', 'warning');
            return;
        }

        residualsClean.sort((a, b) => a - b);
        const h = (residualsClean.length - 1) * (minPercentile / 100);
        const floor_idx = Math.floor(h);
        const ceil_idx = Math.ceil(h);
        const frac = h - floor_idx;
        
        let percentileThreshold;
        if (floor_idx === ceil_idx) {
            percentileThreshold = residualsClean[floor_idx];
        } else {
            percentileThreshold = residualsClean[floor_idx] * (1 - frac) + residualsClean[ceil_idx] * frac;
        }

        // Define time windows: 2-minute intervals up to 30 min, then 15-minute intervals to 90 min
        const timeWindows = [];
        for (let start = 120; start < 1800; start += 120) {
            timeWindows.push([start, start + 120]);
        }
        for (let start = 1800; start < 5400; start += 900) {
            timeWindows.push([start, start + 900]);
        }

        let selectedMask = new Array(allTimes.length).fill(false);

        // Select points from each window
        for (const [tmin, tmax] of timeWindows) {
            const windowIndices = [];
            for (let i = 0; i < allTimes.length; i++) {
                if (allTimes[i] >= tmin && allTimes[i] <= tmax) {
                    windowIndices.push(i);
                }
            }
            if (windowIndices.length === 0) continue;

            // Sort by residual descending
            const sortedIndices = windowIndices.sort((a, b) => residuals[b] - residuals[a]);

            // Take up to valuesPerWindow where residual >= threshold
            let count = 0;
            for (const i of sortedIndices) {
                if (!isNaN(residuals[i]) && residuals[i] >= percentileThreshold && !selectedMask[i]) {
                    selectedTimes.push(allTimes[i]);
                    selectedPowers.push(allPowers[i]);
                    selectedMask[i] = true;
                    count++;
                    if (count >= valuesPerWindow) break;
                }
            }
        }

        // Sprint point
        let minDist = Infinity;
        let sprintIdx = -1;
        for (let i = 0; i < allTimes.length; i++) {
            const dist = Math.abs(allTimes[i] - sprintSeconds);
            if (dist < minDist) {
                minDist = dist;
                sprintIdx = i;
            }
        }
        if (sprintIdx >= 0 && !selectedMask[sprintIdx]) {
            selectedTimes.push(allTimes[sprintIdx]);
            selectedPowers.push(allPowers[sprintIdx]);
            selectedMask[sprintIdx] = true;
        }

        // CHECK: If no points > 600s, add best point from 10-30 min range (only if useLongPointFallback = 1)
        const hasLongPoint = selectedTimes.some(t => t > 600);
        if (!hasLongPoint && useLongPointFallback === 1) {
            let bestIdx = -1;
            let bestResidual = -Infinity;
            
            // Find highest residual in 10-30 min range (600-1800s)
            for (let i = 0; i < allTimes.length; i++) {
                if (allTimes[i] >= 600 && allTimes[i] <= 1800 && !selectedMask[i]) {
                    if (residuals[i] > bestResidual) {
                        bestResidual = residuals[i];
                        bestIdx = i;
                    }
                }
            }
            
            if (bestIdx >= 0) {
                selectedTimes.push(allTimes[bestIdx]);
                selectedPowers.push(allPowers[bestIdx]);
                selectedMask[bestIdx] = true;
            }
        }

        if (selectedTimes.length < 4) {
            showToast('Dati insufficienti dopo il filtraggio. Diminuisci il percentile minimo.', 'warning');
            return;
        }

        // Sort selected data by time for proper plotting
        const sortedIndices = selectedTimes.map((_, i) => i).sort((a, b) => selectedTimes[a] - selectedTimes[b]);
        selectedTimes = sortedIndices.map(i => selectedTimes[i]);
        selectedPowers = sortedIndices.map(i => selectedPowers[i]);

        // Calculate omniPD parameters
        const result = calculateOmniPD(selectedTimes, selectedPowers);

        // Create filtered object for updateCPStats
        const filtered = {
            times: selectedTimes,
            powers: selectedPowers,
            selectedCount: selectedTimes.length,
            totalCount: allTimes.length
        };

        // Update stats display
        updateCPStats(result, filtered);

        // Create charts
        createCPCharts(allTimes, allPowers, selectedTimes, selectedPowers, result);

    } catch (error) {
        console.error('Error calculating CP:', error);
        showToast('Errore nel calcolo del modello: ' + error.message, 'error');
    }
}

// Calculate CP with automatic percentile search (from 100% down)
function calculateAndRenderCPWithAutoSearch(allTimes, allPowers, valuesPerWindow, sprintSeconds, useLongPointFallback = 1) {
    try {
        let currentPercentile = 100;
        let usedPercentile = 100;
        let selectedTimes = [];
        let selectedPowers = [];

        // Search for percentile starting from 100, decreasing until we have enough points
        while (currentPercentile >= 0) {
            selectedTimes = [];
            selectedPowers = [];
            
            // Fit all data to get residuals
            const params = curveFit(allTimes, allPowers);
            const predictions = allTimes.map((t) => ompd_power(t, ...params));
            const residuals = allPowers.map((p, i) => p - predictions[i]);

            // Calculate percentile threshold
            const residualsClean = residuals.filter(r => !isNaN(r));
            if (residualsClean.length === 0) {
                currentPercentile--;
                continue;
            }

            residualsClean.sort((a, b) => a - b);
            const h = (residualsClean.length - 1) * (currentPercentile / 100);
            const floor_idx = Math.floor(h);
            const ceil_idx = Math.ceil(h);
            const frac = h - floor_idx;
            
            let percentileThreshold;
            if (floor_idx === ceil_idx) {
                percentileThreshold = residualsClean[floor_idx];
            } else {
                percentileThreshold = residualsClean[floor_idx] * (1 - frac) + residualsClean[ceil_idx] * frac;
            }

            // Define time windows: 2-minute intervals up to 30 min, then 15-minute intervals to 90 min
            const timeWindows = [];
            for (let start = 120; start < 1800; start += 120) {
                timeWindows.push([start, start + 120]);
            }
            for (let start = 1800; start < 5400; start += 900) {
                timeWindows.push([start, start + 900]);
            }

            let selectedMask = new Array(allTimes.length).fill(false);

            // Select points from each window
            for (const [tmin, tmax] of timeWindows) {
                const windowIndices = [];
                for (let i = 0; i < allTimes.length; i++) {
                    if (allTimes[i] >= tmin && allTimes[i] <= tmax) {
                        windowIndices.push(i);
                    }
                }
                if (windowIndices.length === 0) continue;

                // Sort by residual descending
                const sortedIndices = windowIndices.sort((a, b) => residuals[b] - residuals[a]);

                // Take up to valuesPerWindow where residual >= threshold
                let count = 0;
                for (const i of sortedIndices) {
                    if (!isNaN(residuals[i]) && residuals[i] >= percentileThreshold && !selectedMask[i]) {
                        selectedTimes.push(allTimes[i]);
                        selectedPowers.push(allPowers[i]);
                        selectedMask[i] = true;
                        count++;
                        if (count >= valuesPerWindow) break;
                    }
                }
            }

            // Sprint point (1 second)
            let minDist = Infinity;
            let sprintIdx = -1;
            for (let i = 0; i < allTimes.length; i++) {
                const dist = Math.abs(allTimes[i] - sprintSeconds);
                if (dist < minDist) {
                    minDist = dist;
                    sprintIdx = i;
                }
            }
            if (sprintIdx >= 0 && !selectedMask[sprintIdx]) {
                selectedTimes.push(allTimes[sprintIdx]);
                selectedPowers.push(allPowers[sprintIdx]);
                selectedMask[sprintIdx] = true;
            }

            // CHECK: If no points > 600s, add best point from 10-30 min range (only if useLongPointFallback = 1)
            const hasLongPoint = selectedTimes.some(t => t > 600);
            if (!hasLongPoint && useLongPointFallback === 1) {
                let bestIdx = -1;
                let bestResidual = -Infinity;
                
                // Find highest residual in 10-30 min range (600-1800s)
                for (let i = 0; i < allTimes.length; i++) {
                    if (allTimes[i] >= 600 && allTimes[i] <= 1800 && !selectedMask[i]) {
                        if (residuals[i] > bestResidual) {
                            bestResidual = residuals[i];
                            bestIdx = i;
                        }
                    }
                }
                
                if (bestIdx >= 0) {
                    selectedTimes.push(allTimes[bestIdx]);
                    selectedPowers.push(allPowers[bestIdx]);
                    selectedMask[bestIdx] = true;
                }
            }

            // Check if we have enough points
            if (selectedTimes.length >= 4) {
                usedPercentile = currentPercentile;
                break;
            }
            
            currentPercentile--;
        }

        if (selectedTimes.length < 4) {
            showToast('Dati insufficienti dopo il filtraggio. Non ci sono abbastanza punti validi.', 'warning');
            return;
        }

        // Sort selected data by time for proper plotting
        const sortedIndices = selectedTimes.map((_, i) => i).sort((a, b) => selectedTimes[a] - selectedTimes[b]);
        selectedTimes = sortedIndices.map(i => selectedTimes[i]);
        selectedPowers = sortedIndices.map(i => selectedPowers[i]);

        // Update the input field with the found percentile
        const input = document.getElementById('cp-min-percentile');
        if (input) {
            input.value = usedPercentile;
        }

        // Calculate omniPD parameters
        const result = calculateOmniPD(selectedTimes, selectedPowers);

        // Create filtered object for updateCPStats
        const filtered = {
            times: selectedTimes,
            powers: selectedPowers,
            selectedCount: selectedTimes.length,
            totalCount: allTimes.length
        };

        // Update stats display
        updateCPStats(result, filtered);

        // Create charts
        createCPCharts(allTimes, allPowers, selectedTimes, selectedPowers, result);

        console.log(`[CP Model] Auto-search found ${selectedTimes.length} points at ${usedPercentile}% percentile`);

    } catch (error) {
        console.error('Error calculating CP with auto-search:', error);
        showToast('Errore nel calcolo del modello: ' + error.message, 'error');
    }
}

// Update CP statistics display
function updateCPStats(result, filtered) {
    const statsHtml = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);">
                <h6 style="margin: 0 0 0.5rem 0; opacity: 0.9; font-size: 0.875rem;">CP (Critical Power)</h6>
                <div style="font-size: 2rem; font-weight: 700;">${result.CP} W</div>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);">
                <h6 style="margin: 0 0 0.5rem 0; opacity: 0.9; font-size: 0.875rem;">W' (Anaerobic Capacity)</h6>
                <div style="font-size: 2rem; font-weight: 700;">${result.W_prime} J</div>
            </div>
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);">
                <h6 style="margin: 0 0 0.5rem 0; opacity: 0.9; font-size: 0.875rem;">Pmax</h6>
                <div style="font-size: 2rem; font-weight: 700;">${result.Pmax} W</div>
            </div>
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(250, 112, 154, 0.3);">
                <h6 style="margin: 0 0 0.5rem 0; opacity: 0.9; font-size: 0.875rem;">A (Fatigue Parameter)</h6>
                <div style="font-size: 2rem; font-weight: 700;">${result.A}</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">RMSE</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: #667eea;">${result.RMSE} W</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">99% W'eff at</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: #667eea;">${formatTimeLabel(result.t_99)}</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">Punti usati</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: #667eea;">${filtered.selectedCount} / ${filtered.totalCount}</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">P @ 5min</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: #667eea;">${Math.round(ompd_power(300, result.CP, result.W_prime, result.Pmax, result.A))} W</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">P @ 20min</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: #667eea;">${Math.round(ompd_power(1200, result.CP, result.W_prime, result.Pmax, result.A))} W</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">P @ 30min</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: #667eea;">${Math.round(ompd_power(1800, result.CP, result.W_prime, result.Pmax, result.A))} W</div>
            </div>
        </div>
    `;
    
    document.getElementById('cp-results-stats').innerHTML = statsHtml;
}

// Recalculate CP when filters change
window.recalculateCP = function() {
    const valuesPerWindow = parseInt(document.getElementById('cp-values-per-window').value) || 1;
    const minPercentile = parseInt(document.getElementById('cp-min-percentile').value) || 90;
    const sprintSeconds = parseInt(document.getElementById('cp-sprint-seconds').value) || 10;
    const useLongPointFallback = document.getElementById('cp-use-long-point-fallback').checked ? 1 : 0;

    // Get current period data
    const period = window.cpCurrentPeriod;
    const data = window.cpDataRaw[period];
    
    if (!data) {
        showToast('Dati non disponibili per questo periodo', 'warning');
        return;
    }

    // Data format is {secs: [], watts: []}
    const allTimes = data.secs || [];
    const allPowers = data.watts || [];

    calculateAndRenderCP(allTimes, allPowers, valuesPerWindow, minPercentile, sprintSeconds, useLongPointFallback);
};

// Switch CP period
window.switchCPPeriod = async function(period) {
    window.cpCurrentPeriod = period;

    // Check if data already loaded
    if (window.cpDataRaw[period]) {
        window.recalculateCP();
        return;
    }

    // Load data for this period
    showLoading();
    try {
        const athleteId = window.cpCurrentAthleteId;
        let url;

        if (period === '90d') {
            const today = new Date();
            const days90ago = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
            const dateStr90 = days90ago.toISOString().split('T')[0];
            const todayStr = today.toISOString().split('T')[0];
            url = `/api/athletes/${athleteId}/power-curve?oldest=${dateStr90}&newest=${todayStr}`;
        } else if (period.startsWith('season-')) {
            const seasonId = parseInt(period.replace('season-', ''));
            const season = window.cpSeasons.find(s => s.id === seasonId);
            if (!season) throw new Error('Stagione non trovata');
            
            const today = new Date().toISOString().split('T')[0];
            const endDate = season.end_date || today;
            url = `/api/athletes/${athleteId}/power-curve?oldest=${season.start_date}&newest=${endDate}`;
        }

        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        // API returns {secs: [], watts: []}
        window.cpDataRaw[period] = data;

        window.recalculateCP();
        showToast('Dati caricati con successo', 'success');
    } catch (error) {
        console.error('Error loading CP period data:', error);
        showToast('Errore nel caricamento dei dati: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

// ========== SEASONS TAB ==========

async function renderSeasonsTab(athleteId, tabContent) {
    // Show loading
    tabContent.innerHTML = `
        <div style="padding: 2rem; text-align: center;">
            <div class="spinner" style="margin: 2rem auto;"></div>
            <p style="color: #666; margin-top: 1rem;">Caricamento stagioni...</p>
        </div>
    `;

    try {
        const seasons = await api.getAthleteSeasons(athleteId);
        
        // Check if this tab is still active - prevent race condition
        if (window.currentAthleteActiveTab !== 'seasons') {
            return;
        }
        
        tabContent.innerHTML = `
            <div style="padding: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
                    <h4 style="margin: 0;">📅 Stagioni Sportive</h4>
                    <button class="btn btn-primary" onclick="showCreateSeasonDialog(${athleteId})">
                        <i class="bi bi-plus"></i> Nuova Stagione
                    </button>
                </div>
                
                ${seasons.length === 0 ? `
                    <div style="padding: 3rem; text-align: center; background: #f9fafb; border-radius: 8px; border: 2px dashed #ddd;">
                        <p style="font-size: 2rem; margin: 0;">📅</p>
                        <h5 style="margin: 1rem 0 0.5rem 0; color: #666;">Nessuna stagione configurata</h5>
                        <p style="color: #999; margin: 0;">Crea la prima stagione per organizzare i dati dell'atleta</p>
                        <button class="btn btn-primary" onclick="showCreateSeasonDialog(${athleteId})" style="margin-top: 1rem;">
                            Crea Stagione
                        </button>
                    </div>
                ` : `
                    <div style="display: grid; gap: 1rem;">
                        ${seasons.map(season => `
                            <div style="padding: 1.5rem; background: white; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div style="flex: 1;">
                                        <h5 style="margin: 0 0 0.5rem 0; color: #1f2937; font-size: 1.1rem;">${season.name}</h5>
                                        <div style="display: flex; gap: 2rem; color: #6b7280; font-size: 0.95rem;">
                                            <div>
                                                <strong>Inizio:</strong> ${formatItalianDate(season.start_date)}
                                            </div>
                                            <div>
                                                <strong>Fine:</strong> ${season.end_date ? formatItalianDate(season.end_date) : '<em>In corso</em>'}
                                            </div>
                                        </div>
                                    </div>
                                    <div style="display: flex; gap: 0.5rem;">
                                        <button class="btn btn-secondary btn-sm" onclick="editSeason(${season.id}, '${season.name}', '${season.start_date}')" title="Modifica">
                                            <i class="bi bi-pencil"></i>
                                        </button>
                                        <button class="btn btn-danger btn-sm" onclick="deleteSeason(${season.id}, ${athleteId})" title="Elimina">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `}
            </div>
        `;
    } catch (error) {
        console.error('Error loading seasons:', error);
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <div style="background: #fee; padding: 1.5rem; border-radius: 8px; border: 1px solid #fcc;">
                    <i class="bi bi-x-circle" style="font-size: 2rem; color: #d32f2f;"></i>
                    <h4 style="margin-top: 1rem; color: #c62828;">Errore nel caricamento</h4>
                    <p style="color: #666; margin-top: 0.5rem;">Non è stato possibile caricare le stagioni: ${error.message}</p>
                </div>
            </div>
        `;
    }
}

window.showCreateSeasonDialog = function(athleteId) {
    createModal(
        'Crea Nuova Stagione',
        `
        <div style="padding: 0.5rem 0;">
            <div class="form-group" style="margin-bottom: 1rem;">
                <label class="form-label">Nome Stagione</label>
                <input type="text" id="season-name-input" class="form-input" placeholder="es. Stagione 2025-2026" style="width: 100%;">
                <small style="color: #666; margin-top: 0.5rem; display: block;">
                    Il nome identifica la stagione (es. "Stagione 2025-2026", "Preparazione Olimpica 2026")
                </small>
            </div>
            
            <div class="form-group" style="margin-bottom: 1rem;">
                <label class="form-label">Data Inizio</label>
                <input type="date" id="season-start-date-input" class="form-input" style="width: 100%;">
                <small style="color: #666; margin-top: 0.5rem; display: block;">
                    La fine sarà automaticamente l'inizio della stagione successiva
                </small>
            </div>
            
            <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
                <button class="btn btn-primary" onclick="createSeason(${athleteId})">
                    💾 Crea Stagione
                </button>
                <button class="btn btn-secondary" onclick="closeModal()">
                    Annulla
                </button>
            </div>
        </div>
        `
    );
};

window.createSeason = async function(athleteId) {
    const name = document.getElementById('season-name-input').value.trim();
    const startDate = document.getElementById('season-start-date-input').value;
    
    if (!name) {
        alert('Inserisci un nome per la stagione');
        return;
    }
    
    if (!startDate) {
        alert('Seleziona una data di inizio');
        return;
    }
    
    try {
        showLoading();
        await api.createSeason(athleteId, { name, start_date: startDate });
        
        closeModal();
        showToast('Stagione creata con successo', 'success');
        
        // Reload seasons tab
        const tabContent = document.getElementById('athlete-tab-content');
        await renderSeasonsTab(athleteId, tabContent);
    } catch (error) {
        showToast('Errore creazione stagione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.editSeason = function(seasonId, currentName, currentStartDate) {
    createModal(
        'Modifica Stagione',
        `
        <div style="padding: 0.5rem 0;">
            <div class="form-group" style="margin-bottom: 1rem;">
                <label class="form-label">Nome Stagione</label>
                <input type="text" id="season-name-edit-input" class="form-input" value="${currentName}" style="width: 100%;">
            </div>
            
            <div class="form-group" style="margin-bottom: 1rem;">
                <label class="form-label">Data Inizio</label>
                <input type="date" id="season-start-date-edit-input" class="form-input" value="${currentStartDate}" style="width: 100%;">
            </div>
            
            <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
                <button class="btn btn-primary" onclick="updateSeasonData(${seasonId})">
                    💾 Salva
                </button>
                <button class="btn btn-secondary" onclick="closeModal()">
                    Annulla
                </button>
            </div>
        </div>
        `
    );
};

window.updateSeasonData = async function(seasonId) {
    const name = document.getElementById('season-name-edit-input').value.trim();
    const startDate = document.getElementById('season-start-date-edit-input').value;
    
    if (!name || !startDate) {
        alert('Compila tutti i campi');
        return;
    }
    
    try {
        showLoading();
        await api.updateSeason(seasonId, { name, start_date: startDate });
        
        closeModal();
        showToast('Stagione aggiornata', 'success');
        
        // Reload seasons tab
        const athleteId = window.currentAthleteView;
        const tabContent = document.getElementById('athlete-tab-content');
        await renderSeasonsTab(athleteId, tabContent);
    } catch (error) {
        showToast('Errore aggiornamento: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.deleteSeason = async function(seasonId, athleteId) {
    if (!confirm('Sei sicuro di voler eliminare questa stagione?')) {
        return;
    }
    
    try {
        showLoading();
        await api.deleteSeason(seasonId);
        showToast('Stagione eliminata', 'success');
        
        // Reload seasons tab
        const tabContent = document.getElementById('athlete-tab-content');
        await renderSeasonsTab(athleteId, tabContent);
    } catch (error) {
        showToast('Errore eliminazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

function renderPowerCurveChart(data) {
    // Transform data for ApexCharts
    const durations = data.secs || [];
    const watts = data.watts || [];

    if (!durations || durations.length === 0) {
        document.getElementById('power-curve-chart').innerHTML = 
            '<p style="color: #666; text-align: center; padding: 2rem;">Nessun dato disponibile</p>';
        return;
    }

    // Store raw data globally for later use
    window.currentPowerCurveData = { secs: durations, watts: watts };

    // Calculate actual min/max from data for adaptive scale
    const minDuration = Math.min(...durations.filter(d => d > 0));
    const maxDuration = Math.max(...durations.filter(d => d > 0));
    
    // Minimal padding for cleaner view - no wasted space
    const logMin = Math.log10(minDuration * 0.95);
    const logMax = Math.log10(maxDuration * 1.05);

    // Transform to logarithmic scale for X axis
    const seriesData = durations.map((sec, idx) => ({
        x: Math.log10(Math.max(sec, 1)),
        y: watts[idx] || 0,
        rawX: sec
    }));

    // ApexCharts configuration with adaptive logarithmic X axis
    const options = {
        series: [{
            name: 'Potenza (W)',
            data: seriesData
        }],
        chart: {
            type: 'line',
            height: 500,
            toolbar: {
                show: true,
                tools: {
                    download: true,
                    zoom: true,
                    zoomin: true,
                    zoomout: true,
                    pan: true,
                    reset: true
                }
            },
            zoom: {
                enabled: true,
                type: 'xy'
            }
        },
        stroke: {
            curve: 'smooth',
            width: 3
        },
        colors: ['#3b82f6'],
        xaxis: {
            type: 'numeric',
            title: {
                text: 'Durata (scala logaritmica)',
                style: {
                    fontSize: '14px',
                    fontWeight: 600
                }
            },
            labels: {
                formatter: function(value) {
                    const sec = Math.pow(10, value);
                    if (sec < 60) return Math.round(sec) + 's';
                    if (sec < 3600) return Math.round(sec / 60) + 'm';
                    if (sec < 86400) return (sec / 3600).toFixed(1) + 'h';
                    return (sec / 86400).toFixed(1) + 'd';
                }
            },
            min: logMin,
            max: logMax
        },
        yaxis: {
            title: {
                text: 'Potenza (W)',
                style: {
                    fontSize: '14px',
                    fontWeight: 600
                }
            },
            labels: {
                formatter: function(value) {
                    return Math.round(value) + 'W';
                }
            }
        },
        tooltip: {
            shared: true,
            intersect: false,
            x: {
                formatter: function(value) {
                    const sec = Math.pow(10, value);
                    if (sec < 60) return Math.round(sec) + ' sec';
                    if (sec < 3600) {
                        let mins = Math.floor(sec / 60);
                        let secs = Math.round(sec % 60);
                        if (secs === 60) { mins += 1; secs = 0; }
                        return mins + 'm ' + secs + 's';
                    }
                    if (sec < 86400) {
                        let hours = Math.floor(sec / 3600);
                        let mins = Math.round((sec % 3600) / 60);
                        if (mins === 60) { hours += 1; mins = 0; }
                        return hours + 'h ' + mins + 'm';
                    }
                    let days = Math.floor(sec / 86400);
                    let hours = Math.round((sec % 86400) / 3600);
                    if (hours === 24) { days += 1; hours = 0; }
                    return days + 'd ' + hours + 'h';
                }
            },
            y: {
                formatter: function(value) {
                    return Math.round(value) + ' W';
                }
            }
        },
        grid: {
            borderColor: '#e0e0e0',
            strokeDashArray: 4
        },
        markers: {
            size: 0,
            hover: {
                size: 6
            }
        }
    };

    // Render chart
    if (window.currentPowerCurveChart) {
        window.currentPowerCurveChart.destroy();
    }
    const chart = new ApexCharts(document.querySelector("#power-curve-chart"), options);
    chart.render();
    window.currentPowerCurveChart = chart;

    // Render best efforts table
    renderBestEffortsTable(data);
}

function renderBestEffortsTable(data) {
    const durations = data.secs || [];
    const watts = data.watts || [];

    // Initialize custom durations list if doesn't exist - include longer efforts
    if (!window.customDurations) {
        window.customDurations = [1,2,5,8,10,15,20,30,40,50,60,120,180,240,300,360,480,570,720,900,960,1200,1500,1800,2400,2700,3600,5400,7200];
    }

    const tableData = window.customDurations
        .map(duration => {
            const index = durations.findIndex(d => d >= duration);
            if (index === -1) return null;
            
            return {
                duration: duration,
                watts: watts[index] || 0,
                label: formatDurationLabel(duration)
            };
        })
        .filter(item => item !== null);

    if (tableData.length === 0) {
        document.getElementById('best-efforts-table').innerHTML = 
            '<p style="color: #666; text-align: center;">Nessun dato disponibile</p>';
        return;
    }

    let html = `
        <div style="margin-bottom: 0.75rem;">
            <input type="number" id="custom-duration-input" placeholder="Aggiungi durata (sec)" 
                   style="padding: 0.35rem 0.5rem; font-size: 0.85rem; border: 1px solid #ddd; border-radius: 4px; width: 150px;">
            <button class="btn btn-primary btn-sm" onclick="addCustomDuration()" style="margin-left: 0.35rem; padding: 0.35rem 0.75rem; font-size: 0.8rem;">
                <i class="bi bi-plus"></i> Aggiungi
            </button>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
            <thead>
                <tr>
                    <th style="text-align: left; padding: 0.5rem; border-bottom: 1px solid #ddd; font-weight: 600; font-size: 0.8rem;">Durata</th>
                    <th style="text-align: right; padding: 0.5rem; border-bottom: 1px solid #ddd; font-weight: 600; font-size: 0.8rem;">Potenza</th>
                    <th style="text-align: center; padding: 0.5rem; border-bottom: 1px solid #ddd; width: 35px;"></th>
                </tr>
            </thead>
            <tbody>
    `;

    tableData.forEach(item => {
        html += `
            <tr style="border-bottom: 1px solid #f0f0f0;">
                <td style="padding: 0.4rem 0.5rem; font-weight: 500; font-size: 0.85rem;">${item.label}</td>
                <td style="padding: 0.4rem 0.5rem; text-align: right; color: #3b82f6; font-weight: 600; font-size: 0.85rem;">
                    ${Math.round(item.watts)} W
                </td>
                <td style="text-align: center; padding: 0.4rem 0.5rem;">
                    <button class="btn btn-danger btn-xs" onclick="removeDuration(${item.duration})" 
                            style="padding: 2px 5px; font-size: 0.7rem; background: #f5101f; color: white; border: none; border-radius: 3px; cursor: pointer;">
                        ×
                    </button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    document.getElementById('best-efforts-table').innerHTML = html;
}

window.addCustomDuration = function() {
    const input = document.getElementById('custom-duration-input');
    const durationStr = input.value.trim();
    
    if (!durationStr || isNaN(durationStr)) {
        alert('Inserisci un numero valido di secondi');
        return;
    }
    
    const duration = parseInt(durationStr);
    if (duration <= 0) {
        alert('La durata deve essere > 0 secondi');
        return;
    }
    
    if (!window.customDurations) {
        window.customDurations = [];
    }
    
    // Aggiungi se non esiste già
    if (!window.customDurations.includes(duration)) {
        window.customDurations.push(duration);
        window.customDurations.sort((a, b) => a - b);
        
        // Rifresha tabella
        renderBestEffortsTable(window.currentPowerCurveData);
        input.value = '';
    } else {
        alert('Questa durata è già presente');
    }
};

window.removeDuration = function(duration) {
    if (!window.customDurations) {
        window.customDurations = [];
    }
    
    const index = window.customDurations.indexOf(duration);
    if (index > -1) {
        window.customDurations.splice(index, 1);
        renderBestEffortsTable(window.currentPowerCurveData);
    }
};

function formatDurationLabel(seconds) {
    if (seconds < 60) return seconds + ' sec';
    if (seconds < 3600) return Math.round(seconds / 60) + ' min';
    if (seconds < 86400) return (seconds / 3600).toFixed(1).replace('.0', '') + 'h';
    return (seconds / 86400).toFixed(1) + ' giorni';
}

window.refreshPowerCurve = async function(athleteId) {
    const athlete = window.allAthletes.find(a => a.id === athleteId);
    const tabContent = document.getElementById('athlete-tab-content');
    await renderPowerCurveTab(athleteId, athlete, tabContent);
};

window.switchPowerCurvePeriod = function(period) {
    window.selectedPeriod = period;
    
    // Use the appropriate dataset
    let data;
    if (period === '90d') {
        data = window.powerCurve90d;
    } else if (period.startsWith('season-')) {
        const seasonId = parseInt(period.replace('season-', ''));
        data = window.powerCurveSeasons[seasonId];
    } else {
        data = window.powerCurveAllTime;
    }
    
    if (!data) {
        console.error('Power curve data not available for period:', period);
        showToast('Dati non disponibili per questo periodo', 'warning');
        return;
    }
    
    // Re-render chart and table with selected period
    renderPowerCurveChart(data);
};

window.showCustomPeriodPicker = function(athleteId) {
    createModal(
        '📅 Seleziona Periodo Custom',
        `
        <div style="padding: 1.5rem;">
            <div style="margin-bottom: 1.5rem;">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Data inizio:</label>
                <input type="date" id="custom-period-start" style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="margin-bottom: 1.5rem;">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Data fine:</label>
                <input type="date" id="custom-period-end" style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="display: flex; gap: 1rem;">
                <button class="btn btn-primary" onclick="loadCustomPeriod(${athleteId})">
                    Carica dati
                </button>
                <button class="btn btn-secondary" onclick="closeModal()">
                    Annulla
                </button>
            </div>
        </div>
        `
    );

    // Set default dates (today and 6 months ago)
    const today = new Date();
    const sixMonthsAgo = new Date(today.getTime() - 180 * 24 * 60 * 60 * 1000);
    
    document.getElementById('custom-period-end').value = today.toISOString().split('T')[0];
    document.getElementById('custom-period-start').value = sixMonthsAgo.toISOString().split('T')[0];
};

window.loadCustomPeriod = async function(athleteId) {
    const startDate = document.getElementById('custom-period-start').value;
    const endDate = document.getElementById('custom-period-end').value;
    
    if (!startDate || !endDate) {
        alert('Seleziona entrambe le date');
        return;
    }
    
    if (startDate >= endDate) {
        alert('Data inizio deve essere prima di data fine');
        return;
    }
    
    closeModal();
    
    const tabContent = document.getElementById('athlete-tab-content');
    tabContent.innerHTML = `
        <div style="padding: 2rem; text-align: center;">
            <div class="spinner" style="margin: 2rem auto;"></div>
            <p style="color: #666; margin-top: 1rem;">Caricamento power curve custom...</p>
        </div>
    `;
    
    try {
        const response = await fetch(
            `/api/athletes/${athleteId}/power-curve?oldest=${startDate}&newest=${endDate}`
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const customData = await response.json();
        
        // Store custom data
        window.powerCurveCustom = customData;
        window.selectedPeriod = 'custom';
        window.customPeriodStart = startDate;
        window.customPeriodEnd = endDate;
        
        // Re-render the tab
        const athlete = window.allAthletes.find(a => a.id === athleteId);
        await renderPowerCurveTab(athleteId, athlete, tabContent);
        
        // Switch to custom period and render chart
        renderPowerCurveChart(customData);
        
        showToast(`Caricati dati dal ${formatItalianDate(startDate)} al ${formatItalianDate(endDate)}`, 'success');
        
    } catch (error) {
        console.error('Error loading custom period:', error);
        showToast('Errore caricamento periodo custom', 'error');
        // Reload the original view
        const athlete = window.allAthletes.find(a => a.id === athleteId);
        await renderPowerCurveTab(athleteId, athlete, tabContent);
    }
};

function formatItalianDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('it-IT', { year: 'numeric', month: 'long', day: 'numeric' });
}

window.showCreateAthleteDialog = function() {
    const teamsOptions = window.availableTeams.map(t => 
        `<option value="${t.id}">${t.name}</option>`
    ).join('');
    const categoriesOptions = (window.availableCategories || []).map(c => 
        `<option value="${c.id}">${c.name}</option>`
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
        <div class="form-group">
            <label class="form-label">Categoria</label>
            <select id="athlete-category" class="form-input">
                <option value="">Nessuna categoria</option>
                ${categoriesOptions}
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">kJ/h/kg (default)</label>
            <input type="number" id="athlete-kj-per-hour-per-kg" class="form-input" value="10.0" step="0.1" min="0.5" max="50">
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
        category_id: document.getElementById('athlete-category').value ? parseInt(document.getElementById('athlete-category').value) : null,
        kj_per_hour_per_kg: parseFloat(document.getElementById('athlete-kj-per-hour-per-kg').value) || 10.0,
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

window.saveAthleteDetails = async function(athleteId) {
    try {
        showLoading();
        
        // Raccogliere i dati dal form
        const teamId = document.getElementById('detail-team').value.trim();
        const categoryId = document.getElementById('detail-category').value.trim();
        const gender = document.getElementById('detail-gender').value;
        const weightKg = parseFloat(document.getElementById('detail-weight').value) || null;
        const heightCm = parseFloat(document.getElementById('detail-height').value) || null;
        const cp = parseInt(document.getElementById('detail-cp').value) || null;
        const wPrime = parseInt(document.getElementById('detail-wprime').value) || null;
        const kjPerHourPerKg = parseFloat(document.getElementById('detail-kj-per-kg').value) || null;
        const birthDate = document.getElementById('detail-birth-date').value;
        
        // Inviare al backend
        const response = await fetch(`/api/athletes/${athleteId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                team_id: teamId ? parseInt(teamId) : null,
                category_id: categoryId ? parseInt(categoryId) : null,
                gender: gender || null,
                weight_kg: weightKg,
                height_cm: heightCm,
                cp: cp,
                w_prime: wPrime,
                kj_per_hour_per_kg: kjPerHourPerKg,
                birth_date: birthDate || null
            })
        });
        
        if (!response.ok) throw new Error('Errore durante il salvataggio');
        
        // Aggiornare la lista degli atleti
        const updated = await response.json();
        const idx = window.allAthletes.findIndex(a => a.id === athleteId);
        if (idx >= 0) {
            window.allAthletes[idx] = { ...window.allAthletes[idx], ...updated };
        }
        
        showToast('Dettagli atleta salvati con successo', 'success');
        // Ricaricare la tab per mostrare i nuovi dati
        switchAthleteTab('details');
    } catch (error) {
        showToast('Errore nel salvataggio: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.editAthlete = async function(athleteId) {
    try {
        const athlete = await api.getAthlete(athleteId);
        
        const teamsOptions = window.availableTeams.map(t => 
            `<option value="${t.id}" ${athlete.team_id === t.id ? 'selected' : ''}>${t.name}</option>`
        ).join('');
        const categoriesOptions = (window.availableCategories || []).map(c => 
            `<option value="${c.id}" ${athlete.category_id === c.id ? 'selected' : ''}>${c.name}</option>`
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
            <div class="form-group">
                <label class="form-label">Categoria</label>
                <select id="athlete-category-edit" class="form-input">
                    <option value="">Nessuna categoria</option>
                    ${categoriesOptions}
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">kJ/h/kg (default)</label>
                <input type="number" id="athlete-kj-per-hour-per-kg-edit" class="form-input" value="${athlete.kj_per_hour_per_kg || 10.0}" step="0.1" min="0.5" max="50">
            </div>
            <div style="border-top: 2px solid #e0e0e0; margin-top: 1rem; padding-top: 1rem; margin-bottom: 1rem;">
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
        category_id: document.getElementById('athlete-category-edit').value ? parseInt(document.getElementById('athlete-category-edit').value) : null,
        kj_per_hour_per_kg: parseFloat(document.getElementById('athlete-kj-per-hour-per-kg-edit').value) || 10.0,
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

// ========== CP CHARTS ==========

/**
 * Create the 3 ECharts for CP model visualization
 */
function createCPCharts(allTimes, allPowers, selectedTimes, selectedPowers, result) {
    // Chart 1: Power-Duration Curve
    createCPPowerDurationChart(allTimes, allPowers, selectedTimes, selectedPowers, result);
    
    // Chart 2: Residuals
    createCPResidualsChart(selectedTimes, result.residuals);
    
    // Chart 3: W'eff
    createCPWeffChart(result.W_prime, result.CP, result.Pmax);
}

/**
 * Chart 1: Power-Duration Curve with fitted model
 */
function createCPPowerDurationChart(allTimes, allPowers, timeValues, powerValues, result) {
    const chartDom = document.getElementById('cp-chart-1');
    if (!chartDom) return;
    
    if (window.cpChart1) {
        window.cpChart1.dispose();
    }
    window.cpChart1 = echarts.init(chartDom);

    // Generate fitted curve (log distributed points)
    const minTime = 1;
    const maxTime = 7200;
    const numPoints = 300;
    const logMin = Math.log10(minTime);
    const logMax = Math.log10(maxTime);
    const fittedData = [];
    
    for (let i = 0; i <= numPoints; i++) {
        const logT = logMin + (i / numPoints) * (logMax - logMin);
        const t = Math.pow(10, logT);
        const p = ompd_power(t, result.CP, result.W_prime, result.Pmax, result.A);
        fittedData.push([t, p]);
    }

    const scatterData = timeValues.map((t, i) => [t, powerValues[i]]);
    const realPowerCurveData = allTimes.map((t, i) => [t, allPowers[i]]);

    const option = {
        title: {
            text: 'OmniPD Power-Duration Curve',
            left: 'center',
            textStyle: {
                color: '#667eea',
                fontSize: 20,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#667eea',
            borderWidth: 2,
            axisPointer: {
                type: 'line',
                axis: 'x',
                snap: false,
                label: { show: false },
                lineStyle: {
                    type: 'dashed',
                    color: '#aaa',
                    width: 1
                }
            },
            formatter: function(params) {
                // Find hovered time (x value)
                let hoveredTime = params[0].value[0];
                // Find fitted curve value at this time
                let fitted = null;
                let real = null;
                let selected = null;
                params.forEach(param => {
                    if (param.seriesName === 'Fitted Curve') fitted = param;
                    if (param.seriesName === 'Real Power Curve') real = param;
                    if (param.seriesName === 'Selected Data') selected = param;
                });
                // If not present in params, interpolate fitted and real
                if (!fitted) {
                    // Interpolate fitted curve
                    let fitVal = null;
                    for (let i = 1; i < fittedData.length; ++i) {
                        if (fittedData[i][0] >= hoveredTime) {
                            let t0 = fittedData[i-1][0], t1 = fittedData[i][0];
                            let p0 = fittedData[i-1][1], p1 = fittedData[i][1];
                            fitVal = p0 + (p1-p0)*(hoveredTime-t0)/(t1-t0);
                            break;
                        }
                    }
                    fitted = { marker: '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background:#667eea;"></span>', seriesName: 'Fitted Curve', value: [hoveredTime, fitVal] };
                }
                if (!real) {
                    // Interpolate real curve
                    let realVal = null;
                    for (let i = 1; i < realPowerCurveData.length; ++i) {
                        if (realPowerCurveData[i][0] >= hoveredTime) {
                            let t0 = realPowerCurveData[i-1][0], t1 = realPowerCurveData[i][0];
                            let p0 = realPowerCurveData[i-1][1], p1 = realPowerCurveData[i][1];
                            realVal = p0 + (p1-p0)*(hoveredTime-t0)/(t1-t0);
                            break;
                        }
                    }
                    real = { marker: '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background:#505050;"></span>', seriesName: 'Real Power Curve', value: [hoveredTime, realVal] };
                }
                let resultStr = `<strong>Time: ${formatTimeLabel(hoveredTime)}</strong><br/>`;
                if (fitted) resultStr += `${fitted.marker} ${fitted.seriesName}: ${Math.round(fitted.value[1])} W<br/>`;
                if (real) resultStr += `${real.marker} ${real.seriesName}: ${Math.round(real.value[1])} W<br/>`;
                if (selected) resultStr += `${selected.marker} ${selected.seriesName}: ${Math.round(selected.value[1])} W<br/>`;
                return resultStr;
            }
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: '12%',
            containLabel: true
        },
        xAxis: {
            type: 'log',
            name: 'Time',
            nameLocation: 'middle',
            nameGap: 40,
            min: 1,
            max: 7200,
            nameTextStyle: {
                color: '#667eea',
                fontSize: 14,
                fontWeight: 'bold'
            },
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            },
            splitLine: {
                lineStyle: {
                    color: 'rgba(102, 126, 234, 0.1)'
                }
            },
            axisLabel: {
                formatter: function(value) {
                    const logVal = Math.log10(value);
                    if (Math.abs(logVal - Math.round(logVal)) < 0.1) {
                        return formatTimeLabel(value);
                    }
                    return '';
                },
                color: '#666'
            }
        },
        yAxis: {
            type: 'value',
            name: 'Power (W)',
            nameLocation: 'middle',
            nameGap: 50,
            nameTextStyle: {
                color: '#667eea',
                fontSize: 14,
                fontWeight: 'bold'
            },
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            },
            splitLine: {
                lineStyle: {
                    color: 'rgba(102, 126, 234, 0.1)'
                }
            },
            axisLabel: {
                color: '#666'
            }
        },
        series: [
            {
                name: 'Real Power Curve',
                type: 'scatter',
                data: realPowerCurveData,
                symbolSize: 4,
                itemStyle: {
                    color: 'rgba(80, 80, 80, 0.45)',
                    borderColor: 'rgba(60, 60, 60, 0.25)',
                    borderWidth: 0
                },
                z: 0
            },
            {
                name: 'Fitted Curve',
                type: 'line',
                data: fittedData,
                smooth: false,
                lineStyle: {
                    color: '#667eea',
                    width: 3
                },
                showSymbol: false,
                z: 10
            },
            {
                name: 'Selected Data',
                type: 'scatter',
                data: scatterData,
                symbolSize: 10,
                itemStyle: {
                    color: '#f093fb',
                    borderColor: '#764ba2',
                    borderWidth: 2
                },
                z: 20
            }
        ],
        animationDuration: 1200,
        animationEasing: 'elasticOut'
    };

    window.cpChart1.setOption(option);
    window.addEventListener('resize', () => window.cpChart1.resize());
}

/**
 * Chart 2: Residuals (errors between data and model)
 */
function createCPResidualsChart(timeValues, residuals) {
    const chartDom = document.getElementById('cp-chart-2');
    if (!chartDom) return;
    
    if (window.cpChart2) {
        window.cpChart2.dispose();
    }
    window.cpChart2 = echarts.init(chartDom);

    const residualData = timeValues.map((t, i) => [t, residuals[i]]);

    const option = {
        title: {
            text: 'Residuals',
            left: 'center',
            textStyle: {
                color: '#667eea',
                fontSize: 18,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#f06447',
            borderWidth: 2,
            formatter: function(params) {
                return `<strong>Time: ${formatTimeLabel(params[0].value[0])}</strong><br/>Residual: ${params[0].value[1].toFixed(2)} W`;
            }
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'log',
            name: 'Time',
            nameLocation: 'middle',
            nameGap: 35,
            min: 1,
            max: Math.max(...timeValues) * 1.1,
            nameTextStyle: {
                color: '#667eea',
                fontSize: 12,
                fontWeight: 'bold'
            },
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            },
            splitLine: {
                lineStyle: {
                    color: 'rgba(102, 126, 234, 0.1)'
                }
            },
            axisLabel: {
                formatter: function(value) {
                    return formatTimeLabel(value);
                },
                color: '#666'
            }
        },
        yAxis: {
            type: 'value',
            name: 'Residual (W)',
            nameLocation: 'middle',
            nameGap: 45,
            nameTextStyle: {
                color: '#f06447',
                fontSize: 12,
                fontWeight: 'bold'
            },
            axisLine: {
                lineStyle: {
                    color: '#f06447'
                }
            },
            splitLine: {
                lineStyle: {
                    color: 'rgba(240, 100, 71, 0.1)'
                }
            },
            axisLabel: {
                color: '#666'
            }
        },
        series: [
            {
                name: 'Residual',
                type: 'line',
                data: residualData,
                symbol: 'circle',
                symbolSize: 8,
                lineStyle: {
                    color: '#f06447',
                    width: 2
                },
                itemStyle: {
                    color: '#f06447',
                    borderWidth: 2
                },
                smooth: true
            }
        ],
        animationDuration: 1000,
        animationEasing: 'cubicOut'
    };

    window.cpChart2.setOption(option);
    window.addEventListener('resize', () => window.cpChart2.resize());
}

/**
 * Chart 3: W'eff (Effective W' recovery over time)
 */
function createCPWeffChart(W_prime, CP, Pmax) {
    const chartDom = document.getElementById('cp-chart-3');
    if (!chartDom) return;
    
    if (window.cpChart3) {
        window.cpChart3.dispose();
    }
    window.cpChart3 = echarts.init(chartDom);

    // Calculate W'eff curve
    const T_weff = Array.from({length: 500}, (_, i) => 1 + i * (300 - 1) / 499);
    const Weff_plot = T_weff.map(t => w_eff(t, W_prime, CP, Pmax));
    const weffData = T_weff.map((t, i) => [t, Weff_plot[i]]);

    // Find t_99
    const W_99 = 0.99 * W_prime;
    const t_99_idx = Weff_plot.reduce((minIdx, val, idx, arr) => 
        Math.abs(val - W_99) < Math.abs(arr[minIdx] - W_99) ? idx : minIdx, 0);
    const t_99 = T_weff[t_99_idx];

    const option = {
        title: {
            text: "Effective W' Recovery",
            left: 'center',
            textStyle: {
                color: '#667eea',
                fontSize: 18,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#667eea',
            borderWidth: 2,
            formatter: function(params) {
                return `<strong>Time: ${formatTimeLabel(params[0].value[0])}</strong><br/>W'eff: ${Math.round(params[0].value[1])} J`;
            }
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'log',
            name: 'Time',
            nameLocation: 'middle',
            nameGap: 35,
            min: 1,
            max: 300,
            nameTextStyle: {
                color: '#667eea',
                fontSize: 12,
                fontWeight: 'bold'
            },
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            },
            splitLine: {
                lineStyle: {
                    color: 'rgba(102, 126, 234, 0.1)'
                }
            },
            axisLabel: {
                formatter: function(value) {
                    return formatTimeLabel(value);
                },
                color: '#666'
            }
        },
        yAxis: {
            type: 'value',
            name: "W'eff (J)",
            nameLocation: 'middle',
            nameGap: 45,
            nameTextStyle: {
                color: '#52c787',
                fontSize: 12,
                fontWeight: 'bold'
            },
            axisLine: {
                lineStyle: {
                    color: '#52c787'
                }
            },
            splitLine: {
                lineStyle: {
                    color: 'rgba(82, 199, 135, 0.1)'
                }
            },
            axisLabel: {
                color: '#666'
            }
        },
        series: [
            {
                name: "W'eff",
                type: 'line',
                data: weffData,
                smooth: true,
                lineStyle: {
                    color: '#52c787',
                    width: 3
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            { offset: 0, color: 'rgba(82, 199, 135, 0.5)' },
                            { offset: 1, color: 'rgba(82, 199, 135, 0.05)' }
                        ]
                    }
                },
                showSymbol: false,
                markLine: {
                    silent: true,
                    symbol: ['none', 'none'],
                    label: {
                        show: true,
                        formatter: `99% at ${formatTimeLabel(t_99)}`,
                        color: '#333',
                        fontWeight: 'bold'
                    },
                    lineStyle: {
                        color: '#ff6b6b',
                        type: 'dashed',
                        width: 2
                    },
                    data: [{yAxis: W_99}]
                }
            }
        ],
        animationDuration: 1200,
        animationEasing: 'elasticOut'
    };

    window.cpChart3.setOption(option);
    window.addEventListener('resize', () => window.cpChart3.resize());
}
