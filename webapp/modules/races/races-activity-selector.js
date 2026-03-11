/**
 * Races Activity Selector Module
 * Handles matching Intervals activities to race athletes
 * Smart auto-matching with manual fallback selection
 */

/**
 * Open modal to select race activities from Intervals
 * @param {number} raceId - ID della gara
 * @param {number} stageNumber - (Opzionale) Numero della tappa (1-based)
 */
window.openRaceActivitySelector = async function(raceId, stageNumber) {
    try {
        showLoading();
        
        // Fetch candidate activities for all athletes
        const url = stageNumber 
            ? `/api/races/${raceId}/candidate-activities?stage_number=${stageNumber}`
            : `/api/races/${raceId}/candidate-activities`;
            
        const response = await fetch(url, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        hideLoading();
        
        // Render the selector modal
        await renderActivitySelector(raceId, data, stageNumber);
        
    } catch (error) {
        hideLoading();
        showToast(`Errore nel caricamento delle attività: ${error.message}`, 'error');
    }
};

/**
 * Render activity selector modal/panel
 * @param {number} raceId - ID della gara
 * @param {object} data - Data containing race and athlete activity candidates
 * @param {number} stageNumber - (Opzionale) Numero della tappa
 */
window.renderActivitySelector = async function(raceId, data, stageNumber) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'activity-selector-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    
    const raceName = data.race_name || 'Gara';
    const raceDate = data.race_date || 'N/A';
    const results = data.results || {};
    
    // Build athlete sections
    let athleteSectionsHtml = '';
    for (const [athleteId, athleteData] of Object.entries(results)) {
        const athleteName = athleteData.athlete_name || 'Unknown';
        const error = athleteData.error;
        const autoMatched = athleteData.auto_matched;
        const candidates = athleteData.candidates || [];
        
        if (error) {
            athleteSectionsHtml += `
                <div class="athlete-activity-section" data-athlete-id="${athleteId}">
                    <h4>${athleteName}</h4>
                    <div class="error-box">⚠️ ${error}</div>
                </div>
            `;
            continue;
        }
        
        // Build candidates list
        let candidatesHtml = '';
        if (candidates.length === 0) {
            candidatesHtml = '<p class="no-activities">Nessuna attività trovata per questo giorno</p>';
        } else {
            for (const candidate of candidates) {
                // Convert distance: if > 1000, assume it's in meters
                let distance = candidate.distance_km || 0;
                if (distance > 1000) {
                    distance = distance / 1000;
                }
                distance = distance ? distance.toFixed(1) : '—';
                
                const watts = candidate.avg_watts !== null ? candidate.avg_watts.toFixed(0) : null;
                const hr = candidate.avg_hr !== null ? candidate.avg_hr.toFixed(0) : '—';
                // Format time: convert minutes to ##h##m
                const timeMinutes = candidate.moving_time_min || 0;
                const hours = Math.floor(timeMinutes / 60);
                const mins = Math.round(timeMinutes % 60);
                const time = timeMinutes ? `${hours}h ${mins}m` : '—';
                
                let isHighlighted = '';
                let highlightBadge = '';
                if (autoMatched && candidate.id === autoMatched.id) {
                    isHighlighted = 'highlighted';
                    highlightBadge = `<span class="badge-auto">Auto-match ${autoMatched.similarity}%</span>`;
                }
                
                candidatesHtml += `
                    <div class="activity-candidate ${isHighlighted}" data-activity-id="${candidate.id}" data-athlete-id="${athleteId}">
                        <div class="activity-main">
                            <div class="activity-name">${candidate.name}</div>
                            ${highlightBadge}
                            <div class="activity-meta">
                                <span>📅 ${candidate.date}</span>
                                <span>🚴 ${distance}km</span>
                                <span>⏱️ ${time}</span>
                                ${watts ? `<span>⚡ ${watts}W</span>` : ''}
                                <span>❤️ ${hr}bpm</span>
                            </div>
                        </div>
                        <button class="btn-small" onclick="window.selectActivity('${raceId}', ${athleteId}, '${candidate.id}', '${candidate.name.replace(/'/g, "\\'")}')">
                            Seleziona
                        </button>
                    </div>
                `;
            }
        }
        
        athleteSectionsHtml += `
            <div class="athlete-activity-section" data-athlete-id="${athleteId}">
                <h4>${athleteName}</h4>
                ${autoMatched ? `
                    <div class="auto-match-badge">
                        ✅ Auto-match trovato: <strong>${autoMatched.name}</strong> (${autoMatched.similarity}% match)
                    </div>
                ` : ''}
                <div class="candidates-list">
                    ${candidatesHtml}
                </div>
            </div>
        `;
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'activity-selector-content';
    contentDiv.style.cssText = `
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        width: 90%;
        max-width: 1000px;
        max-height: 85vh;
        display: flex;
        flex-direction: column;
    `;
    
    // Build title with stage indicator if applicable
    const titleText = stageNumber 
        ? `🎯 Seleziona Attività di Gara - Tappa ${stageNumber}`
        : `🎯 Seleziona Attività di Gara`;
    
    contentDiv.innerHTML = `
        <div class="modal-header" style="padding: 20px; border-bottom: 2px solid #e0e0e0; flex-shrink: 0; display: flex; justify-content: space-between; align-items: center;">
            <h2 style="margin: 0; font-size: 1.5rem;">${titleText}</h2>
            <button class="btn-close" onclick="document.getElementById('activity-selector-modal').remove()" style="background: none; border: none; font-size: 2.5rem; cursor: pointer; color: #999; padding: 0; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;" title="Chiudi">×</button>
        </div>
        
        <div class="modal-body" style="flex: 1; overflow-y: auto; padding: 20px;">
            <div class="athletes-activities" style="display: flex; flex-direction: column; gap: 25px;">
                ${athleteSectionsHtml}
            </div>
        </div>
        
        <div class="modal-footer" style="padding: 15px 20px; border-top: 1px solid #e0e0e0; display: flex; justify-content: flex-end; gap: 10px; flex-shrink: 0; background: #fafafa;">
            <button class="btn btn-primary" onclick="window.finalizeLinkActivities('${raceId}')" style="padding: 10px 20px; border-radius: 6px; border: none; background: #3b82f6; color: white; cursor: pointer; font-weight: 600;">✓ Salva Selezioni</button>
        </div>
        
        <style>
            .selector-info p { margin: 5px 0; }
            
            .athlete-activity-section {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                background: #fafafa;
            }
            
            .athlete-activity-section h4 {
                margin: 0 0 15px 0;
                color: #333;
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 8px;
            }
            
            .auto-match-badge {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 6px;
                padding: 10px;
                margin-bottom: 15px;
                color: #155724;
                font-size: 0.9rem;
            }
            
            .candidates-list {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .activity-candidate {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.2s;
                cursor: pointer;
            }
            
            .activity-candidate:hover {
                border-color: #3b82f6;
                background: #f8f9ff;
            }
            
            .activity-candidate.highlighted {
                background: #fef3c7;
                border: 2px solid #fbbf24;
            }
            
            .activity-main {
                flex: 1;
            }
            
            .activity-name {
                font-weight: 500;
                color: #333;
                margin-bottom: 5px;
            }
            
            .activity-meta {
                display: flex;
                gap: 15px;
                font-size: 0.85rem;
                color: #666;
                flex-wrap: wrap;
            }
            
            .activity-meta span {
                display: flex;
                align-items: center;
                gap: 3px;
            }
            
            .badge-auto {
                display: inline-block;
                background: #fbbf24;
                color: #92400e;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 8px;
            }
            
            .no-activities {
                color: #999;
                font-style: italic;
                text-align: center;
                padding: 20px;
                background: white;
                border-radius: 6px;
            }
            
            .error-box {
                background: #fee;
                border: 1px solid #fcc;
                color: #c33;
                padding: 10px;
                border-radius: 6px;
                font-size: 0.9rem;
            }
            
            .btn-small {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.85rem;
                white-space: nowrap;
                flex-shrink: 0;
                margin-left: 10px;
            }
            
            .btn-small:hover {
                background: #2563eb;
            }
        </style>
    `;
    
    modal.appendChild(contentDiv);
    document.body.appendChild(modal);
};

/**
 * Select an activity for an athlete
 */
window.selectActivity = async function(raceId, athleteId, activityId, activityName) {
    try {
        showLoading();
        
        // Get race name from modal
        const raceData = await fetch(`/api/races/${raceId}`);
        const race = await raceData.json();
        const raceName = race.name || 'Gara';
        
        // Link activity
        const response = await fetch(`/api/races/${raceId}/link-activity`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                athlete_id: athleteId,
                intervals_activity_id: activityId,
                race_name: raceName
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        hideLoading();
        
        // Highlight the selected item
        const selectedEl = document.querySelector(`[data-activity-id="${activityId}"][data-athlete-id="${athleteId}"]`);
        if (selectedEl) {
            selectedEl.style.background = '#d4edda';
            selectedEl.style.borderColor = '#28a745';
            const btn = selectedEl.querySelector('.btn-small');
            if (btn) {
                btn.textContent = '✓ Collegato';
                btn.disabled = true;
                btn.style.background = '#28a745';
            }
        }
        
        showToast(`✓ Attività di ${activityName} collegata`, 'success');
        
        // Auto-scroll to next athlete with smooth animation
        const modalBody = document.querySelector('#activity-selector-modal .modal-body');
        const allSections = Array.from(document.querySelectorAll('.athlete-activity-section'));
        const currentSection = document.querySelector(`.athlete-activity-section[data-athlete-id="${athleteId}"]`);
        
        if (currentSection && allSections.length > 0 && modalBody) {
            const currentIndex = allSections.indexOf(currentSection);
            const nextSection = allSections[currentIndex + 1];
            
            if (nextSection) {
                // Use smooth scroll with correct offset calculation
                setTimeout(() => {
                    const athletesContainer = document.querySelector('#activity-selector-modal .athletes-activities');
                    if (athletesContainer) {
                        // Calculate position of next section relative to athletes container
                        const nextPos = nextSection.offsetTop - athletesContainer.offsetTop;
                        // Use scroll with smooth behavior
                        modalBody.scrollTo({
                            top: nextPos - 40,
                            behavior: 'smooth'
                        });
                    }
                }, 100);
            }
        }
        
    } catch (error) {
        hideLoading();
        showToast(`Errore nel collegamento: ${error.message}`, 'error');
    }
};

/**
 * Finalize all activity selections
 */
window.finalizeLinkActivities = async function(raceId) {
    try {
        showToast('✓ Attività collegate con successo!', 'success');
        
        // Close modal and refresh race details
        const modal = document.getElementById('activity-selector-modal');
        if (modal) {
            modal.remove();
        }
        
        // Reload race details to show updated activity links
        await window.renderRaceDetailsPage(raceId);
        
    } catch (error) {
        showToast(`Errore: ${error.message}`, 'error');
    }
};
