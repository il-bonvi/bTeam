/**
 * Races GPX Module - GPX/FIT/TCX import and map display
 * Handles file import, parsing, distance calculation, and Leaflet map visualization
 */

// Use global state from races-main.js or initialize if needed
window.gpxTraceData = window.gpxTraceData || null;

/**
 * Handle GPX file import
 */
window.handleGpxImport = function(event) {
    const file = event?.target?.files[0];
    if (!file) {
        // Try from create dialog
        const createFileInput = document.getElementById('gpx-file');
        if (createFileInput?.files?.length > 0) {
            processGpxFile(createFileInput.files[0]);
        }
        return;
    }
    
    processGpxFile(file);
};

/**
 * Process GPX file upload
 */
function processGpxFile(file) {
    // Update filename display
    const filenameDisplay = document.getElementById('gpx-filename');
    if (filenameDisplay) {
        filenameDisplay.textContent = file.name;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        parseGpxFile(content, file.name);
    };
    reader.readAsText(file);
}

/**
 * Parse GPX file content and extract track data
 */
function parseGpxFile(content, filename) {
    try {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(content, 'text/xml');
        
        // Check for parsing errors
        const parserError = xmlDoc.querySelector('parsererror');
        if (parserError) {
            showToast('Errore nel parsing del file GPX', 'error');
            return;
        }
        
        // Find trackpoints
        const trackpoints = xmlDoc.querySelectorAll('trkpt');
        if (trackpoints.length === 0) {
            showToast('Nessun trackpoint trovato nel file', 'warning');
            return;
        }
        
        const coordinates = [];
        let totalDistance = 0;
        let elevationGain = 0;
        let prevElevation = null;
        let prevLat = null;
        let prevLon = null;
        
        // Process each trackpoint
        trackpoints.forEach(point => {
            const lat = parseFloat(point.getAttribute('lat'));
            const lon = parseFloat(point.getAttribute('lon'));
            const eleNode = point.querySelector('ele');
            const elevation = eleNode ? parseFloat(eleNode.textContent) : null;
            
            coordinates.push([lat, lon]);
            
            // Calculate distance
            if (prevLat !== null && prevLon !== null) {
                totalDistance += calculateDistance(prevLat, prevLon, lat, lon);
            }
            
            // Calculate elevation gain
            if (elevation !== null) {
                if (prevElevation !== null) {
                    const diff = elevation - prevElevation;
                    if (diff > 0) {
                        elevationGain += diff;
                    }
                }
                prevElevation = elevation;
            }
            
            prevLat = lat;
            prevLon = lon;
        });
        
        // Store trace data globally
        window.gpxTraceData = { coordinates, totalDistance, elevationGain };
        
        // Update form fields in create dialog
        updateCreateFormFromGpx(totalDistance, elevationGain);
        
        // Update form fields in detail dialog
        updateDetailFormFromGpx(totalDistance, elevationGain);
        
        // Display the map
        displayGpxMap(coordinates);
        
        // Update predictions
        if (typeof updateCreateRacePredictions === 'function') {
            updateCreateRacePredictions();
        }
        if (typeof updateDetailPredictions === 'function') {
            updateDetailPredictions();
        }
        
        showToast(`✅ Traccia importata: ${totalDistance.toFixed(1)}km, ${Math.round(elevationGain)}m D+`, 'success');
        
    } catch (error) {
        console.error('Error parsing GPX:', error);
        showToast('Errore nell\'elaborazione del file: ' + error.message, 'error');
    }
}

/**
 * Update create form fields from GPX data
 */
function updateCreateFormFromGpx(totalDistance, elevationGain) {
    const distanceEl = document.getElementById('race-distance');
    const elevationEl = document.getElementById('race-elevation');
    const gpxDistanceEl = document.getElementById('gpx-distance');
    const gpxElevationEl = document.getElementById('gpx-elevation');
    const gpxPreviewEl = document.getElementById('gpx-preview');
    
    if (totalDistance > 0 && distanceEl) {
        distanceEl.value = totalDistance.toFixed(1);
    }
    if (elevationGain > 0 && elevationEl) {
        elevationEl.value = Math.round(elevationGain);
    }
    
    // Update preview display
    if (gpxDistanceEl) {
        gpxDistanceEl.textContent = totalDistance.toFixed(1) + ' km';
    }
    if (gpxElevationEl) {
        gpxElevationEl.textContent = Math.round(elevationGain) + ' m';
    }
    if (gpxPreviewEl) {
        gpxPreviewEl.style.display = 'block';
    }
}

/**
 * Update detail form fields from GPX data
 */
function updateDetailFormFromGpx(totalDistance, elevationGain) {
    const detailDistanceEl = document.getElementById('detail-distance');
    const detailElevationEl = document.getElementById('detail-elevation');
    
    if (totalDistance > 0 && detailDistanceEl) {
        detailDistanceEl.value = totalDistance.toFixed(1);
    }
    if (elevationGain > 0 && detailElevationEl) {
        detailElevationEl.value = Math.round(elevationGain);
    }
}

/**
 * Calculate distance between two GPS coordinates using Haversine formula
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

/**
 * Display GPX track on Leaflet map
 */
function displayGpxMap(coordinates) {
    if (coordinates.length === 0) return;
    
    // Find map container (different IDs for create vs detail)
    let mapContainer = document.getElementById('map-container');
    if (!mapContainer) {
        mapContainer = document.getElementById('gpx-map');
    }
    if (!mapContainer) return;
    
    mapContainer.innerHTML = '<div id="leaflet-map" style="width: 100%; height: 100%;"></div>';
    
    setTimeout(() => {
        try {
            const map = L.map('leaflet-map').setView(coordinates[0], 13);
            
            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);
            
            // Add track polyline
            L.polyline(coordinates, {
                color: '#ff6b35',
                weight: 4,
                opacity: 0.8
            }).addTo(map);
            
            // Add start marker (green)
            L.marker(coordinates[0], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                })
            }).addTo(map).bindPopup('<strong>🏁 Partenza</strong>');
            
            // Add finish marker (red)
            L.marker(coordinates[coordinates.length - 1], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                })
            }).addTo(map).bindPopup('<strong>🏆 Arrivo</strong>');
            
            // Fit map to track bounds
            const bounds = L.latLngBounds(coordinates);
            map.fitBounds(bounds, { padding: [20, 20] });
            
        } catch (error) {
            console.error('Error displaying map:', error);
            mapContainer.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #ff0000;">
                    Errore nella visualizzazione della mappa: ${error.message}
                </div>
            `;
        }
    }, 100);
}