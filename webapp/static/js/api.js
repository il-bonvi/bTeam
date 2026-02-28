/**
 * bTeam WebApp - API Client
 * Handles all API communication with the backend
 */

const API_BASE_URL = window.location.origin + '/api';

class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };
        
        const response = await fetch(url, config);
        let data;
        
        // Read body once to avoid "already consumed" error
        const text = await response.text();
        
        try {
            data = text ? JSON.parse(text) : {};
        } catch (jsonError) {
            console.error('Failed to parse JSON response:', text);
            throw new Error(`Server returned invalid JSON: ${text.substring(0, 100)}`);
        }

        if (!response.ok) {
            let errorMessage = 'Request failed';
            
            // Handle different error response formats
            if (typeof data.detail === 'string') {
                errorMessage = data.detail;
            } else if (typeof data.message === 'string') {
                errorMessage = data.message;
            } else if (Array.isArray(data.detail)) {
                // Handle array of validation errors
                errorMessage = data.detail
                    .map(item => typeof item === 'string' ? item : JSON.stringify(item))
                    .join('; ');
            } else if (Array.isArray(data.message)) {
                errorMessage = data.message
                    .map(item => typeof item === 'string' ? item : JSON.stringify(item))
                    .join('; ');
            } else if (typeof data.detail === 'object' && data.detail !== null) {
                errorMessage = JSON.stringify(data.detail);
            }
            
            throw new Error(errorMessage);
        }

        return data;
    }

    // Teams
    async getTeams() {
        return this.request('/teams/');
    }

    async getTeam(id) {
        return this.request(`/teams/${id}`);
    }

    async createTeam(data) {
        return this.request('/teams/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateTeam(id, data) {
        return this.request(`/teams/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteTeam(id) {
        return this.request(`/teams/${id}`, {
            method: 'DELETE',
        });
    }

    // Athletes
    async getAthletes(teamId = null, categoryId = null) {
        const params = new URLSearchParams();
        if (teamId) params.append('team_id', teamId);
        if (categoryId) params.append('category_id', categoryId);
        const query = params.toString();
        return this.request(`/athletes/${query ? `?${query}` : ''}`);
    }

    async getAthlete(id) {
        return this.request(`/athletes/${id}`);
    }

    async createAthlete(data) {
        return this.request('/athletes/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateAthlete(id, data) {
        return this.request(`/athletes/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteAthlete(id) {
        return this.request(`/athletes/${id}`, {
            method: 'DELETE',
        });
    }

    async getAthletePowerCurve(id, oldest = null, newest = null) {
        let url = `/athletes/${id}/power-curve`;
        const params = [];
        if (oldest) params.push(`oldest=${oldest}`);
        if (newest) params.push(`newest=${newest}`);
        if (params.length > 0) url += `?${params.join('&')}`;
        return this.request(url);
    }

    // Seasons
    async getAthleteSeasons(athleteId) {
        return this.request(`/athletes/${athleteId}/seasons`);
    }

    async createSeason(athleteId, data) {
        return this.request(`/athletes/${athleteId}/seasons`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateSeason(seasonId, data) {
        return this.request(`/athletes/seasons/${seasonId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteSeason(seasonId) {
        return this.request(`/athletes/seasons/${seasonId}`, {
            method: 'DELETE'
        });
    }

    // Activities
    async getActivities(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request(`/activities/?${params}`);
    }

    async getActivity(id) {
        return this.request(`/activities/${id}`);
    }

    async createActivity(data) {
        return this.request('/activities/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async deleteActivity(id) {
        return this.request(`/activities/${id}`, {
            method: 'DELETE',
        });
    }

    async getAthleteStats(athleteId) {
        return this.request(`/activities/athlete/${athleteId}/stats`);
    }

    // Races
    async getRaces() {
        return this.request('/races/');
    }

    async getRace(id) {
        return this.request(`/races/${id}`);
    }

    async createRace(data) {
        return this.request('/races/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateRace(id, data) {
        return this.request(`/races/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteRace(id) {
        return this.request(`/races/${id}`, {
            method: 'DELETE',
        });
    }

    async addAthleteToRace(raceId, data) {
        return this.request(`/races/${raceId}/athletes`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateAthleteInRace(raceId, athleteId, data) {
        return this.request(`/races/${raceId}/athletes/${athleteId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async removeAthleteFromRace(raceId, athleteId) {
        return this.request(`/races/${raceId}/athletes/${athleteId}`, {
            method: 'DELETE',
        });
    }

    async getRaceAthletes(raceId) {
        return this.request(`/races/${raceId}/athletes`);
    }

    // Stages
    async getStages(raceId) {
        return this.request(`/races/${raceId}/stages`);
    }

    async getStage(raceId, stageId) {
        return this.request(`/races/${raceId}/stages/${stageId}`);
    }

    async createStage(raceId, data) {
        return this.request(`/races/${raceId}/stages`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateStage(raceId, stageId, data) {
        return this.request(`/races/${raceId}/stages/${stageId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteStage(raceId, stageId) {
        return this.request(`/races/${raceId}/stages/${stageId}`, {
            method: 'DELETE',
        });
    }

    // Wellness
    async getWellness(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request(`/wellness/?${params}`);
    }

    async getWellnessEntry(id) {
        return this.request(`/wellness/${id}`);
    }

    async createWellness(data) {
        return this.request('/wellness/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateWellness(id, data) {
        return this.request(`/wellness/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteWellness(id) {
        return this.request(`/wellness/${id}`, {
            method: 'DELETE',
        });
    }

    async getLatestWellness(athleteId) {
        return this.request(`/wellness/athlete/${athleteId}/latest`);
    }

    // Sync
    async testConnection(apiKey) {
        return this.request('/sync/test-connection', {
            method: 'POST',
            body: JSON.stringify({ api_key: apiKey }),
        });
    }

    async syncActivities(data) {
        return this.request('/sync/activities', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async syncWellness(data) {
        const result = await this.request('/sync/wellness', {
            method: 'POST',
            body: JSON.stringify(data),
        });
        return result;
    }

    async pushRace(raceId) {
        return this.request('/sync/push-race', {
            method: 'POST',
            body: JSON.stringify({ race_id: raceId }),
        });
    }

    async syncAthleteMetrics(athleteId, apiKey) {
        return this.request(`/sync/athlete-metrics`, {
            method: 'POST',
            body: JSON.stringify({ athlete_id: athleteId, api_key: apiKey }),
        });
    }

    async getPowerCurve(athleteId, apiKey, daysBack = 90) {
        return this.request(`/sync/power-curve/${athleteId}?api_key=${apiKey}&days_back=${daysBack}`);
    }

    // Categories
    async getCategories() {
        return this.request('/categories/');
    }

    async getCategory(id) {
        return this.request(`/categories/${id}`);
    }

    async createCategory(data) {
        return this.request('/categories/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateCategory(id, data) {
        return this.request(`/categories/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteCategory(id) {
        return this.request(`/categories/${id}`, {
            method: 'DELETE',
        });
    }
}

// Create global API client instance
window.api = new APIClient();
