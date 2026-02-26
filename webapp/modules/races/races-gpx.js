/**
 * Races GPX Module - GPX/FIT/TCX import and map display
 * Handles file import, parsing, distance calculation, and Leaflet map visualization
 *
 * FILE: webapp/modules/races/races-gpx.js
 */

window.gpxTraceData = window.gpxTraceData || null;

window.handleGpxImport = function(event) {
    const file = event?.target?.files[0];
    if (!file) {
        const createFileInput = document.getElementById('gpx-file');
        if (createFileInput?.files?.length > 0) processGpxFile(createFileInput.files[0]);
        return;
    }
    processGpxFile(file);
};

function processGpxFile(file) {
    const filenameDisplay = document.getElementById('gpx-filename');
    if (filenameDisplay) filenameDisplay.textContent = file.name;
    const reader = new FileReader();
    reader.onload = function(e) { parseGpxFile(e.target.result, file.name); };
    reader.readAsText(file);
}

function parseGpxFile(content, filename) {
    try {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(content, 'text/xml');
        if (xmlDoc.querySelector('parsererror')) { showToast('Errore nel parsing del file GPX', 'error'); return; }

        const trackpoints = xmlDoc.querySelectorAll('trkpt');
        if (trackpoints.length === 0) { showToast('Nessun trackpoint trovato nel file', 'warning'); return; }

        const coordinates = [];  // [lat, lon] for Leaflet map
        const points = [];       // [lat, lon, ele] for Route visualizer
        let totalDistance = 0, elevationGain = 0;
        let prevElevation = null, prevLat = null, prevLon = null;

        trackpoints.forEach(point => {
            const lat = parseFloat(point.getAttribute('lat'));
            const lon = parseFloat(point.getAttribute('lon'));
            const elevation = parseFloat(point.querySelector('ele')?.textContent || 0);

            coordinates.push([lat, lon]);
            points.push([lat, lon, elevation]);

            if (prevLat !== null) totalDistance += calculateDistance(prevLat, prevLon, lat, lon);
            if (prevElevation !== null && elevation - prevElevation > 0) elevationGain += elevation - prevElevation;

            prevElevation = elevation; prevLat = lat; prevLon = lon;
        });

        // points includes elevation [lat, lon, ele] — compact JSON for Route visualizer
        window.gpxTraceData = { coordinates, points, totalDistance, elevationGain };

        updateCreateFormFromGpx(totalDistance, elevationGain);
        updateDetailFormFromGpx(totalDistance, elevationGain);
        displayGpxMap(coordinates);

        if (typeof updateCreateRacePredictions === 'function') updateCreateRacePredictions();
        if (typeof updateDetailPredictions === 'function') updateDetailPredictions();

        // If Route tab already open, reload with new data
        const iframe = document.getElementById('route-visualizer-iframe');
        if (iframe && iframe.dataset.loaded === 'true') {
            iframe.dataset.loaded = 'false';
            window.initRouteTab();
        }

        showToast(`✅ Traccia importata: ${totalDistance.toFixed(1)}km, ${Math.round(elevationGain)}m D+`, 'success');

    } catch (error) {
        console.error('Error parsing GPX:', error);
        showToast('Errore nell\'elaborazione del file: ' + error.message, 'error');
    }
}

function updateCreateFormFromGpx(totalDistance, elevationGain) {
    const distanceEl = document.getElementById('race-distance');
    const elevationEl = document.getElementById('race-elevation');
    if (totalDistance > 0 && distanceEl) distanceEl.value = totalDistance.toFixed(1);
    if (elevationGain > 0 && elevationEl) elevationEl.value = Math.round(elevationGain);
    const gpxDistanceEl = document.getElementById('gpx-distance');
    const gpxElevationEl = document.getElementById('gpx-elevation');
    const gpxPreviewEl = document.getElementById('gpx-preview');
    if (gpxDistanceEl) gpxDistanceEl.textContent = totalDistance.toFixed(1) + ' km';
    if (gpxElevationEl) gpxElevationEl.textContent = Math.round(elevationGain) + ' m';
    if (gpxPreviewEl) gpxPreviewEl.style.display = 'block';
}

function updateDetailFormFromGpx(totalDistance, elevationGain) {
    const detailDistanceEl = document.getElementById('detail-distance');
    const detailElevationEl = document.getElementById('detail-elevation');
    if (totalDistance > 0 && detailDistanceEl) detailDistanceEl.value = totalDistance.toFixed(1);
    if (elevationGain > 0 && detailElevationEl) detailElevationEl.value = Math.round(elevationGain);
    const deleteBtn = document.getElementById('gpx-delete-btn');
    if (deleteBtn) deleteBtn.style.display = 'inline-block';
    const filenameDisplay = document.getElementById('gpx-filename');
    if (filenameDisplay && filenameDisplay.textContent === 'Nessun file importato') {
        filenameDisplay.textContent = '✅ Traccia caricata';
        filenameDisplay.style.color = '#22C55E';
    }

    const exportBtn = document.getElementById('export-route-btn');
    if (exportBtn) {
        exportBtn.disabled = false;
        exportBtn.style.opacity = '1';
        exportBtn.style.cursor = 'pointer';
    }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}

function displayGpxMap(coordinates) {
    if (coordinates.length === 0) return;
    let mapContainer = document.getElementById('map-container') || document.getElementById('gpx-map');
    if (!mapContainer) return;
    mapContainer.innerHTML = '<div id="leaflet-map" style="width: 100%; height: 100%;"></div>';
    setTimeout(() => {
        try {
            const map = L.map('leaflet-map').setView(coordinates[0], 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors', maxZoom: 19
            }).addTo(map);
            L.polyline(coordinates, { color: '#ff6b35', weight: 4, opacity: 0.8 }).addTo(map);
            L.marker(coordinates[0]).addTo(map).bindPopup('🟢 Partenza');
            L.marker(coordinates[coordinates.length - 1]).addTo(map).bindPopup('🔴 Arrivo');
            map.fitBounds(L.latLngBounds(coordinates), { padding: [20, 20] });
        } catch (error) {
            console.error('Error creating map:', error);
            mapContainer.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#999;">Errore mappa</div>';
        }
    }, 100);
}