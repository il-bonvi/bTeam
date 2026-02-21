/**
 * bTeam WebApp - Main Application
 */

// Page modules
const pages = {
    dashboard: {
        title: 'Dashboard',
        load: loadDashboard
    },
    teams: {
        title: 'Gestione Squadre',
        load: loadTeams
    },
    categories: {
        title: 'Gestione Categorie',
        load: loadCategories
    },
    athletes: {
        title: 'Gestione Atleti',
        load: loadAthletes
    },
    activities: {
        title: 'Attività',
        load: loadActivities
    },
    races: {
        title: 'Gestione Gare',
        load: loadRaces
    },
    wellness: {
        title: 'Wellness',
        load: loadWellness
    },
    sync: {
        title: 'Sincronizzazione Intervals.icu',
        load: loadSync
    }
};

// Current page state
let currentPage = 'dashboard';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    loadPage('dashboard');
});

// Setup navigation
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.getAttribute('data-page');
            
            // Update active state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Load page
            loadPage(page);
        });
    });
}

// Load page content
async function loadPage(pageName) {
    currentPage = pageName;
    const page = pages[pageName];
    
    if (!page) {
        console.error('Page not found:', pageName);
        return;
    }
    
    // Update title
    document.getElementById('page-title').textContent = page.title;
    
    // Load content
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = '<div class="text-center"><div class="spinner"></div></div>';
    
    try {
        await page.load();
    } catch (error) {
        console.error('Error loading page:', error);
        contentArea.innerHTML = `
            <div class="card">
                <p style="color: var(--danger-color);">
                    <i class="bi bi-exclamation-circle"></i> 
                    Errore nel caricamento della pagina: ${error.message}
                </p>
            </div>
        `;
    }
}

// ============================================
// DASHBOARD
// ============================================
async function loadDashboard() {
    const contentArea = document.getElementById('content-area');
    
    try {
        showLoading();
        
        // Fetch data
        const [teams, athletes, activities, races] = await Promise.all([
            api.getTeams(),
            api.getAthletes(),
            api.getActivities({ limit: 10 }),
            api.getRaces()
        ]);
        
        contentArea.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon primary">
                        <i class="bi bi-people-fill"></i>
                    </div>
                    <div class="stat-content">
                        <h3>${teams.length}</h3>
                        <p>Squadre</p>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon success">
                        <i class="bi bi-person-circle"></i>
                    </div>
                    <div class="stat-content">
                        <h3>${athletes.length}</h3>
                        <p>Atleti</p>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon warning">
                        <i class="bi bi-activity"></i>
                    </div>
                    <div class="stat-content">
                        <h3>${activities.length}</h3>
                        <p>Attività Recenti</p>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon info">
                        <i class="bi bi-flag-fill"></i>
                    </div>
                    <div class="stat-content">
                        <h3>${races.length}</h3>
                        <p>Gare Pianificate</p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Attività Recenti</h3>
                    <button class="btn btn-primary" onclick="loadPage('activities')">
                        <i class="bi bi-eye"></i> Vedi Tutte
                    </button>
                </div>
                <div id="recent-activities"></div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Prossime Gare</h3>
                    <button class="btn btn-primary" onclick="loadPage('races')">
                        <i class="bi bi-eye"></i> Vedi Tutte
                    </button>
                </div>
                <div id="upcoming-races"></div>
            </div>
        `;
        
        // Render recent activities
        const recentActivitiesHtml = createTable(
            [
                { key: 'athlete_name', label: 'Atleta' },
                { key: 'title', label: 'Titolo' },
                { key: 'activity_date', label: 'Data', format: formatDate },
                { key: 'distance_km', label: 'Distanza (km)', format: v => formatNumber(v, 1) },
                { key: 'duration_minutes', label: 'Durata', format: formatDuration },
            ],
            activities
        );
        document.getElementById('recent-activities').innerHTML = recentActivitiesHtml;
        
        // Render upcoming races
        const upcomingRacesHtml = createTable(
            [
                { key: 'name', label: 'Nome' },
                { key: 'race_date', label: 'Data', format: formatDate },
                { key: 'distance_km', label: 'Distanza (km)' },
                { key: 'category', label: 'Categoria' },
            ],
            races
        );
        document.getElementById('upcoming-races').innerHTML = upcomingRacesHtml;
        
    } catch (error) {
        showToast('Errore nel caricamento del dashboard', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
}

// Load other pages from modules
async function loadTeams() {
    if (typeof window.renderTeamsPage !== 'function') {
        const script = document.createElement('script');
        script.src = '/modules/teams/teams.js';
        document.body.appendChild(script);
        await new Promise(resolve => {
            script.onload = resolve;
        });
    }
    
    if (typeof window.renderTeamsPage === 'function') {
        window.renderTeamsPage();
    }
}

async function loadCategories() {
    if (typeof window.renderCategoriesPage !== 'function') {
        const script = document.createElement('script');
        script.src = '/modules/categories/categories.js';
        document.body.appendChild(script);
        await new Promise(resolve => {
            script.onload = resolve;
        });
    }
    
    if (typeof window.renderCategoriesPage === 'function') {
        window.renderCategoriesPage();
    }
}

async function loadAthletes() {
    const script = document.createElement('script');
    script.src = '/modules/athletes/athletes.js';
    document.body.appendChild(script);
    
    await new Promise(resolve => {
        script.onload = resolve;
    });
    
    if (typeof window.renderAthletesPage === 'function') {
        window.renderAthletesPage();
    }
}

async function loadActivities() {
    const script = document.createElement('script');
    script.src = '/modules/activities/activities.js';
    document.body.appendChild(script);
    
    await new Promise(resolve => {
        script.onload = resolve;
    });
    
    if (typeof window.renderActivitiesPage === 'function') {
        window.renderActivitiesPage();
    }
}

async function loadRaces() {
    // Races module is already loaded in HTML, just call the render function
    if (typeof window.renderRacesPage === 'function') {
        await window.renderRacesPage();
    } else {
        console.error('Races module not loaded');
    }
}

async function loadWellness() {
    const script = document.createElement('script');
    script.src = '/modules/wellness/wellness.js';
    document.body.appendChild(script);
    
    await new Promise(resolve => {
        script.onload = resolve;
    });
    
    if (typeof window.renderWellnessPage === 'function') {
        window.renderWellnessPage();
    }
}

async function loadSync() {
    const script = document.createElement('script');
    script.src = '/modules/sync/sync.js';
    document.body.appendChild(script);
    
    await new Promise(resolve => {
        script.onload = resolve;
    });
    
    if (typeof window.renderSyncPage === 'function') {
        window.renderSyncPage();
    }
}
