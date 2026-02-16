/**
 * Teams Module - Frontend
 * Multi-team dashboard with team detail views
 */

// Global state
window.currentTeamView = null; // null = dashboard, number = team ID

window.renderTeamsPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    console.log('[TEAMS] renderTeamsPage started. currentTeamView:', window.currentTeamView);
    
    try {
        showLoading();
        const teams = await api.getTeams();
        
        console.log('[TEAMS] Loaded', teams.length, 'teams');
        
        // Store globally
        window.allTeams = teams;
        
        // Render based on current view
        if (window.currentTeamView === null) {
            console.log('[TEAMS] Rendering dashboard view');
            await renderTeamsDashboard(teams, contentArea);
        } else {
            console.log('[TEAMS] Rendering detail view for team', window.currentTeamView);
            renderTeamDetail(window.currentTeamView, teams, contentArea);
        }
        
    } catch (error) {
        console.error('[TEAMS] Error:', error);
        showToast('Errore nel caricamento delle squadre', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

async function renderTeamsDashboard(teams, contentArea) {
    contentArea.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 Dashboard Squadre</h3>
                <button class="btn btn-primary" onclick="showCreateTeamDialog()">
                    <i class="bi bi-plus"></i> Nuova Squadra
                </button>
            </div>
            <div class="card-body">
                <!-- Teams Grid -->
                <div id="teams-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem;">
                    ${teams.map(team => `<div id="team-card-${team.id}" class="team-card-placeholder">Caricamento...</div>`).join('')}
                </div>
            </div>
        </div>
    `;
    
    // Load member counts for each team
    for (const team of teams) {
        try {
            const athletes = await api.getAthletes(team.id);
            const cardHtml = createTeamCard(team, athletes.length);
            const placeholder = document.getElementById(`team-card-${team.id}`);
            if (placeholder) {
                placeholder.innerHTML = cardHtml;
            }
        } catch (err) {
            console.warn(`Failed to load member count for team ${team.id}:`, err);
        }
    }
}

function createTeamCard(team, memberCount = 0) {
    const initials = team.name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
    const colors = ['#667eea', '#f093fb', '#4facfe', '#fa709a', '#43e97b', '#38f9d7'];
    const colorIdx = team.id % colors.length;
    const bgColor = colors[colorIdx];
    
    return `
        <div onclick="showTeamDetail(${team.id})" style="
            cursor: pointer;
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border: 2px solid transparent;
        " onmouseover="this.style.boxShadow='0 4px 20px rgba(0,0,0,0.12)'; this.style.borderColor='${bgColor}';" onmouseout="this.style.boxShadow='0 2px 12px rgba(0,0,0,0.08)'; this.style.borderColor='transparent';">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="
                    width: 50px;
                    height: 50px;
                    border-radius: 10px;
                    background: linear-gradient(135deg, ${bgColor} 0%, ${bgColor}dd 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: 700;
                    font-size: 1.25rem;
                ">${initials}</div>
                <div>
                    <div style="font-weight: 600; color: #333; font-size: 1.1rem;">${team.name}</div>
                </div>
            </div>
            <div style="border-top: 1px solid #eee; padding-top: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.25rem;">Membri</div>
                        <div style="font-size: 1.75rem; font-weight: 700; color: ${bgColor};">${memberCount}</div>
                    </div>
                    <div style="font-size: 2rem; opacity: 0.2;">→</div>
                </div>
            </div>
        </div>
    `;
}

window.showTeamDetail = function(teamId) {
    console.log('[TEAMS] Switching to detail view for team', teamId);
    window.currentTeamView = teamId;
    window.renderTeamsPage();
};

window.backToTeamsDashboard = function() {
    console.log('[TEAMS] Switching back to dashboard');
    window.currentTeamView = null;
    window.renderTeamsPage();
};

async function renderTeamDetail(teamId, teams, contentArea) {
    const team = teams.find(t => t.id === teamId);
    if (!team) {
        showToast('Squadra non trovata', 'error');
        window.backToTeamsDashboard();
        return;
    }

    // Load team athletes
    const athletes = await api.getAthletes(teamId);
    
    contentArea.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <button class="btn btn-secondary" onclick="backToTeamsDashboard()">
                <i class="bi bi-arrow-left"></i> Dashboard
            </button>
        </div>
        
        <div class="card">
            <div class="card-header" style="background: white; border-left: 4px solid #667eea; display: flex; justify-content: space-between; align-items: center; padding-left: 1.5rem;">
                <div style="padding-left: 0.75rem;">
                    <h2 style="margin: 0; color: #333;">${team.name}</h2>
                    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;">${athletes.length} membri</p>
                </div>
                <button class="btn btn-primary" onclick="editTeam(${teamId})" style="margin-left: 1rem;">
                    <i class="bi bi-pencil"></i> Modifica Squadra
                </button>
            </div>
            
            <!-- Tabs -->
            <div class="tabs" style="border-bottom: 1px solid #ddd; background: #f8f9fa; display: flex; gap: 0;">
                <button class="tab-btn active" data-tab="overview" onclick="switchTeamTab('overview', ${teamId})">
                    📊 Overview
                </button>
                <button class="tab-btn" data-tab="members" onclick="switchTeamTab('members', ${teamId})">
                    👥 Membri
                </button>
                <button class="tab-btn" data-tab="rankings" onclick="switchTeamTab('rankings', ${teamId})">
                    🏆 Rankings
                </button>
                <button class="tab-btn" data-tab="comparison" onclick="switchTeamTab('comparison', ${teamId})">
                    📈 Comparazione
                </button>
            </div>
            
            <!-- Tab Content -->
            <div id="team-tab-content" class="card-body" style="min-height: 400px;">
                <!-- Content will be loaded here -->
            </div>
        </div>
    `;

    // Store team and athletes globally
    window.currentTeam = team;
    window.currentTeamAthletes = athletes;

    // Load default tab (overview)
    switchTeamTab('overview', teamId);
}

window.switchTeamTab = function(tabName, teamId) {
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });

    const tabContent = document.getElementById('team-tab-content');
    const team = window.currentTeam;
    const athletes = window.currentTeamAthletes;

    if (tabName === 'overview') {
        renderTeamOverviewTab(teamId, team, athletes, tabContent);
    } else if (tabName === 'members') {
        renderTeamMembersTab(teamId, team, athletes, tabContent);
    } else if (tabName === 'rankings') {
        renderTeamRankingsTab(teamId, team, athletes, tabContent);
    } else if (tabName === 'comparison') {
        renderTeamComparisonTab(teamId, team, athletes, tabContent);
    }
};

// ========== OVERVIEW TAB ==========

async function renderTeamOverviewTab(teamId, team, athletes, tabContent) {
    tabContent.innerHTML = `
        <div style="padding: 1.5rem;">
            <h4>📊 Statistiche Squadra</h4>
            <p style="color: #666;">Caricamento statistiche...</p>
        </div>
    `;

    // Calculate team statistics
    const stats = await calculateTeamStatistics(athletes);

    let html = `
        <div style="padding: 1.5rem;">
            <!-- Summary Cards -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                <div class="stat-card" style="background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%); border-left: 4px solid #667eea;">
                    <div class="stat-label">Totale Membri</div>
                    <div class="stat-value" style="color: #667eea;">${stats.totalMembers}</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #fff5f0 0%, #fff0f5 100%); border-left: 4px solid #ff6b6b;">
                    <div class="stat-label">CP Medio</div>
                    <div class="stat-value" style="color: #ff6b6b;">${stats.avgCP} W</div>
                    <div style="font-size: 0.875rem; color: #666; margin-top: 0.5rem;">${stats.avgCPkg} W/kg</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #f0fff5 0%, #f0f5ff 100%); border-left: 4px solid #43e97b;">
                    <div class="stat-label">W' Medio</div>
                    <div class="stat-value" style="color: #43e97b;">${stats.avgWPrime} J</div>
                    <div style="font-size: 0.875rem; color: #666; margin-top: 0.5rem;">${stats.avgWPrimeKg} kJ/kg</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #fffef0 0%, #fff5f0 100%); border-left: 4px solid #ffa502;">
                    <div class="stat-label">Peso Medio</div>
                    <div class="stat-value" style="color: #ffa502;">${stats.avgWeight} kg</div>
                </div>
            </div>

            <!-- Best Performances -->
            <h5 style="margin-bottom: 1rem;">🌟 Migliori Performance</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                ${stats.bestPerformances.map(perf => `
                    <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">${perf.label}</div>
                        <div style="font-size: 1.5rem; font-weight: 600; color: #667eea;">${perf.value} W</div>
                        <div style="font-size: 0.875rem; color: #999; margin-top: 0.25rem;">${perf.athlete}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    tabContent.innerHTML = html;
}

// ========== MEMBERS TAB ==========

async function renderTeamMembersTab(teamId, team, athletes, tabContent) {
    if (athletes.length === 0) {
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <p style="color: #666;">Nessun membro in questa squadra</p>
            </div>
        `;
        return;
    }

    let html = `
        <div style="padding: 1.5rem;">
            <h4 style="margin-bottom: 1rem;">👥 Membri della Squadra</h4>
            <div style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead style="background: #f8f9fa;">
                        <tr>
                            <th style="padding: 1rem; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600;">Atleta</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">Peso (kg)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">CP (W)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">CP (W/kg)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">W' (J)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">Azioni</th>
                        </tr>
                    </thead>
                    <tbody>`;

    athletes.forEach((athlete, idx) => {
        const bgColor = idx % 2 === 0 ? 'white' : '#f8f9fa';
        const cpKg = athlete.cp && athlete.weight_kg ? (athlete.cp / athlete.weight_kg).toFixed(2) : '-';
        
        html += `
            <tr style="background: ${bgColor}; border-bottom: 1px solid #eee;">
                <td style="padding: 1rem;">
                    <div style="font-weight: 600;">${athlete.first_name} ${athlete.last_name}</div>
                    <div style="font-size: 0.875rem; color: #666;">${athlete.gender || ''}</div>
                </td>
                <td style="padding: 1rem; text-align: center;">${athlete.weight_kg || '-'}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #667eea;">${athlete.cp || '-'}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #4facfe;">${cpKg}</td>
                <td style="padding: 1rem; text-align: center;">${athlete.cp ? '-' : '-'}</td>
                <td style="padding: 1rem; text-align: center;">
                    <button class="btn btn-primary btn-sm" onclick="navigateToAthlete(${athlete.id})">
                        Dettagli
                    </button>
                </td>
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

// ========== RANKINGS TAB ==========

async function renderTeamRankingsTab(teamId, team, athletes, tabContent) {
    tabContent.innerHTML = `
        <div style="padding: 2rem; text-align: center;">
            <div class="spinner" style="margin: 2rem auto;"></div>
            <p style="color: #666; margin-top: 1rem;">Caricamento rankings...</p>
        </div>
    `;

    // Check if athletes have API keys
    const athletesWithKeys = athletes.filter(a => a.api_key);
    
    if (athletesWithKeys.length === 0) {
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <p style="color: #666;">Nessun atleta con API key configurata</p>
            </div>
        `;
        return;
    }

    // Calculate rankings for all athletes
    const rankings = await calculateTeamRankings(athletesWithKeys);

    renderRankingsTable(rankings, tabContent);
}

// ========== COMPARISON TAB ==========

async function renderTeamComparisonTab(teamId, team, athletes, tabContent) {
    tabContent.innerHTML = `
        <div style="padding: 2rem; text-align: center;">
            <div class="spinner" style="margin: 2rem auto;"></div>
            <p style="color: #666; margin-top: 1rem;">Caricamento power curves...</p>
        </div>
    `;

    const athletesWithKeys = athletes.filter(a => a.api_key);
    
    if (athletesWithKeys.length === 0) {
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <p style="color: #666;">Nessun atleta con API key configurata</p>
            </div>
        `;
        return;
    }

    // Fetch power curves for all athletes
    const powerCurves = await fetchAllPowerCurves(athletesWithKeys);

    renderPowerCurvesComparison(powerCurves, athletesWithKeys, tabContent);
}

// ========== HELPER FUNCTIONS ==========

window.navigateToAthlete = function(athleteId) {
    // Set the athlete view
    window.currentAthleteView = athleteId;
    
    // Navigate to athletes module
    const athletesNav = document.querySelector('[data-page="athletes"]');
    if (athletesNav) {
        athletesNav.click();
    }
};

async function calculateTeamStatistics(athletes) {
    const withCP = athletes.filter(a => a.cp);
    const withWeight = athletes.filter(a => a.weight_kg);

    const avgCP = withCP.length > 0 
        ? Math.round(withCP.reduce((sum, a) => sum + a.cp, 0) / withCP.length)
        : 0;

    const avgCPkg = withCP.length > 0 && withWeight.length > 0
        ? (withCP.reduce((sum, a) => {
              if (a.weight_kg) return sum + (a.cp / a.weight_kg);
              return sum;
          }, 0) / withCP.filter(a => a.weight_kg).length).toFixed(2)
        : '0.00';

    const avgWeight = withWeight.length > 0
        ? (withWeight.reduce((sum, a) => sum + a.weight_kg, 0) / withWeight.length).toFixed(1)
        : '0';

    // Calculate W' average from power curves (90 days)
    let totalWPrime = 0;
    let totalWPrimeKg = 0;
    let withWPrimeCount = 0;
    let withWPrimeKgCount = 0;

    const today = new Date();
    const days90ago = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
    const dateStr90 = days90ago.toISOString().split('T')[0];
    const todayStr = today.toISOString().split('T')[0];

    for (const athlete of athletes) {
        if (!athlete.api_key) continue;
        
        try {
            const response = await fetch(`/api/athletes/${athlete.id}/power-curve?oldest=${dateStr90}&newest=${todayStr}`);
            if (!response.ok) continue;
            
            const powerData = await response.json();
            const durations = powerData.secs || [];
            const watts = powerData.watts || [];
            
            if (durations.length < 4) continue;
            
            const filtered = filterPowerCurveData(durations, watts, 1, 70, 10);
            if (filtered.selectedCount < 4) continue;
            
            try {
                const cpResult = calculateOmniPD(filtered.times, filtered.powers);
                totalWPrime += cpResult.W_prime;
                withWPrimeCount++;
                
                if (athlete.weight_kg) {
                    totalWPrimeKg += cpResult.W_prime / athlete.weight_kg / 1000;
                    withWPrimeKgCount++;
                }
            } catch (err) {
                console.warn(`Failed to calculate CP for ${athlete.id}:`, err);
            }
        } catch (err) {
            console.warn(`Failed to load power curve for ${athlete.id}:`, err);
        }
    }

    const avgWPrime = withWPrimeCount > 0 ? Math.round(totalWPrime / withWPrimeCount) : 0;
    const avgWPrimeKg = withWPrimeKgCount > 0 ? (totalWPrimeKg / withWPrimeKgCount).toFixed(3) : '0.000';

    // Best performances
    const bestPerformances = [
        { label: 'CP Massima', value: withCP.length > 0 ? Math.max(...withCP.map(a => a.cp)) : 0, athlete: withCP.length > 0 ? `${withCP.reduce((max, a) => a.cp > max.cp ? a : max).first_name} ${withCP.reduce((max, a) => a.cp > max.cp ? a : max).last_name}` : '-' },
        { label: 'CP/kg Massima', value: withCP.filter(a => a.weight_kg).length > 0 ? Math.round(Math.max(...withCP.filter(a => a.weight_kg).map(a => a.cp / a.weight_kg))) : 0, athlete: '-' }
    ];

    return {
        totalMembers: athletes.length,
        avgCP,
        avgCPkg,
        avgWPrime,
        avgWPrimeKg,
        avgWeight,
        bestPerformances
    };
}

async function calculateTeamRankings(athletes) {
    const today = new Date();
    const days90ago = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
    const dateStr90 = days90ago.toISOString().split('T')[0];
    const todayStr = today.toISOString().split('T')[0];

    const rankings = [];

    for (const athlete of athletes) {
        try {
            const response = await fetch(`/api/athletes/${athlete.id}/power-curve?oldest=${dateStr90}&newest=${todayStr}`);
            if (!response.ok) continue;

            const powerData = await response.json();
            const durations = powerData.secs || [];
            const watts = powerData.watts || [];

            if (durations.length === 0) continue;

            // Extract specific durations
            const targetDurations = [1, 5, 180, 360, 720]; // 1s, 5s, 3m, 6m, 12m
            const mmps = {};

            for (const duration of targetDurations) {
                const index = durations.findIndex(d => d >= duration);
                if (index !== -1) {
                    mmps[duration] = watts[index] || 0;
                } else {
                    mmps[duration] = null;
                }
            }

            // Calculate CP
            const valuesPerWindow = 1;
            const minPercentile = 70;
            const sprintSeconds = 10;

            let filtered = null;
            let currentPercentile = minPercentile;

            while (currentPercentile >= 0) {
                const tempFiltered = filterPowerCurveData(durations, watts, valuesPerWindow, currentPercentile, sprintSeconds);
                if (tempFiltered.selectedCount >= 4) {
                    filtered = tempFiltered;
                    break;
                }
                currentPercentile--;
            }

            let cp = null;
            let w_prime = null;
            if (filtered) {
                try {
                    const cpResult = calculateOmniPD(filtered.times, filtered.powers);
                    cp = Math.round(cpResult.CP);
                    w_prime = Math.round(cpResult.W_prime);
                } catch (err) {
                    console.warn(`Failed to calculate CP for athlete ${athlete.id}:`, err);
                }
            }

            rankings.push({
                athlete: athlete,
                cp: cp,
                w_prime: w_prime,
                mmp_1s: mmps[1],
                mmp_5s: mmps[5],
                mmp_3m: mmps[180],
                mmp_6m: mmps[360],
                mmp_12m: mmps[720]
            });

        } catch (err) {
            console.warn(`Failed to load power curve for athlete ${athlete.id}:`, err);
        }
    }

    return rankings;
}

function renderRankingsTable(rankings, tabContent) {
    const durations = [
        { key: 'mmp_1s', label: '1s', name: '1 secondo' },
        { key: 'mmp_5s', label: '5s', name: '5 secondi' },
        { key: 'mmp_3m', label: '3m', name: '3 minuti' },
        { key: 'mmp_6m', label: '6m', name: '6 minuti' },
        { key: 'mmp_12m', label: '12m', name: '12 minuti' }
    ];

    let html = `
        <div style="padding: 1.5rem;">
            <h4 style="margin-bottom: 1.5rem;">🏆 Rankings della Squadra</h4>
    `;

    // Create ranking table for each duration
    durations.forEach(duration => {
        // Sort by absolute power
        const sortedAbsolute = [...rankings]
            .filter(r => r[duration.key] !== null)
            .sort((a, b) => (b[duration.key] || 0) - (a[duration.key] || 0));

        // Sort by W/kg
        const sortedPerKg = [...rankings]
            .filter(r => r[duration.key] !== null && r.athlete.weight_kg)
            .sort((a, b) => {
                const aPerKg = a[duration.key] / a.athlete.weight_kg;
                const bPerKg = b[duration.key] / b.athlete.weight_kg;
                return bPerKg - aPerKg;
            });

        html += `
            <div style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                <div style="background: #667eea; color: white; padding: 1rem;">
                    <h5 style="margin: 0; color: white;">📊 ${duration.name}</h5>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0;">
                    <!-- Absolute Power -->
                    <div style="border-right: 1px solid #ddd;">
                        <div style="background: #f8f9fa; padding: 0.75rem; font-weight: 600; border-bottom: 1px solid #ddd;">
                            Assoluto (W)
                        </div>
                        ${sortedAbsolute.slice(0, 5).map((r, idx) => `
                            <div style="padding: 0.75rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                                <div style="display: flex; align-items: center; gap: 0.75rem;">
                                    <span style="font-weight: 700; font-size: 1.25rem; color: ${idx === 0 ? '#FFD700' : idx === 1 ? '#C0C0C0' : idx === 2 ? '#CD7F32' : '#999'};">${idx + 1}</span>
                                    <span>${r.athlete.first_name} ${r.athlete.last_name}</span>
                                </div>
                                <span style="font-weight: 600; color: #667eea;">${Math.round(r[duration.key])} W</span>
                            </div>
                        `).join('')}
                    </div>
                    
                    <!-- W/kg -->
                    <div>
                        <div style="background: #f8f9fa; padding: 0.75rem; font-weight: 600; border-bottom: 1px solid #ddd;">
                            W/kg
                        </div>
                        ${sortedPerKg.slice(0, 5).map((r, idx) => {
                            const perKg = (r[duration.key] / r.athlete.weight_kg).toFixed(2);
                            return `
                                <div style="padding: 0.75rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                                        <span style="font-weight: 700; font-size: 1.25rem; color: ${idx === 0 ? '#FFD700' : idx === 1 ? '#C0C0C0' : idx === 2 ? '#CD7F32' : '#999'};">${idx + 1}</span>
                                        <span>${r.athlete.first_name} ${r.athlete.last_name}</span>
                                    </div>
                                    <span style="font-weight: 600; color: #4facfe;">${perKg} W/kg</span>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
    });

    html += `</div>`;
    tabContent.innerHTML = html;
}

async function fetchAllPowerCurves(athletes) {
    const today = new Date();
    const days90ago = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
    const dateStr90 = days90ago.toISOString().split('T')[0];
    const todayStr = today.toISOString().split('T')[0];

    const powerCurves = [];

    for (const athlete of athletes) {
        try {
            const response = await fetch(`/api/athletes/${athlete.id}/power-curve?oldest=${dateStr90}&newest=${todayStr}`);
            if (!response.ok) continue;

            const powerData = await response.json();
            if (powerData.secs && powerData.secs.length > 0) {
                powerCurves.push({
                    athlete: athlete,
                    data: powerData
                });
            }
        } catch (err) {
            console.warn(`Failed to load power curve for athlete ${athlete.id}:`, err);
        }
    }

    return powerCurves;
}

function renderPowerCurvesComparison(powerCurves, athletes, tabContent) {
    if (powerCurves.length === 0) {
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <p style="color: #666;">Nessun dato disponibile per la comparazione</p>
            </div>
        `;
        return;
    }

    let html = `
        <div style="padding: 1.5rem;">
            <h4 style="margin-bottom: 1.5rem;">📈 Comparazione Power Curves (90 giorni)</h4>
            
            <div id="team-comparison-chart" style="width: 100%; height: 600px; background: white; border: 1px solid #e0e0e0; border-radius: 8px;"></div>
        </div>
    `;

    tabContent.innerHTML = html;

    // Render comparison chart
    renderComparisonChart(powerCurves);
}

function renderComparisonChart(powerCurves) {
    // Colors for each athlete
    const colors = ['#667eea', '#f093fb', '#4facfe', '#fa709a', '#43e97b', '#38f9d7', '#f6d365', '#fda085'];

    // Prepare series data
    const series = powerCurves.map((pc, idx) => {
        const durations = pc.data.secs || [];
        const watts = pc.data.watts || [];

        const seriesData = durations.map((sec, i) => ({
            x: Math.log10(Math.max(sec, 1)),
            y: watts[i] || 0,
            rawX: sec
        }));

        return {
            name: `${pc.athlete.first_name} ${pc.athlete.last_name}`,
            data: seriesData
        };
    });

    // Calculate min/max for axes
    const allDurations = powerCurves.flatMap(pc => pc.data.secs || []);
    const minDuration = Math.min(...allDurations.filter(d => d > 0));
    const maxDuration = Math.max(...allDurations.filter(d => d > 0));
    const logMin = Math.log10(minDuration * 0.95);
    const logMax = Math.log10(maxDuration * 1.05);

    const options = {
        series: series,
        chart: {
            type: 'line',
            height: 600,
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
                type: 'x'
            }
        },
        stroke: {
            curve: 'smooth',
            width: 3
        },
        colors: colors.slice(0, powerCurves.length),
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
            shared: false,
            intersect: false,
            x: {
                formatter: function(value) {
                    const sec = Math.pow(10, value);
                    if (sec < 60) return Math.round(sec) + ' sec';
                    if (sec < 3600) {
                        const mins = Math.floor(sec / 60);
                        const secs = Math.round(sec % 60);
                        return mins + 'm ' + secs + 's';
                    }
                    if (sec < 86400) {
                        const hours = Math.floor(sec / 3600);
                        const mins = Math.round((sec % 3600) / 60);
                        return hours + 'h ' + mins + 'm';
                    }
                    const days = Math.floor(sec / 86400);
                    const hours = Math.round((sec % 86400) / 3600);
                    return days + 'd ' + hours + 'h';
                }
            },
            y: {
                formatter: function(value) {
                    return Math.round(value) + ' W';
                }
            }
        },
        legend: {
            show: true,
            position: 'top',
            horizontalAlign: 'center'
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
    if (window.teamComparisonChart) {
        window.teamComparisonChart.destroy();
    }
    const chart = new ApexCharts(document.querySelector("#team-comparison-chart"), options);
    chart.render();
    window.teamComparisonChart = chart;
}

// ========== CRUD OPERATIONS ==========

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

// ========== CRUD OPERATIONS ==========

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
        window.backToTeamsDashboard();
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
    createModal(
        '⚠️ Conferma Eliminazione',
        '<p>Sei sicuro di voler eliminare questa squadra? Questa azione non può essere annullata.</p>',
        [
            {
                label: 'Annulla',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Elimina Squadra',
                class: 'btn-danger',
                onclick: `deleteTeamExecute(${teamId})`
            }
        ]
    );
};

window.deleteTeamExecute = async function(teamId) {
    try {
        showLoading();
        await api.deleteTeam(teamId);
        showToast('Squadra eliminata con successo', 'success');
        document.querySelector('.modal-overlay')?.remove();
        window.backToTeamsDashboard();
        window.renderTeamsPage();
    } catch (error) {
        showToast('Errore nell\'eliminazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};
