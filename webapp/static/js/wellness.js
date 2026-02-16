/**
 * Wellness Module - Frontend
 */

// Helper function to get color class for wellness scores (1-4 scale)
function getWellnessScoreColor(value) {
    if (!value) return '';
    switch (parseInt(value)) {
        case 1: return 'score-green';
        case 2: return 'score-black';
        case 3: return 'score-orange';
        case 4: return 'score-red';
        default: return '';
    }
}

window.renderWellnessPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    try {
        showLoading();
        const athletes = await api.getAthletes();
        
        // Get latest wellness for each athlete
        const athletesWithWellness = await Promise.all(
            athletes.map(async (athlete) => {
                try {
                    const latestWellness = await api.getLatestWellness(athlete.id);
                    return { ...athlete, latestWellness };
                } catch (error) {
                    // If no wellness data, return athlete with null wellness
                    return { ...athlete, latestWellness: null };
                }
            })
        );
        
        window.availableAthletes = athletes;
        
        contentArea.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Athlete Wellness</h3>
                    <div class="header-actions">
                        <button class="btn btn-secondary" onclick="syncWellnessData()">
                            <i class="bi bi-arrow-repeat"></i> Sync from Intervals
                        </button>
                        <button class="btn btn-primary" onclick="showCreateWellnessDialog()">
                            <i class="bi bi-plus"></i> Nuovo Entry
                        </button>
                    </div>
                </div>
                <div id="wellness-athletes-grid" class="athletes-grid"></div>
            </div>
        `;
        
        // Render athletes grid
        renderAthletesWellnessGrid(athletesWithWellness);
        
    } catch (error) {
        showToast('Errore nel caricamento dei dati wellness', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

function renderAthletesWellnessGrid(athletesWithWellness) {
    const gridContainer = document.getElementById('wellness-athletes-grid');
    
    // Filter athletes that have wellness data
    const athletesWithData = athletesWithWellness.filter(athlete => athlete.latestWellness !== null);
    
    if (athletesWithData.length === 0) {
        gridContainer.innerHTML = '<p class="no-data">No athletes with wellness data found</p>';
        return;
    }
    
    const gridHtml = athletesWithData.map(athlete => {
        const wellness = athlete.latestWellness;
        const athleteName = `${athlete.first_name} ${athlete.last_name}`;
        
        let wellnessContent = '<p class="no-wellness">No wellness data available</p>';
        
        if (wellness) {
            const sleepHours = wellness.sleep_secs ? (wellness.sleep_secs / 3600).toFixed(1) : '-';
            const menstrualPhaseText = wellness.menstrual_cycle_phase ? 
                ['Menstrual', 'Follicular', 'Ovulatory', 'Luteal'][wellness.menstrual_cycle_phase - 1] || wellness.menstrual_cycle_phase : null;
            
            wellnessContent = `
                <div class="wellness-summary-grid">
                    <div class="wellness-section">
                        <div class="section-title">📅 ${formatDate(wellness.wellness_date)}</div>
                        <div class="wellness-metrics">
                            ${wellness.weight_kg ? `<div class="metric"><span class="metric-label">Weight:</span><span class="metric-value">${formatNumber(wellness.weight_kg, 1)} kg</span></div>` : ''}
                            ${wellness.body_fat ? `<div class="metric"><span class="metric-label">Body Fat:</span><span class="metric-value">${formatNumber(wellness.body_fat, 1)}%</span></div>` : ''}
                            ${wellness.kcal ? `<div class="metric"><span class="metric-label">Calories:</span><span class="metric-value">${wellness.kcal}</span></div>` : ''}
                        </div>
                    </div>
                    
                    <div class="wellness-section">
                        <div class="section-title">❤️ Cardio</div>
                        <div class="wellness-metrics">
                            ${wellness.resting_hr ? `<div class="metric"><span class="metric-label">Resting HR:</span><span class="metric-value">${wellness.resting_hr} bpm</span></div>` : ''}
                            ${wellness.hrv ? `<div class="metric"><span class="metric-label">HRV:</span><span class="metric-value">${formatNumber(wellness.hrv, 1)} ms</span></div>` : ''}
                            ${wellness.avg_sleeping_hr ? `<div class="metric"><span class="metric-label">Sleep HR:</span><span class="metric-value">${formatNumber(wellness.avg_sleeping_hr, 1)} bpm</span></div>` : ''}
                        </div>
                    </div>
                    
                    <div class="wellness-section">
                        <div class="section-title">😴 Sleep</div>
                        <div class="wellness-metrics">
                            ${wellness.sleep_secs ? `<div class="metric"><span class="metric-label">Hours:</span><span class="metric-value">${sleepHours} h</span></div>` : ''}
                            ${wellness.sleep_quality ? `<div class="metric"><span class="metric-label">Quality:</span><span class="metric-value">${wellness.sleep_quality}/5</span></div>` : ''}
                            ${wellness.sleep_score ? `<div class="metric"><span class="metric-label">Score:</span><span class="metric-value">${wellness.sleep_score}/10</span></div>` : ''}
                            ${wellness.readiness ? `<div class="metric"><span class="metric-label">Readiness:</span><span class="metric-value">${formatNumber(wellness.readiness, 1)}</span></div>` : ''}
                        </div>
                    </div>
                    
                    <div class="wellness-section">
                        <div class="section-title">💪 Status</div>
                        <div class="wellness-metrics">
                            ${wellness.mood ? `<div class="metric"><span class="metric-label">Mood:</span><span class="metric-value ${getWellnessScoreColor(wellness.mood)}">${wellness.mood}/4</span></div>` : ''}
                            ${wellness.fatigue ? `<div class="metric"><span class="metric-label">Fatigue:</span><span class="metric-value ${getWellnessScoreColor(wellness.fatigue)}">${wellness.fatigue}/4</span></div>` : ''}
                            ${wellness.stress ? `<div class="metric"><span class="metric-label">Stress:</span><span class="metric-value">${wellness.stress}/10</span></div>` : ''}
                            ${wellness.motivation ? `<div class="metric"><span class="metric-label">Motivation:</span><span class="metric-value ${getWellnessScoreColor(wellness.motivation)}">${wellness.motivation}/4</span></div>` : ''}
                            ${wellness.soreness ? `<div class="metric"><span class="metric-label">Soreness:</span><span class="metric-value ${getWellnessScoreColor(wellness.soreness)}">${wellness.soreness}/4</span></div>` : ''}
                        </div>
                    </div>
                    
                    <div class="wellness-section">
                        <div class="section-title">🏃 Training</div>
                        <div class="wellness-metrics">
                            ${wellness.ctl ? `<div class="metric"><span class="metric-label">CTL:</span><span class="metric-value">${formatNumber(wellness.ctl, 1)}</span></div>` : ''}
                            ${wellness.atl ? `<div class="metric"><span class="metric-label">ATL:</span><span class="metric-value">${formatNumber(wellness.atl, 1)}</span></div>` : ''}
                            ${wellness.ramp_rate ? `<div class="metric"><span class="metric-label">Ramp Rate:</span><span class="metric-value">${formatNumber(wellness.ramp_rate, 3)}</span></div>` : ''}
                        </div>
                    </div>
                    
                    <div class="wellness-section">
                        <div class="section-title">📊 Other</div>
                        <div class="wellness-metrics">
                            ${wellness.steps ? `<div class="metric"><span class="metric-label">Steps:</span><span class="metric-value">${wellness.steps.toLocaleString()}</span></div>` : ''}
                            ${wellness.respiration ? `<div class="metric"><span class="metric-label">Respiration:</span><span class="metric-value">${formatNumber(wellness.respiration, 1)} rpm</span></div>` : ''}
                            ${wellness.spO2 ? `<div class="metric"><span class="metric-label">SpO2:</span><span class="metric-value">${formatNumber(wellness.spO2, 1)}%</span></div>` : ''}
                            ${wellness.injury ? `<div class="metric"><span class="metric-label">Injury:</span><span class="metric-value">${formatNumber(wellness.injury, 1)}</span></div>` : ''}
                            ${menstrualPhaseText ? `<div class="metric"><span class="metric-label">Cycle:</span><span class="metric-value">${menstrualPhaseText}</span></div>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="athlete-wellness-card">
                <div class="athlete-header">
                    <h4>${athleteName}</h4>
                    <button class="btn btn-secondary btn-sm" onclick="viewAthleteWellnessDetails(${athlete.id}, '${athleteName}')">
                        <i class="bi bi-graph-up"></i> Details
                    </button>
                </div>
                <div class="wellness-content">
                    ${wellnessContent}
                </div>
            </div>
        `;
    }).join('');
    
    gridContainer.innerHTML = gridHtml;
}

