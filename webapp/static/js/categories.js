/**
 * Categories Module - Frontend
 * Multi-category dashboard with category detail views
 */

// Global state
window.currentCategoryView = null; // null = dashboard, number = category ID

window.renderCategoriesPage = async function() {
    const contentArea = document.getElementById('content-area');
    
    console.log('[CATEGORIES] renderCategoriesPage started. currentCategoryView:', window.currentCategoryView);
    
    try {
        showLoading();
        const categories = await api.getCategories();
        
        console.log('[CATEGORIES] Loaded', categories.length, 'categories');
        
        // Store globally
        window.allCategories = categories;
        
        // Render based on current view
        if (window.currentCategoryView === null) {
            console.log('[CATEGORIES] Rendering dashboard view');
            await renderCategoriesDashboard(categories, contentArea);
        } else {
            console.log('[CATEGORIES] Rendering detail view for category', window.currentCategoryView);
            renderCategoryDetail(window.currentCategoryView, categories, contentArea);
        }
        
    } catch (error) {
        console.error('[CATEGORIES] Error:', error);
        showToast('Errore nel caricamento delle categorie', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
};

async function renderCategoriesDashboard(categories, contentArea) {
    contentArea.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 Dashboard Categorie</h3>
                <button class="btn btn-primary" onclick="showCreateCategoryDialog()">
                    <i class="bi bi-plus"></i> Nuova Categoria
                </button>
            </div>
            <div class="card-body">
                <!-- Categories Grid -->
                <div id="categories-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem;">
                    ${categories.map(category => `<div id="category-card-${category.id}" class="team-card-placeholder">Caricamento...</div>`).join('')}
                </div>
            </div>
        </div>
    `;
    
    // Load member counts for each category
    for (const category of categories) {
        try {
            const athletes = await api.getAthletes(null, category.id);
            const cardHtml = createCategoryCard(category, athletes.length);
            const placeholder = document.getElementById(`category-card-${category.id}`);
            if (placeholder) {
                placeholder.innerHTML = cardHtml;
            }
        } catch (err) {
            console.warn(`Failed to load member count for category ${category.id}:`, err);
        }
    }
}

function createCategoryCard(category, memberCount = 0) {
    const initials = category.name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
    const colors = ['#667eea', '#f093fb', '#4facfe', '#fa709a', '#43e97b', '#38f9d7'];
    const colorIdx = category.id % colors.length;
    const bgColor = colors[colorIdx];
    
    return `
        <div onclick="showCategoryDetail(${category.id})" style="
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
                    <div style="font-weight: 600; color: #333; font-size: 1.1rem;">${category.name}</div>
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

window.showCategoryDetail = function(categoryId) {
    console.log('[CATEGORIES] Switching to detail view for category', categoryId);
    window.currentCategoryView = categoryId;
    window.renderCategoriesPage();
};

window.backToCategoriesDashboard = function() {
    console.log('[CATEGORIES] Switching back to dashboard');
    window.currentCategoryView = null;
    window.renderCategoriesPage();
};

async function renderCategoryDetail(categoryId, categories, contentArea) {
    const category = categories.find(c => c.id === categoryId);
    if (!category) {
        showToast('Categoria non trovata', 'error');
        window.backToCategoriesDashboard();
        return;
    }

    // Load category athletes
    const athletes = await api.getAthletes(null, categoryId);
    // Sort athletes alphabetically by last name
    athletes.sort((a, b) => a.last_name.localeCompare(b.last_name, 'it'));
    
    contentArea.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <button class="btn btn-secondary" onclick="backToCategoriesDashboard()">
                <i class="bi bi-arrow-left"></i> Dashboard
            </button>
        </div>
        
        <div class="card">
            <div class="card-header" style="background: white; border-left: 4px solid #667eea; display: flex; justify-content: space-between; align-items: center; padding-left: 1.5rem;">
                <div style="padding-left: 0.75rem;">
                    <h2 style="margin: 0; color: #333;">${category.name}</h2>
                    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;">${athletes.length} membri</p>
                </div>
                <button class="btn btn-primary" onclick="editCategory(${categoryId})" style="margin-left: 1rem;">
                    <i class="bi bi-pencil"></i> Modifica Categoria
                </button>
            </div>
            
            <!-- Date Range Filter -->
            <div style="padding: 1rem; background: #f0f4ff; border-bottom: 1px solid #ddd;">
                <label style="display: inline-block; margin-right: 1rem; font-weight: 600;">📅 Filtra per Periodo:</label>
                <select id="category-date-filter" style="padding: 0.5rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem; cursor: pointer;">
                    <option value="90days">Ultimi 90 giorni</option>
                    <option value="season_2026">Stagione 2026 (Nov 2025 - Ott 2026)</option>
                    <option value="season_2025">Stagione 2025 (Nov 2024 - Ott 2025)</option>
                </select>
            </div>
            
            <!-- Tabs -->
            <div class="tabs" style="border-bottom: 1px solid #ddd; background: #f8f9fa; display: flex; gap: 0;">
                <button class="tab-btn active" data-tab="overview" onclick="switchCategoryTab('overview', ${categoryId})">
                    📊 Overview
                </button>
                <button class="tab-btn" data-tab="members" onclick="switchCategoryTab('members', ${categoryId})">
                    👥 Membri
                </button>
                <button class="tab-btn" data-tab="rankings" onclick="switchCategoryTab('rankings', ${categoryId})">
                    🏆 Rankings
                </button>
                <button class="tab-btn" data-tab="comparison" onclick="switchCategoryTab('comparison', ${categoryId})">
                    📈 Comparazione
                </button>
            </div>
            
            <!-- Tab Content -->
            <div id="category-tab-content" class="card-body" style="min-height: 400px;">
                <!-- Content will be loaded here -->
            </div>
        </div>
    `;

    // Store category and athletes globally
    window.currentCategory = category;
    window.currentCategoryAthletes = athletes;
    window.currentCategoryDateRange = { days: 90 }; // Default: last 90 days

    // Add event listener to date filter
    setTimeout(() => {
        const dateFilter = document.getElementById('category-date-filter');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                const value = e.target.value;
                if (value === '90days') {
                    window.currentCategoryDateRange = { days: 90 };
                } else if (value === 'season_2026') {
                    window.currentCategoryDateRange = { season: 2026 };
                } else if (value === 'season_2025') {
                    window.currentCategoryDateRange = { season: 2025 };
                }
                // Reload current tab with new date range
                const activeTab = document.querySelector('.tab-btn.active');
                if (activeTab) {
                    const tabName = activeTab.getAttribute('data-tab');
                    switchCategoryTab(tabName, categoryId);
                }
            });
        }
    }, 0);

    // Load default tab (overview)
    switchCategoryTab('overview', categoryId);
}

window.switchCategoryTab = function(tabName, categoryId) {
    // Track which tab is active to prevent race conditions
    window.currentCategoryActiveTab = tabName;
    
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });

    const tabContent = document.getElementById('category-tab-content');
    const category = window.currentCategory;
    const athletes = window.currentCategoryAthletes;

    if (tabName === 'overview') {
        renderCategoryOverviewTab(categoryId, category, athletes, tabContent);
    } else if (tabName === 'members') {
        renderCategoryMembersTab(categoryId, category, athletes, tabContent);
    } else if (tabName === 'rankings') {
        renderCategoryRankingsTab(categoryId, category, athletes, tabContent);
    } else if (tabName === 'comparison') {
        renderCategoryComparisonTab(categoryId, category, athletes, tabContent);
    }
};

// ========== OVERVIEW TAB ==========

async function renderCategoryOverviewTab(categoryId, category, athletes, tabContent) {
    tabContent.innerHTML = `
        <div style="padding: 1.5rem;">
            <h4>📊 Statistiche Categoria</h4>
            <p style="color: #666;">Caricamento statistiche...</p>
        </div>
    `;

    // Get current date range from global filter
    const dateRange = window.currentCategoryDateRange || { days: 90 };

    // Initialize cache if needed
    if (!window.categoryOverviewCache) {
        window.categoryOverviewCache = {};
    }
    
    // Create cache key
    const cacheKey = `${categoryId}_${JSON.stringify(dateRange)}`;
    
    // Check if data is already cached with the same date range
    let stats;
    if (window.categoryOverviewCache[cacheKey]) {
        console.log('[CATEGORIES] Using cached overview data for category', categoryId);
        stats = window.categoryOverviewCache[cacheKey];
    } else {
        console.log('[CATEGORIES] Loading fresh overview data for category', categoryId);
        stats = await calculateCategoryStatistics(athletes, dateRange);
        // Cache the loaded data
        window.categoryOverviewCache[cacheKey] = stats;
    }

    // Check if this tab is still active - prevent race condition
    if (window.currentCategoryActiveTab !== 'overview') {
        return;
    }

    let html = `
        <div style="padding: 1.5rem;">
            <!-- Summary Cards - Dati Impostati -->
            <h5 style="margin-top: 0; margin-bottom: 1rem;">📌 Dati Impostati Manualmente</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
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
                <div class="stat-card" style="background: linear-gradient(135deg, #ffeef0 0%, #ffe0e0 100%); border-left: 4px solid #ec4899;">
                    <div class="stat-label">Potenza 5s Medio</div>
                    <div class="stat-value" style="color: #ec4899;">${stats.avgPower5s} W</div>
                    <div style="font-size: 0.875rem; color: #666; margin-top: 0.5rem;">reale da dati</div>
                </div>
            </div>

            <!-- Summary Cards - Dati Calcolati dal Modello -->
            <h5 style="margin-bottom: 1rem;">📈 Dati Calcolati (OmniPD)</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;" data-calc-cards>
                <div class="stat-card" style="background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%); border-left: 4px solid #667eea;">
                    <div class="stat-label">CP Calcolato Medio</div>
                    <div class="stat-value" style="color: #667eea;">${stats.avgCalcCP} W</div>
                    <div style="font-size: 0.875rem; color: #666; margin-top: 0.5rem;">atleti con dati: ${stats.athletesWithCalcCP}</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #f0f4ff 0%, #fff0f0 100%); border-left: 4px solid #4facfe;">
                    <div class="stat-label">W' Calcolato Medio</div>
                    <div class="stat-value" style="color: #4facfe;">${stats.avgCalcWPrime} J</div>
                    <div style="font-size: 0.875rem; color: #666; margin-top: 0.5rem;">${stats.avgCalcWPrimeKg} kJ/kg</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #fff0f0 0%, #fff5f0 100%); border-left: 4px solid #fa709a;">
                    <div class="stat-label">Pmax Medio</div>
                    <div class="stat-value" style="color: #fa709a;">${stats.avgPmax} W</div>
                    <div style="font-size: 0.875rem; color: #666; margin-top: 0.5rem;">a 1s</div>
                </div>
            </div>

            <!-- Best Performances -->
            <h5 style="margin-bottom: 1rem;">🌟 Migliori Performance</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;" data-best-perf>
                ${stats.bestPerformances.map(perf => `
                    <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">${perf.label}</div>
                        <div style="font-size: 1.5rem; font-weight: 600; color: ${perf.color || '#667eea'};">${perf.value}${perf.unit || ' W'}</div>
                        <div style="font-size: 0.875rem; color: #999; margin-top: 0.25rem;">${perf.athlete}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    tabContent.innerHTML = html;
}

// ========== MEMBERS TAB ==========

async function renderCategoryMembersTab(categoryId, category, athletes, tabContent) {
    if (athletes.length === 0) {
        tabContent.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <p style="color: #666;">Nessun membro in questa categoria</p>
            </div>
        `;
        return;
    }

    // Show loading state
    tabContent.innerHTML = `
        <div style="padding: 1.5rem;">
            <h4 style="margin-bottom: 1rem;">👥 Membri della Categoria</h4>
            <div style="text-align: center; color: #666;">Caricamento dati calcolati...</div>
        </div>
    `;

    // Get current date range from global filter
    const dateRange = window.currentCategoryDateRange || { days: 90 };
    const { dateStr90, todayStr } = getCategoryNormalizedDateRange(dateRange);
    
    // Initialize cache if needed
    if (!window.categoryMembersCache) {
        window.categoryMembersCache = {};
    }
    
    // Create cache key
    const cacheKey = `${categoryId}_${JSON.stringify(dateRange)}`;
    
    // Check if data is already cached with the same date range
    let athletesWithStats;
    if (window.categoryMembersCache[cacheKey]) {
        console.log('[CATEGORIES] Using cached members data for category', categoryId);
        athletesWithStats = window.categoryMembersCache[cacheKey];
    } else {
        console.log('[CATEGORIES] Loading fresh members data for category', categoryId);
        // Load calculated statistics for each athlete
        athletesWithStats = await Promise.all(athletes.map(async (athlete) => {
            const stats = { ...athlete, eCP: null, eWPrime: null, Pmax: null };
            
            if (!athlete.api_key) {
                return stats;
            }

            try {
                const response = await fetch(`/api/athletes/${athlete.id}/power-curve?oldest=${dateStr90}&newest=${todayStr}`);
                if (!response.ok) return stats;

                const powerData = await response.json();
                const durations = powerData.secs || [];
                const watts = powerData.watts || [];

                if (durations.length === 0) return stats;

                // Calculate CP, W', and Pmax using OmniPD model
                const filtered = filterPowerCurveData(durations, watts, 1, 70, 10);
                if (filtered.selectedCount >= 4) {
                    const cpResult = calculateOmniPD(filtered.times, filtered.powers);
                    stats.eCP = Math.round(cpResult.CP);
                    stats.eWPrime = Math.round(cpResult.W_prime);
                    // Pmax at 1s from OmniPD model
                    const pmax1s = ompd_power(1, cpResult.CP, cpResult.W_prime, cpResult.Pmax, cpResult.A);
                    stats.Pmax = pmax1s ? Math.round(pmax1s) : null;
                }
                
                // Find power at 5 seconds from raw data
                const idx5s = durations.findIndex(d => d >= 5);
                if (idx5s !== -1 && watts[idx5s]) {
                    stats.power5s = Math.round(watts[idx5s]);
                } else if (durations.length > 0) {
                    // Fallback: take highest available power if no 5s data
                    stats.power5s = Math.max(...watts);
                }
            } catch (err) {
                console.warn(`Failed to load stats for athlete ${athlete.id}:`, err);
            }

            return stats;
        }));
        
        // Cache the loaded data
        window.categoryMembersCache[cacheKey] = athletesWithStats;
    }

    // Check if this tab is still active - prevent race condition
    if (window.currentCategoryActiveTab !== 'members') {
        return;
    }
    
    // Initialize sorting state for categories
    if (!window.categoryMembersSortState) {
        window.categoryMembersSortState = { field: 'name', direction: 'asc' };
    }
    
    // Function to render members table with sorting
    const renderCatMembersTable = (athletes, sortState) => {
        const sortedAthletes = [...athletes];
        sortedAthletes.sort((a, b) => {
            let aVal, bVal;
            
            switch(sortState.field) {
                case 'name':
                    aVal = `${a.first_name} ${a.last_name}`.toLowerCase();
                    bVal = `${b.first_name} ${b.last_name}`.toLowerCase();
                    break;
                case 'weight':
                    aVal = a.weight_kg || 0;
                    bVal = b.weight_kg || 0;
                    break;
                case 'cp':
                    aVal = a.cp || 0;
                    bVal = b.cp || 0;
                    break;
                case 'cp_kg':
                    aVal = (a.cp && a.weight_kg) ? a.cp / a.weight_kg : 0;
                    bVal = (b.cp && b.weight_kg) ? b.cp / b.weight_kg : 0;
                    break;
                case 'ecp':
                    aVal = a.eCP || 0;
                    bVal = b.eCP || 0;
                    break;
                case 'ecp_kg':
                    aVal = (a.eCP && a.weight_kg) ? a.eCP / a.weight_kg : 0;
                    bVal = (b.eCP && b.weight_kg) ? b.eCP / b.weight_kg : 0;
                    break;
                case 'wprime':
                    aVal = a.w_prime || 0;
                    bVal = b.w_prime || 0;
                    break;
                case 'ewprime':
                    aVal = a.eWPrime || 0;
                    bVal = b.eWPrime || 0;
                    break;
                case 'power5s':
                    aVal = a.power5s || 0;
                    bVal = b.power5s || 0;
                    break;
                case 'power5s_kg':
                    aVal = (a.power5s && a.weight_kg) ? a.power5s / a.weight_kg : 0;
                    bVal = (b.power5s && b.weight_kg) ? b.power5s / b.weight_kg : 0;
                    break;
                default:
                    return 0;
            }
            
            if (typeof aVal === 'string') {
                return sortState.direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            } else {
                return sortState.direction === 'asc' ? aVal - bVal : bVal - aVal;
            }
        });
        return sortedAthletes;
    };
    
    const getCatSortIndicator = (field) => {
        if (window.categoryMembersSortState.field !== field) return '';
        return window.categoryMembersSortState.direction === 'asc' ? ' ↑' : ' ↓';
    };
    
    window.sortCategoryMembers = (field) => {
        if (window.categoryMembersSortState.field === field) {
            window.categoryMembersSortState.direction = window.categoryMembersSortState.direction === 'asc' ? 'desc' : 'asc';
        } else {
            window.categoryMembersSortState.field = field;
            window.categoryMembersSortState.direction = 'asc';
        }
        // Re-render with cached data, don't refetch
        renderCatMembersTableOnly(window.currentCategoryId, window.currentCategory, window.currentCategoryAthletes, tabContent, athletesWithStats, window.categoryMembersSortState);
    };

    let html = `
        <div style="padding: 1.5rem;">
            <h4 style="margin-bottom: 1rem;">👥 Membri della Categoria</h4>
            <div style="background: white; border-radius: 8px; overflow-x: auto; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead style="background: #f8f9fa;">
                        <tr>
                            <th style="padding: 1rem; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" onclick="sortCategoryMembers('name')">Atleta${getCatSortIndicator('name')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" onclick="sortCategoryMembers('weight')">Peso (kg)${getCatSortIndicator('weight')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Valore impostato manualmente" onclick="sortCategoryMembers('cp')">CP (W)${getCatSortIndicator('cp')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Valore impostato manualmente" onclick="sortCategoryMembers('cp_kg')">CP (W/kg)${getCatSortIndicator('cp_kg')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Calcolato dal modello OmniPD" onclick="sortCategoryMembers('ecp')">CP calc (W)${getCatSortIndicator('ecp')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Calcolato dal modello OmniPD" onclick="sortCategoryMembers('ecp_kg')">CP calc (W/kg)${getCatSortIndicator('ecp_kg')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Valore impostato manualmente" onclick="sortCategoryMembers('wprime')">W' (J)${getCatSortIndicator('wprime')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Calcolato dal modello OmniPD" onclick="sortCategoryMembers('ewprime')">W' calc (J)${getCatSortIndicator('ewprime')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Power a 5 secondi" onclick="sortCategoryMembers('power5s')">Power 5s (W)${getCatSortIndicator('power5s')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Power a 5 secondi per kg" onclick="sortCategoryMembers('power5s_kg')">5s W/kg${getCatSortIndicator('power5s_kg')}</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">Azioni</th>
                        </tr>
                    </thead>
                    <tbody>`;
    
    // Render the table with cached data
    renderCatMembersTableOnly(categoryId, category, athletes, tabContent, athletesWithStats, window.categoryMembersSortState);
}

// Separate function to render table only, without fetching data
function renderCatMembersTableOnly(categoryId, category, athletes, tabContent, athletesWithStats, sortState) {
    // Sort athletes based on current sort state
    const sortedAthletes = [...athletesWithStats];
    sortedAthletes.sort((a, b) => {
        let aVal, bVal;
        
        switch(sortState.field) {
            case 'name':
                aVal = `${a.first_name} ${a.last_name}`.toLowerCase();
                bVal = `${b.first_name} ${b.last_name}`.toLowerCase();
                break;
            case 'weight':
                aVal = a.weight_kg || 0;
                bVal = b.weight_kg || 0;
                break;
            case 'cp':
                aVal = a.cp || 0;
                bVal = b.cp || 0;
                break;
            case 'cp_kg':
                aVal = (a.cp && a.weight_kg) ? a.cp / a.weight_kg : 0;
                bVal = (b.cp && b.weight_kg) ? b.cp / b.weight_kg : 0;
                break;
            case 'ecp':
                aVal = a.eCP || 0;
                bVal = b.eCP || 0;
                break;
            case 'ecp_kg':
                aVal = (a.eCP && a.weight_kg) ? a.eCP / a.weight_kg : 0;
                bVal = (b.eCP && b.weight_kg) ? b.eCP / b.weight_kg : 0;
                break;
            case 'wprime':
                aVal = a.w_prime || 0;
                bVal = b.w_prime || 0;
                break;
            case 'ewprime':
                aVal = a.eWPrime || 0;
                bVal = b.eWPrime || 0;
                break;
            case 'power5s':
                aVal = a.power5s || 0;
                bVal = b.power5s || 0;
                break;
            case 'power5s_kg':
                aVal = (a.power5s && a.weight_kg) ? a.power5s / a.weight_kg : 0;
                bVal = (b.power5s && b.weight_kg) ? b.power5s / b.weight_kg : 0;
                break;
            default:
                return 0;
        }
        
        if (typeof aVal === 'string') {
            return sortState.direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        } else {
            return sortState.direction === 'asc' ? aVal - bVal : bVal - aVal;
        }
    });

    let html = `
        <div style="padding: 1.5rem;">
            <h4 style="margin-bottom: 1rem;">👥 Membri della Categoria</h4>
            <div style="background: white; border-radius: 8px; overflow-x: auto; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead style="background: #f8f9fa;">
                        <tr>
                            <th style="padding: 1rem; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" onclick="sortCategoryMembers('name')">Atleta</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" onclick="sortCategoryMembers('weight')">Peso (kg)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Valore impostato manualmente" onclick="sortCategoryMembers('cp')">CP (W)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Valore impostato manualmente" onclick="sortCategoryMembers('cp_kg')">CP (W/kg)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Calcolato dal modello OmniPD" onclick="sortCategoryMembers('ecp')">CP calc (W)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Calcolato dal modello OmniPD" onclick="sortCategoryMembers('ecp_kg')">CP calc (W/kg)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Valore impostato manualmente" onclick="sortCategoryMembers('wprime')">W' (J)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Calcolato dal modello OmniPD" onclick="sortCategoryMembers('ewprime')">W' calc (J)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Power a 5 secondi" onclick="sortCategoryMembers('power5s')">Power 5s (W)</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600; cursor: pointer;" title="Power a 5 secondi per kg" onclick="sortCategoryMembers('power5s_kg')">5s W/kg</th>
                            <th style="padding: 1rem; text-align: center; border-bottom: 2px solid #ddd; font-weight: 600;">Azioni</th>
                        </tr>
                    </thead>
                    <tbody>`;

    sortedAthletes.forEach((athlete, idx) => {
        const bgColor = idx % 2 === 0 ? 'white' : '#f8f9fa';
        const cpPerKg = athlete.cp && athlete.weight_kg ? (athlete.cp / athlete.weight_kg).toFixed(2) : '-';
        const ecpPerKg = athlete.eCP && athlete.weight_kg ? (athlete.eCP / athlete.weight_kg).toFixed(2) : '-';
        const power5sPerKg = athlete.power5s && athlete.weight_kg ? (athlete.power5s / athlete.weight_kg).toFixed(2) : '-';
        
        html += `
            <tr style="background: ${bgColor}; border-bottom: 1px solid #eee;">
                <td style="padding: 1rem;">
                    <div style="font-weight: 600;">${athlete.first_name} ${athlete.last_name}</div>
                    <div style="font-size: 0.875rem; color: #666;">${athlete.gender || ''}</div>
                </td>
                <td style="padding: 1rem; text-align: center;">${athlete.weight_kg || '-'}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #667eea;">${athlete.cp || '-'}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #667eea;">${cpPerKg}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #ff6b6b;">${athlete.eCP || '-'}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #ff6b6b;">${ecpPerKg}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #43e97b;">${athlete.w_prime || '-'}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #4facfe;">${athlete.eWPrime || '-'}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #ec4899;">${athlete.power5s || '-'}</td>
                <td style="padding: 1rem; text-align: center; font-weight: 600; color: #ec4899;">${power5sPerKg}</td>
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

async function renderCategoryRankingsTab(categoryId, category, athletes, tabContent) {
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

    // Get current date range from global filter
    const dateRange = window.currentCategoryDateRange || { days: 90 };

    // Initialize cache if needed
    if (!window.categoryRankingsCache) {
        window.categoryRankingsCache = {};
    }
    
    // Create cache key
    const cacheKey = `${categoryId}_${JSON.stringify(dateRange)}`;
    
    // Check if data is already cached with the same date range
    let rankings;
    if (window.categoryRankingsCache[cacheKey]) {
        console.log('[CATEGORIES] Using cached rankings data for category', categoryId);
        rankings = window.categoryRankingsCache[cacheKey];
    } else {
        console.log('[CATEGORIES] Loading fresh rankings data for category', categoryId);
        rankings = await calculateCategoryRankings(athletesWithKeys, dateRange);
        // Cache the loaded data
        window.categoryRankingsCache[cacheKey] = rankings;
    }

    // Check if this tab is still active - prevent race condition
    if (window.currentCategoryActiveTab !== 'rankings') {
        return;
    }

    renderCategoryRankingsTable(rankings, tabContent);
}

// ========== COMPARISON TAB ==========

async function renderCategoryComparisonTab(categoryId, category, athletes, tabContent) {
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

    // Get current date range from global filter
    const dateRange = window.currentCategoryDateRange || { days: 90 };

    // Initialize cache if needed
    if (!window.categoryComparisonCache) {
        window.categoryComparisonCache = {};
    }
    
    // Create cache key
    const cacheKey = `${categoryId}_${JSON.stringify(dateRange)}`;
    
    // Check if data is already cached with the same date range
    let powerCurves;
    if (window.categoryComparisonCache[cacheKey]) {
        console.log('[CATEGORIES] Using cached comparison data for category', categoryId);
        powerCurves = window.categoryComparisonCache[cacheKey];
    } else {
        console.log('[CATEGORIES] Loading fresh comparison data for category', categoryId);
        powerCurves = await fetchAllCategoryPowerCurves(athletesWithKeys, dateRange);
        // Cache the loaded data
        window.categoryComparisonCache[cacheKey] = powerCurves;
    }

    // Check if this tab is still active - prevent race condition
    if (window.currentCategoryActiveTab !== 'comparison') {
        return;
    }

    renderCategoryPowerCurvesComparison(powerCurves, athletesWithKeys, tabContent);
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

// Helper function to normalize date range
function getCategoryNormalizedDateRange(dateRangeOpt = { days: 90 }) {
    let dateStr90, todayStr;
    if (dateRangeOpt.days) {
        // Last N days
        const today = new Date();
        const daysAgo = new Date(today.getTime() - dateRangeOpt.days * 24 * 60 * 60 * 1000);
        dateStr90 = daysAgo.toISOString().split('T')[0];
        todayStr = today.toISOString().split('T')[0];
    } else if (dateRangeOpt.season) {
        // Season: November of previous year to October of current year
        const season = dateRangeOpt.season;
        dateStr90 = `${season - 1}-11-01`;
        todayStr = `${season}-10-31`;
    } else if (dateRangeOpt.start && dateRangeOpt.end) {
        dateStr90 = dateRangeOpt.start.toISOString().split('T')[0];
        todayStr = dateRangeOpt.end.toISOString().split('T')[0];
    } else {
        // Default to last 90 days
        const today = new Date();
        const daysAgo = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
        dateStr90 = daysAgo.toISOString().split('T')[0];
        todayStr = today.toISOString().split('T')[0];
    }
    return { dateStr90, todayStr };
}

async function calculateCategoryStatistics(athletes, dateRangeOpt = { days: 90 }) {
    // Normalize date range using helper function
    const { dateStr90, todayStr } = getCategoryNormalizedDateRange(dateRangeOpt);
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

    // Calculate CP, W', Pmax average from power curves (OmniPD model, 90 days)
    let totalWPrime = 0;
    let totalWPrimeKg = 0;
    let withWPrimeCount = 0;
    let withWPrimeKgCount = 0;

    // Calculated values from OmniPD model
    let totalCalcCP = 0;
    let totalCalcWPrime = 0;
    let totalCalcWPrimeKg = 0;
    let totalPmax = 0;
    let totalPower5s = 0;
    let withCalcCPCount = 0;
    let withCalcWPrimeCount = 0;
    let withCalcWPrimeKgCount = 0;
    let withPmaxCount = 0;
    let withPower5sCount = 0;
    
    // For tracking max values
    let maxPower5s = 0;
    let maxP5sAthlete = null;
    let maxCalcCP = 0;
    let maxCalcCPAthlete = null;

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
                
                // Old method (stored in DB)
                totalWPrime += cpResult.W_prime;
                withWPrimeCount++;
                
                if (athlete.weight_kg) {
                    totalWPrimeKg += cpResult.W_prime / athlete.weight_kg / 1000;
                    withWPrimeKgCount++;
                }
                
                // New OmniPD calculated values
                totalCalcCP += cpResult.CP;
                withCalcCPCount++;
                
                totalCalcWPrime += cpResult.W_prime;
                withCalcWPrimeCount++;
                
                if (athlete.weight_kg) {
                    totalCalcWPrimeKg += cpResult.W_prime / athlete.weight_kg / 1000;
                    withCalcWPrimeKgCount++;
                }
                
                // Pmax at 1s from OmniPD model
                const pmax1s = ompd_power(1, cpResult.CP, cpResult.W_prime, cpResult.Pmax, cpResult.A);
                if (pmax1s && !isNaN(pmax1s)) {
                    totalPmax += pmax1s;
                    withPmaxCount++;
                }
                
                // Power at 5s from raw data
                const idx5s = durations.findIndex(d => d >= 5);
                let power5sValue = 0;
                if (idx5s !== -1 && watts[idx5s]) {
                    power5sValue = watts[idx5s];
                    totalPower5s += power5sValue;
                    withPower5sCount++;
                } else if (durations.length > 0) {
                    // Fallback: take highest available power if no 5s data
                    power5sValue = Math.max(...watts);
                    totalPower5s += power5sValue;
                    withPower5sCount++;
                }
                
                // Track max power 5s
                if (power5sValue > maxPower5s) {
                    maxPower5s = power5sValue;
                    maxP5sAthlete = athlete;
                }
                
                // Track max calculated CP
                if (cpResult.CP > maxCalcCP) {
                    maxCalcCP = cpResult.CP;
                    maxCalcCPAthlete = athlete;
                }
                
            } catch (err) {
                console.warn(`Failed to calculate CP for ${athlete.id}:`, err);
                console.debug(`Data available - durations: ${durations.length}, watts: ${watts.length}`, {durations, watts});
            }
        } catch (err) {
            console.warn(`Failed to load power curve for ${athlete.id}:`, err);
        }
    }

    const avgWPrime = withWPrimeCount > 0 ? Math.round(totalWPrime / withWPrimeCount) : 0;
    const avgWPrimeKg = withWPrimeKgCount > 0 ? (totalWPrimeKg / withWPrimeKgCount).toFixed(3) : '0.000';

    // Calculated values
    const avgCalcCP = withCalcCPCount > 0 ? Math.round(totalCalcCP / withCalcCPCount) : 0;
    const avgCalcWPrime = withCalcWPrimeCount > 0 ? Math.round(totalCalcWPrime / withCalcWPrimeCount) : 0;
    const avgCalcWPrimeKg = withCalcWPrimeKgCount > 0 ? (totalCalcWPrimeKg / withCalcWPrimeKgCount).toFixed(3) : '0.000';
    const avgPmax = withPmaxCount > 0 ? Math.round(totalPmax / withPmaxCount) : 0;
    const avgPower5s = withPower5sCount > 0 ? Math.round(totalPower5s / withPower5sCount) : 0;
    const athletesWithCalcCP = withCalcCPCount;

    // Best performances with colors and units
    const bestPerformances = [
        { 
            label: 'CP/kg Massima', 
            value: withCP.filter(a => a.weight_kg).length > 0 ? (Math.max(...withCP.filter(a => a.weight_kg).map(a => a.cp / a.weight_kg))).toFixed(2) : 0,
            athlete: withCP.filter(a => a.weight_kg).length > 0 ? (() => {
                const maxAthlete = withCP.filter(a => a.weight_kg).reduce((max, a) => (a.cp / a.weight_kg) > (max.cp / max.weight_kg) ? a : max);
                return `${maxAthlete.first_name} ${maxAthlete.last_name}`;
            })() : '-',
            color: '#ff6b6b',
            unit: ' W/kg'
        },
        { 
            label: 'CP Calcolato Massima', 
            value: maxCalcCP > 0 ? Math.round(maxCalcCP) : 0,
            athlete: maxCalcCPAthlete ? `${maxCalcCPAthlete.first_name} ${maxCalcCPAthlete.last_name}` : '-',
            color: '#667eea',
            unit: ' W'
        },
        { 
            label: 'W\' Massimo (impostato)', 
            value: withCP.length > 0 ? Math.max(...athletes.map(a => a.w_prime || 0)) : 0,
            athlete: athletes.length > 0 ? (() => {
                const athlete = athletes.reduce((max, a) => (a.w_prime || 0) > (max.w_prime || 0) ? a : max);
                return athlete.w_prime ? `${athlete.first_name} ${athlete.last_name}` : '-';
            })() : '-',
            color: '#43e97b',
            unit: ' J'
        },
        { 
            label: 'Potenza 5s Massima', 
            value: maxPower5s > 0 ? Math.round(maxPower5s) : 0,
            athlete: maxP5sAthlete ? `${maxP5sAthlete.first_name} ${maxP5sAthlete.last_name}` : '-',
            color: '#ec4899',
            unit: ' W'
        }
    ]

    return {
        avgCP,
        avgCPkg,
        avgWPrime,
        avgWPrimeKg,
        avgWeight,
        avgCalcCP,
        avgCalcWPrime,
        avgCalcWPrimeKg,
        avgPmax,
        avgPower5s,
        athletesWithCalcCP,
        bestPerformances
    };
}

async function calculateCategoryRankings(athletes, dateRangeOpt = { days: 90 }) {
    const { dateStr90, todayStr } = getCategoryNormalizedDateRange(dateRangeOpt);

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

function renderCategoryRankingsTable(rankings, tabContent) {
    const durations = [
        { key: 'mmp_1s', label: '1s', name: '1 secondo' },
        { key: 'mmp_5s', label: '5s', name: '5 secondi' },
        { key: 'mmp_3m', label: '3m', name: '3 minuti' },
        { key: 'mmp_6m', label: '6m', name: '6 minuti' },
        { key: 'mmp_12m', label: '12m', name: '12 minuti' }
    ];

    let html = `
        <div style="padding: 1.5rem;">
            <h4 style="margin-bottom: 1.5rem;">🏆 Rankings della Categoria</h4>
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

async function fetchAllCategoryPowerCurves(athletes, dateRangeOpt = { days: 90 }) {
    const { dateStr90, todayStr } = getCategoryNormalizedDateRange(dateRangeOpt);

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

function renderCategoryPowerCurvesComparison(powerCurves, athletes, tabContent) {
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
            <h4 style="margin-bottom: 1.5rem;">📈 Comparazione Power Curves (Ultimi 90 giorni)</h4>
            
            <div style="margin-bottom: 2rem;">
                <h5 style="margin-bottom: 1rem;">Potenza Assoluta (W)</h5>
                <div id="category-comparison-chart-absolute" style="width: 100%; height: 500px; background: white; border: 1px solid #e0e0e0; border-radius: 8px;"></div>
            </div>
            
            <div>
                <h5 style="margin-bottom: 1rem;">Potenza per Kg (W/kg)</h5>
                <div id="category-comparison-chart-per-kg" style="width: 100%; height: 500px; background: white; border: 1px solid #e0e0e0; border-radius: 8px;"></div>
            </div>
        </div>
    `;

    tabContent.innerHTML = html;

    // Render comparison charts
    renderCategoryComparisonCharts(powerCurves);
}

function renderCategoryComparisonCharts(powerCurves) {
    // Colors for each athlete
    const colors = ['#667eea', '#f093fb', '#4facfe', '#fa709a', '#43e97b', '#38f9d7', '#f6d365', '#fda085'];

    const baseDurations = (powerCurves[0]?.data?.secs || []).filter(d => d > 0);
    const getNearestWatts = (durations, watts, target) => {
        if (!durations.length || !watts.length) return 0;
        const idx = durations.findIndex(d => d >= target);
        if (idx !== -1) return watts[idx] || 0;
        return watts[watts.length - 1] || 0;
    };

    // Calculate min/max for axes
    const allDurations = baseDurations.length > 0
        ? baseDurations
        : powerCurves.flatMap(pc => (pc.data.secs || []).filter(d => d > 0));
    const minDuration = Math.min(...allDurations.filter(d => d > 0));
    const maxDuration = Math.max(...allDurations.filter(d => d > 0));
    const logMin = Math.log10(minDuration * 0.95);
    const logMax = Math.log10(maxDuration * 1.05);

    // ===== CHART 1: Absolute Power =====
    const seriesAbsolute = powerCurves.map((pc) => {
        const durations = pc.data.secs || [];
        const watts = pc.data.watts || [];
        const sourceDurations = baseDurations.length > 0 ? baseDurations : durations;

        const seriesData = sourceDurations.map((sec) => ({
            x: Math.log10(Math.max(sec, 1)),
            y: getNearestWatts(durations, watts, sec),
            rawX: sec
        }));

        return {
            name: `${pc.athlete.first_name} ${pc.athlete.last_name}`,
            data: seriesData
        };
    });

    const optionsAbsolute = {
        series: seriesAbsolute,
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

    // ===== CHART 2: Power per Kg =====
    const seriesPerKg = powerCurves.map((pc) => {
        const durations = pc.data.secs || [];
        const watts = pc.data.watts || [];
        const weight = pc.athlete.weight_kg || 1;
        const sourceDurations = baseDurations.length > 0 ? baseDurations : durations;

        const seriesData = sourceDurations.map((sec) => ({
            x: Math.log10(Math.max(sec, 1)),
            y: getNearestWatts(durations, watts, sec) / weight,
            rawX: sec
        }));

        return {
            name: `${pc.athlete.first_name} ${pc.athlete.last_name}`,
            data: seriesData
        };
    });

    const optionsPerKg = {
        series: seriesPerKg,
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
                text: 'Potenza (W/kg)',
                style: {
                    fontSize: '14px',
                    fontWeight: 600
                }
            },
            labels: {
                formatter: function(value) {
                    return value.toFixed(1) + 'W/kg';
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
                    return value.toFixed(2) + ' W/kg';
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

    // Render charts
    if (window.categoryComparisonChartAbsolute) {
        window.categoryComparisonChartAbsolute.destroy();
    }
    if (window.categoryComparisonChartPerKg) {
        window.categoryComparisonChartPerKg.destroy();
    }

    const chartAbsolute = new ApexCharts(document.querySelector("#category-comparison-chart-absolute"), optionsAbsolute);
    chartAbsolute.render();
    window.categoryComparisonChartAbsolute = chartAbsolute;

    const chartPerKg = new ApexCharts(document.querySelector("#category-comparison-chart-per-kg"), optionsPerKg);
    chartPerKg.render();
    window.categoryComparisonChartPerKg = chartPerKg;
}

// ========== CRUD OPERATIONS ==========

window.showCreateCategoryDialog = function() {
    createModal(
        'Nuova Categoria',
        `
        <div class="form-group">
            <label class="form-label">Nome Categoria</label>
            <input type="text" id="category-name" class="form-input" placeholder="Es. U23" required>
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
                onclick: 'createCategory()'
            }
        ]
    );
};

window.createCategory = async function() {
    const name = document.getElementById('category-name').value.trim();
    
    if (!name) {
        showToast('Inserisci un nome per la categoria', 'warning');
        return;
    }
    
    try {
        showLoading();
        await api.createCategory({ name });
        showToast('Categoria creata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderCategoriesPage();
    } catch (error) {
        showToast('Errore nella creazione della categoria: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

// ========== CRUD OPERATIONS ==========

window.showCreateCategoryDialog = function() {
    createModal(
        'Nuova Categoria',
        `
        <div class="form-group">
            <label class="form-label">Nome Categoria</label>
            <input type="text" id="category-name" class="form-input" placeholder="Es. U23" required>
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
                onclick: 'createCategory()'
            }
        ]
    );
};

window.createCategory = async function() {
    const name = document.getElementById('category-name').value.trim();
    
    if (!name) {
        showToast('Inserisci un nome per la categoria', 'warning');
        return;
    }
    
    try {
        showLoading();
        await api.createCategory({ name });
        showToast('Categoria creata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.backToCategoriesDashboard();
        window.renderCategoriesPage();
    } catch (error) {
        showToast('Errore nella creazione della categoria: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.editCategory = async function(categoryId) {
    try {
        const category = await api.getCategory(categoryId);
        
        createModal(
            'Modifica Categoria',
            `
            <div class="form-group">
                <label class="form-label">Nome Categoria</label>
                <input type="text" id="category-name-edit" class="form-input" value="${category.name}" required>
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
                    onclick: `updateCategory(${categoryId})`
                }
            ]
        );
    } catch (error) {
        showToast('Errore nel caricamento dei dati', 'error');
    }
};

window.updateCategory = async function(categoryId) {
    const name = document.getElementById('category-name-edit').value.trim();
    
    if (!name) {
        showToast('Inserisci un nome per la categoria', 'warning');
        return;
    }
    
    try {
        showLoading();
        await api.updateCategory(categoryId, { name });
        showToast('Categoria aggiornata con successo', 'success');
        document.querySelector('.modal-overlay').remove();
        window.renderCategoriesPage();
    } catch (error) {
        showToast('Errore nell\'aggiornamento: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};

window.deleteCategoryConfirm = function(categoryId) {
    createModal(
        '⚠️ Conferma Eliminazione',
        '<p>Sei sicuro di voler eliminare questa categoria? Questa azione non può essere annullata.</p>',
        [
            {
                label: 'Annulla',
                class: 'btn-secondary',
                onclick: 'this.closest(".modal-overlay").remove()'
            },
            {
                label: 'Elimina Categoria',
                class: 'btn-danger',
                onclick: `deleteCategoryExecute(${categoryId})`
            }
        ]
    );
};

window.deleteCategoryExecute = async function(categoryId) {
    try {
        showLoading();
        await api.deleteCategory(categoryId);
        showToast('Categoria eliminata con successo', 'success');
        document.querySelector('.modal-overlay')?.remove();
        window.backToCategoriesDashboard();
        window.renderCategoriesPage();
    } catch (error) {
        showToast('Errore nell\'eliminazione: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
};
