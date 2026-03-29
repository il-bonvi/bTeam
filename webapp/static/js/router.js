/**
 * bTeam Router - Client-side routing with browser history support
 * Enables back/forward navigation and bookmarkable URLs
 */

const Router = {
    // Route configuration
    routes: {
        'dashboard': { title: 'Dashboard', page: 'dashboard' },
        'teams': { title: 'Gestione Squadre', page: 'teams' },
        'categories': { title: 'Gestione Categorie', page: 'categories' },
        'athletes': { title: 'Gestione Atleti', page: 'athletes' },
        'activities': { title: 'Attività', page: 'activities' },
        'races': { title: 'Gestione Gare', page: 'races' },
        'wellness': { title: 'Wellness', page: 'wellness' },
        'sync': { title: 'Sincronizzazione Intervals.icu', page: 'sync' }
    },

    // Initialize router
    init() {
        // Handle popstate (back/forward buttons)
        window.addEventListener('popstate', (e) => {
            this.loadFromState(e.state);
        });

        // Load initial page from URL
        const path = this.getCurrentPath();
        if (path === '/' || path === '') {
            this.navigate('dashboard', null, true); // Use replaceState for initial load
        } else {
            this.loadFromPath(path);
        }
    },

    // Get current path from URL
    getCurrentPath() {
        const url = new URL(window.location.href);
        return url.pathname.replace(/^\/app\/?/, '').replace(/\/$/, '') || '/';
    },

    // Parse path into route and params
    parsePath(path) {
        const parts = path.split('/').filter(p => p);
        
        if (parts.length === 0) {
            return { page: 'dashboard' };
        }

        const page = parts[0];
        const params = {};

        // Handle detail views (e.g., /athletes/123)
        if (parts.length > 1) {
            const id = parseInt(parts[1]);
            if (!isNaN(id)) {
                params.id = id;
            }
        }

        return { page, params };
    },

    // Load page from current URL path
    async loadFromPath(path) {
        const { page, params } = this.parsePath(path);
        
        if (!this.routes[page]) {
            // Unknown route, go to dashboard
            this.navigate('dashboard', null, true); // use replaceState for first load
            return;
        }

        // Use replaceState for initial page load to avoid duplicate history entries
        const state = { page, params: params.id ? { id: params.id } : {} };
        const url = this.buildUrl(page, params.id || null);
        window.history.replaceState(state, '', url);

        await this.loadPage(page, params);
    },

    // Load from state object (used by popstate)
    async loadFromState(state) {
        if (!state) {
            // No state available (e.g., initial history entry). Derive route from URL.
            const path = this.getCurrentPath();
            await this.loadFromPath(path);
            return;
        }

        await this.loadPage(state.page, state.params || {});
    },

    // Build URL for a page and optional id
    buildUrl(page, id = null) {
        let url = `/app/${page}`;
        if (id !== null) {
            url += `/${id}`;
        }
        return url;
    },

    // Navigate to a page with optional id
    async navigate(page, id = null, replace = false) {
        if (!this.routes[page]) {
            console.error('Unknown page:', page);
            return;
        }

        const params = id !== null ? { id } : {};
        const url = this.buildUrl(page, id);
        const state = { page, params };

        // Update browser history
        if (replace) {
            window.history.replaceState(state, '', url);
        } else {
            window.history.pushState(state, '', url);
        }

        // Load the page
        await this.loadPage(page, params);
    },

    // Load page content
    async loadPage(page, params = {}) {
        const route = this.routes[page];
        
        // Show top-bar (it may have been hidden by detail views)
        const topBar = document.querySelector('.top-bar');
        if (topBar) {
            topBar.style.display = '';
        }
        
        // Update sidebar
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-page') === page) {
                item.classList.add('active');
            }
        });

        // Update page title
        document.getElementById('page-title').textContent = route.title;

        // Set global state for modules
        window.currentPage = page;
        
        // Handle detail views
        if (params.id !== undefined) {
            switch (page) {
                case 'athletes':
                    window.currentAthleteView = params.id;
                    break;
                case 'races':
                    window.currentRaceView = params.id;
                    break;
                case 'teams':
                    window.currentTeamView = params.id;
                    break;
                case 'activities':
                    window.currentActivityView = params.id;
                    break;
            }
        } else {
            // Reset detail views for list pages
            window.currentAthleteView = null;
            window.currentRaceView = null;
            window.currentTeamView = null;
            window.currentActivityView = null;
        }

        // Load page using existing pages object
        if (pages[page] && pages[page].load) {
            const contentArea = document.getElementById('content-area');
            contentArea.innerHTML = '<div class="text-center"><div class="spinner"></div></div>';
            
            try {
                await pages[page].load();
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
    }
};

// Helper function for module navigation (used in onclick handlers)
window.navigateTo = function(page, id = null) {
    Router.navigate(page, id).catch(err => console.error('Navigation error:', err));
};

// Helper function to navigate to detail view (used by modules)
window.navigateToDetail = function(page, id) {
    Router.navigate(page, id).catch(err => console.error('Navigation error:', err));
};

// Helper function to go back (maintains history)
window.goBack = function() {
    window.history.back();
};