window.viewAthleteWellnessDetails = async function(athleteId, athleteName) {
    try {
        showLoading();
        const wellnessData = await api.getWellness({ athlete_id: athleteId, days_back: 90 });
        
        createModal(
            `Wellness History - ${athleteName}`,
            `
            <div id="athlete-wellness-details">
                ${wellnessData.length === 0 ? 
                    '<p class="no-data">No wellness data available</p>' :
                    createWellnessTable(wellnessData)
                }
            </div>
            `,
            [
                {
                    label: 'Close',
                    class: 'btn-secondary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                }
            ],
            'large-modal'
        );
        
    } catch (error) {
        showToast('Error loading wellness history', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

function createWellnessTable(wellnessData) {
    const tableHtml = `
        <div class="table-responsive">
            <table class="table wellness-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Weight</th>
                        <th>Body Fat</th>
                        <th>Resting HR</th>
                        <th>Sleep</th>
                        <th>Mood</th>
                        <th>Fatigue</th>
                        <th>Stress</th>
                        <th>Readiness</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${wellnessData.map(entry => {
                        const sleepHours = entry.sleep_secs ? (entry.sleep_secs / 3600).toFixed(1) : '-';
                        const readiness = entry.readiness ? formatNumber(entry.readiness, 1) : '-';
                        
                        return `
                            <tr class="wellness-row" onclick="toggleWellnessDetails(${entry.id})">
                                <td class="date-cell">${formatDate(entry.wellness_date)}</td>
                                <td>${entry.weight_kg ? formatNumber(entry.weight_kg, 1) + ' kg' : '-'}</td>
                                <td>${entry.body_fat ? formatNumber(entry.body_fat, 1) + '%' : '-'}</td>
                                <td>${entry.resting_hr || '-'}</td>
                                <td>${sleepHours} h</td>
                                <td>${entry.mood || '-'}</td>
                                <td>${entry.fatigue || '-'}</td>
                                <td>${entry.stress || '-'}</td>
                                <td>${readiness}</td>
                                <td class="actions-cell">
                                    <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); editWellness(${entry.id})">
                                        <i class="bi bi-pencil"></i>
                                    </button>
                                    <button class="btn btn-danger btn-sm" onclick="event.stopPropagation(); deleteWellnessConfirm(${entry.id})">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </td>
                            </tr>
                            <tr id="details-${entry.id}" class="wellness-details-row" style="display: none;">
                                <td colspan="10">
                                    <div class="wellness-details">
                                        <div class="details-grid">
                                            ${entry.body_fat ? `<div class="detail-item"><span class="detail-label">Body Fat:</span><span class="detail-value">${formatNumber(entry.body_fat, 1)}%</span></div>` : ''}
                                            ${entry.hrv ? `<div class="detail-item"><span class="detail-label">HRV:</span><span class="detail-value">${formatNumber(entry.hrv, 1)} ms</span></div>` : ''}
                                            ${entry.avg_sleeping_hr ? `<div class="detail-item"><span class="detail-label">Sleep HR:</span><span class="detail-value">${formatNumber(entry.avg_sleeping_hr, 1)} bpm</span></div>` : ''}
                                            ${entry.sleep_quality ? `<div class="detail-item"><span class="detail-label">Sleep Quality:</span><span class="detail-value">${entry.sleep_quality}/5</span></div>` : ''}
                                            ${entry.sleep_score ? `<div class="detail-item"><span class="detail-label">Sleep Score:</span><span class="detail-value">${entry.sleep_score}/10</span></div>` : ''}
                                            ${entry.motivation ? `<div class="detail-item"><span class="detail-label">Motivation:</span><span class="detail-value ${getWellnessScoreColor(entry.motivation)}">${entry.motivation}/4</span></div>` : ''}
                                            ${entry.soreness ? `<div class="detail-item"><span class="detail-label">Soreness:</span><span class="detail-value ${getWellnessScoreColor(entry.soreness)}">${entry.soreness}/4</span></div>` : ''}
                                            ${entry.kcal ? `<div class="detail-item"><span class="detail-label">Calories:</span><span class="detail-value">${entry.kcal}</span></div>` : ''}
                                            ${entry.steps ? `<div class="detail-item"><span class="detail-label">Steps:</span><span class="detail-value">${entry.steps.toLocaleString()}</span></div>` : ''}
                                            ${entry.respiration ? `<div class="detail-item"><span class="detail-label">Respiration:</span><span class="detail-value">${formatNumber(entry.respiration, 1)} rpm</span></div>` : ''}
                                            ${entry.spO2 ? `<div class="detail-item"><span class="detail-label">SpO2:</span><span class="detail-value">${formatNumber(entry.spO2, 1)}%</span></div>` : ''}
                                            ${entry.injury ? `<div class="detail-item"><span class="detail-label">Injury:</span><span class="detail-value">${formatNumber(entry.injury, 1)}</span></div>` : ''}
                                            ${entry.ctl ? `<div class="detail-item"><span class="detail-label">CTL:</span><span class="detail-value">${formatNumber(entry.ctl, 1)}</span></div>` : ''}
                                            ${entry.atl ? `<div class="detail-item"><span class="detail-label">ATL:</span><span class="detail-value">${formatNumber(entry.atl, 1)}</span></div>` : ''}
                                            ${entry.ramp_rate ? `<div class="detail-item"><span class="detail-label">Ramp Rate:</span><span class="detail-value">${formatNumber(entry.ramp_rate, 3)}</span></div>` : ''}
                                            ${entry.menstruation !== null ? `<div class="detail-item"><span class="detail-label">Menstrual:</span><span class="detail-value">${entry.menstruation ? 'Yes' : 'No'}</span></div>` : ''}
                                            ${entry.menstrual_cycle_phase ? `<div class="detail-item"><span class="detail-label">Cycle Phase:</span><span class="detail-value">${['Menstrual', 'Follicular', 'Ovulatory', 'Luteal'][entry.menstrual_cycle_phase - 1] || entry.menstrual_cycle_phase}</span></div>` : ''}
                                            ${entry.comments ? `<div class="detail-item full-width"><span class="detail-label">Notes:</span><span class="detail-value">${entry.comments}</span></div>` : ''}
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
    return tableHtml;
}

function toggleWellnessDetails(entryId) {
    const detailsRow = document.getElementById(`details-${entryId}`);
    const isVisible = detailsRow.style.display !== 'none';
    
    // Chiudi tutti i dettagli aperti
    document.querySelectorAll('.wellness-details-row').forEach(row => {
        row.style.display = 'none';
    });
    
    // Rimuovi la classe active da tutte le righe
    document.querySelectorAll('.wellness-row').forEach(row => {
        row.classList.remove('active');
    });
    
    // Se non era visibile, aprilo
    if (!isVisible) {
        detailsRow.style.display = 'table-row';
        event.currentTarget.classList.add('active');
    }
}

window.showCreateWellnessDialog = function() {
    const athletesOptions = window.availableAthletes.map(a => 
        `<option value="${a.id}">${a.first_name} ${a.last_name}</option>`
    ).join('');
    
    createModal(
        'Nuovo Entry Wellness',
        `
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Atleta</label>
                <select id="wellness-athlete" class="form-input" required>
                    <option value="">Seleziona atleta</option>
                    ${athletesOptions}
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Date</label>
                <input type="date" id="wellness-date" class="form-input" required>
            </div>
        </div>
        
        <div class="form-section">
            <h4>Physical Data</h4>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Weight (kg)</label>
                    <input type="number" id="wellness-weight" class="form-input" step="0.1">
                </div>
                <div class="form-group">
                    <label class="form-label">Body Fat (%)</label>
                    <input type="number" id="wellness-body-fat" class="form-input" step="0.1">
                </div>
                <div class="form-group">
                    <label class="form-label">Calories</label>
                    <input type="number" id="wellness-kcal" class="form-input" step="1">
                </div>
            </div>
        </div>
        
        <div class="form-section">
            <h4>Cardiac Data</h4>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Resting HR (bpm)</label>
                    <input type="number" id="wellness-hr" class="form-input" step="1">
                </div>
                <div class="form-group">
                    <label class="form-label">HRV (ms)</label>
                    <input type="number" id="wellness-hrv" class="form-input" step="0.1">
                </div>
                <div class="form-group">
                    <label class="form-label">Sleep HR (bpm)</label>
                    <input type="number" id="wellness-avg-sleeping-hr" class="form-input" step="0.1">
                </div>
            </div>
        </div>
        
        <div class="form-section">
            <h4>Sleep Data</h4>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Sleep (hours)</label>
                    <input type="number" id="wellness-sleep" class="form-input" step="0.5" placeholder="E.g. 8.5">
                </div>
                <div class="form-group">
                    <label class="form-label">Sleep Quality (1-5)</label>
                    <input type="number" id="wellness-sleep-quality" class="form-input" min="1" max="5" step="1">
                </div>
                <div class="form-group">
                    <label class="form-label">Sleep Score (1-10)</label>
                    <input type="number" id="wellness-sleep-score" class="form-input" min="1" max="10" step="1">
                </div>
            </div>
        </div>
        
        <div class="form-section">
            <h4>Activity and Movement</h4>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Steps</label>
                    <input type="number" id="wellness-steps" class="form-input" step="1">
                </div>
                <div class="form-group">
                    <label class="form-label">Respiration (rpm)</label>
                    <input type="number" id="wellness-respiration" class="form-input" step="0.1">
                </div>
                <div class="form-group">
                    <label class="form-label">SpO2 (%)</label>
                    <input type="number" id="wellness-spo2" class="form-input" step="0.1">
                </div>
            </div>
        </div>
        
        <div class="form-section">
            <h4>Perceptual State</h4>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Mood (1-4)</label>
                    <input type="number" id="wellness-mood" class="form-input" min="1" max="4" step="1">
                </div>
                <div class="form-group">
                    <label class="form-label">Fatigue (1-4)</label>
                    <input type="number" id="wellness-fatigue" class="form-input" min="1" max="4" step="1">
                </div>
                <div class="form-group">
                    <label class="form-label">Stress (1-10)</label>
                    <input type="number" id="wellness-stress" class="form-input" min="1" max="10" step="1">
                </div>
                <div class="form-group">
                    <label class="form-label">Motivation (1-4)</label>
                    <input type="number" id="wellness-motivation" class="form-input" min="1" max="4" step="1">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Muscle Soreness (1-4)</label>
                    <input type="number" id="wellness-soreness" class="form-input" min="1" max="4" step="1">
                </div>
                <div class="form-group">
                    <label class="form-label">Injury</label>
                    <input type="number" id="wellness-injury" class="form-input" step="0.1">
                </div>
                <div class="form-group">
                    <label class="form-label">Readiness</label>
                    <input type="number" id="wellness-readiness" class="form-input" step="0.1">
                </div>
            </div>
        </div>
        
        <div class="form-section">
            <h4>Training Load</h4>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">CTL</label>
                    <input type="number" id="wellness-ctl" class="form-input" step="0.1">
                </div>
                <div class="form-group">
                    <label class="form-label">ATL</label>
                    <input type="number" id="wellness-atl" class="form-input" step="0.1">
                </div>
                <div class="form-group">
                    <label class="form-label">Ramp Rate</label>
                    <input type="number" id="wellness-ramp-rate" class="form-input" step="0.001">
                </div>
            </div>
        </div>
        
        <div class="form-section">
            <h4>Menstrual Cycle</h4>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Menstrual</label>
                    <select id="wellness-menstruation" class="form-input">
                        <option value="">Select</option>
                        <option value="true">Yes</option>
                        <option value="false">No</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Cycle Phase</label>
                    <select id="wellness-menstrual-phase" class="form-input">
                        <option value="">Select</option>
                        <option value="1">Menstrual</option>
                        <option value="2">Follicular</option>
                        <option value="3">Ovulatory</option>
                        <option value="4">Luteal</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="form-group">
            <label class="form-label">Comments</label>
            <textarea id="wellness-comments" class="form-input" rows="3"></textarea>
        </div>
        `,
        [
            {
                label: 'Cancel',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Create',
                class: 'btn-primary',
                onclick: 'createWellness()'
            }
        ]
    );
};

window.createWellness = async function() {
    const athleteId = document.getElementById('wellness-athlete').value;
    const wellnessDate = document.getElementById('wellness-date').value;
    
    if (!athleteId || !wellnessDate) {
        showToast('Select athlete and date', 'warning');
        return;
    }
    
    const sleepHours = document.getElementById('wellness-sleep').value;
    const sleepSecs = sleepHours ? parseFloat(sleepHours) * 3600 : null;
    
    const data = {
        athlete_id: parseInt(athleteId),
        wellness_date: wellnessDate,
        weight_kg: document.getElementById('wellness-weight').value ? parseFloat(document.getElementById('wellness-weight').value) : null,
        resting_hr: document.getElementById('wellness-hr').value ? parseInt(document.getElementById('wellness-hr').value) : null,
        hrv: document.getElementById('wellness-hrv').value ? parseFloat(document.getElementById('wellness-hrv').value) : null,
        steps: document.getElementById('wellness-steps').value ? parseInt(document.getElementById('wellness-steps').value) : null,
        soreness: document.getElementById('wellness-soreness').value ? parseInt(document.getElementById('wellness-soreness').value) : null,
        fatigue: document.getElementById('wellness-fatigue').value ? parseInt(document.getElementById('wellness-fatigue').value) : null,
        stress: document.getElementById('wellness-stress').value ? parseInt(document.getElementById('wellness-stress').value) : null,
        mood: document.getElementById('wellness-mood').value ? parseInt(document.getElementById('wellness-mood').value) : null,
        motivation: document.getElementById('wellness-motivation').value ? parseInt(document.getElementById('wellness-motivation').value) : null,
        injury: document.getElementById('wellness-injury').value ? parseFloat(document.getElementById('wellness-injury').value) : null,
        kcal: document.getElementById('wellness-kcal').value ? parseInt(document.getElementById('wellness-kcal').value) : null,
        sleep_secs: sleepSecs,
        sleep_score: document.getElementById('wellness-sleep-score').value ? parseInt(document.getElementById('wellness-sleep-score').value) : null,
        sleep_quality: document.getElementById('wellness-sleep-quality').value ? parseInt(document.getElementById('wellness-sleep-quality').value) : null,
        avg_sleeping_hr: document.getElementById('wellness-avg-sleeping-hr').value ? parseFloat(document.getElementById('wellness-avg-sleeping-hr').value) : null,
        menstruation: document.getElementById('wellness-menstruation').value ? (document.getElementById('wellness-menstruation').value === 'true') : null,
        menstrual_cycle_phase: document.getElementById('wellness-menstrual-phase').value ? parseInt(document.getElementById('wellness-menstrual-phase').value) : null,
        body_fat: document.getElementById('wellness-body-fat').value ? parseFloat(document.getElementById('wellness-body-fat').value) : null,
        respiration: document.getElementById('wellness-respiration').value ? parseFloat(document.getElementById('wellness-respiration').value) : null,
        spO2: document.getElementById('wellness-spo2').value ? parseFloat(document.getElementById('wellness-spo2').value) : null,
        readiness: document.getElementById('wellness-readiness').value ? parseFloat(document.getElementById('wellness-readiness').value) : null,
        ctl: document.getElementById('wellness-ctl').value ? parseFloat(document.getElementById('wellness-ctl').value) : null,
        atl: document.getElementById('wellness-atl').value ? parseFloat(document.getElementById('wellness-atl').value) : null,
        ramp_rate: document.getElementById('wellness-ramp-rate').value ? parseFloat(document.getElementById('wellness-ramp-rate').value) : null,
        comments: document.getElementById('wellness-comments').value || null
    };
    
    try {
        showLoading();
        await api.createWellness(data);
        showToast('Entry wellness creato con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderWellnessPage();
    } catch (error) {
        showToast('Errore nella creazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.editWellness = async function(wellnessId) {
    try {
        const wellness = await api.getWellnessEntry(wellnessId);
        const sleepHours = wellness.sleep_secs ? (wellness.sleep_secs / 3600).toFixed(1) : '';
        
        createModal(
            'Edit Wellness',
            `
            <div class="form-section">
                <h4>Main Data</h4>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Weight (kg)</label>
                        <input type="number" id="wellness-weight-edit" class="form-input" value="${wellness.weight_kg || ''}" step="0.1">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Resting HR (bpm)</label>
                        <input type="number" id="wellness-hr-edit" class="form-input" value="${wellness.resting_hr || ''}" step="1">
                    </div>
                    <div class="form-group">
                        <label class="form-label">HRV (ms)</label>
                        <input type="number" id="wellness-hrv-edit" class="form-input" value="${wellness.hrv || ''}" step="0.1">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Umore (1-10)</label>
                        <input type="number" id="wellness-mood-edit" class="form-input" value="${wellness.mood || ''}" min="1" max="10" step="1">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Sonno (ore)</label>
                        <input type="number" id="wellness-sleep-edit" class="form-input" value="${sleepHours}" step="0.5">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Comments</label>
                        <textarea id="wellness-comments-edit" class="form-input" rows="2">${wellness.comments || ''}</textarea>
                    </div>
                </div>
            </div>
            `,
            [
                {
                    label: 'Cancel',
                    class: 'btn-secondary',
                    onclick: 'this.closest(".modal-overlay").remove()'
                },
                {
                    label: 'Save',
                    class: 'btn-primary',
                    onclick: `updateWellness(${wellnessId}, ${wellness.athlete_id}, '${wellness.wellness_date}')`
                }
            ]
        );
    } catch (error) {
        showToast('Errore nel caricamento dei dati', 'error');
    }
};

window.updateWellness = async function(wellnessId, athleteId, wellnessDate) {
    const sleepHours = document.getElementById('wellness-sleep-edit').value;
    const sleepSecs = sleepHours ? parseFloat(sleepHours) * 3600 : null;
    
    const data = {
        athlete_id: athleteId,
        wellness_date: wellnessDate,
        weight_kg: document.getElementById('wellness-weight-edit').value ? parseFloat(document.getElementById('wellness-weight-edit').value) : null,
        resting_hr: document.getElementById('wellness-hr-edit').value ? parseInt(document.getElementById('wellness-hr-edit').value) : null,
        hrv: document.getElementById('wellness-hrv-edit').value ? parseFloat(document.getElementById('wellness-hrv-edit').value) : null,
        mood: document.getElementById('wellness-mood-edit').value ? parseInt(document.getElementById('wellness-mood-edit').value) : null,
        sleep_secs: sleepSecs,
        comments: document.getElementById('wellness-comments-edit').value || null
    };
    
    try {
        showLoading();
        await api.updateWellness(wellnessId, data);
        showToast('Wellness aggiornato con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderWellnessPage();
    } catch (error) {
        showToast('Errore nell\'aggiornamento: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.deleteWellnessConfirm = function(wellnessId) {
    createModal(
        '⚠️ Conferma Eliminazione',
        '<p>Sei sicuro di voler eliminare questa entry wellness?</p>',
        [
            {
                label: 'Annulla',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Elimina Entry',
                class: 'btn-danger',
                onclick: `deleteWellnessExecute(${wellnessId})`
            }
        ]
    );
};

window.deleteWellnessExecute = async function(wellnessId) {
    try {
        showLoading();
        await api.deleteWellness(wellnessId);
        showToast('Wellness deleted successfully', 'success');
        document.querySelector('.modal-overlay')?.remove();
        window.renderWellnessPage();
    } catch (error) {
        showToast('Error deleting: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.syncWellnessData = async function() {
    // Show athlete selection dialog
    const athleteOptions = window.availableAthletes
        .filter(athlete => athlete.api_key)
        .map(athlete => `<option value="${athlete.id}">${athlete.first_name} ${athlete.last_name}</option>`)
        .join('');
    
    if (athleteOptions.length === 0) {
        showToast('No athletes with API keys found. Please configure API keys in athlete settings.', 'warning');
        return;
    }
    
    createModal(
        'Sync Wellness from Intervals.icu',
        `
        <div style="padding: 1rem;">
            <div class="form-group">
                <label for="sync-athlete-select">Select Athlete:</label>
                <select id="sync-athlete-select" class="form-control" required>
                    <option value="">Choose athlete...</option>
                    ${athleteOptions}
                </select>
            </div>
            <div class="form-group">
                <label for="sync-days-back">Days back:</label>
                <input type="number" id="sync-days-back" class="form-control" value="30" min="1" max="90" required>
            </div>
        </div>
        `,
        [
            {
                label: 'Cancel',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Sync',
                class: 'btn-primary',
                onclick: 'performWellnessSync()'
            }
        ]
    );
};

window.performWellnessSync = async function() {
    const athleteId = document.getElementById('sync-athlete-select').value;
    const daysBack = document.getElementById('sync-days-back').value;
    
    if (!athleteId) {
        showToast('Please select an athlete', 'warning');
        return;
    }
    
    const athlete = window.availableAthletes.find(a => a.id === parseInt(athleteId));
    
    try {
        // Close modal
        document.querySelector('.modal-overlay').remove();
        
        showLoading();
        
        const result = await api.syncWellness({
            athlete_id: parseInt(athleteId),
            api_key: athlete.api_key,
            days_back: parseInt(daysBack)
        });
        
        showToast(result.message, 'success');
        
        // Refresh the page to show updated data
        window.renderWellnessPage();
        
    } catch (error) {
        showToast('Sync failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};
