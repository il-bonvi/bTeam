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

        try {
            const response = await fetch(url, config);
            let data;
            
            try {
                data = await response.json();
            } catch (jsonError) {
                // If JSON parsing fails, get the text response
                const text = await response.text();
                console.error('Failed to parse JSON response:', text);
                throw new Error(`Server returned invalid JSON: ${text.substring(0, 100)}`);
            }

            if (!response.ok) {
                throw new Error(data.detail || data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
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
    async getAthletes(teamId = null) {
        const params = teamId ? `?team_id=${teamId}` : '';
        return this.request(`/athletes/${params}`);
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

    async removeAthleteFromRace(raceId, athleteId) {
        return this.request(`/races/${raceId}/athletes/${athleteId}`, {
            method: 'DELETE',
        });
    }

    async getRaceAthletes(raceId) {
        return this.request(`/races/${raceId}/athletes`);
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
        return this.request('/sync/wellness', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async pushRace(raceId, apiKey) {
        return this.request('/sync/push-race', {
            method: 'POST',
            body: JSON.stringify({ race_id: raceId, api_key: apiKey }),
        });
    }

    async getPowerCurve(athleteId, apiKey, daysBack = 90) {
        return this.request(`/sync/power-curve/${athleteId}?api_key=${apiKey}&days_back=${daysBack}`);
    }
}

// Create global API client instance
window.api = new APIClient();
