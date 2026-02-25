/**
 * Races Export Module - Export route as standalone HTML report
 * Mirrors the logic of genera_report.py but runs entirely in the browser.
 *
 * FILE: webapp/modules/races/races-export.js
 * Include in templates/index.html after races-route.js:
 *   <script src="/modules/races/races-route.js"></script>
 *   <script src="/modules/races/races-export.js"></script>
 */

/**
 * Export the current race route as a standalone HTML file.
 * Uses ROUTE_VISUALIZER_HTML (from races-route.js) as template,
 * injects the GPX data as base64 and adds a title bar — identical
 * to what genera_report.py produces on the desktop.
 *
 * @param {string} raceName  - Used as page title and filename
 * @param {object} gpxData   - window.gpxTraceData  { points: [[lat,lon,ele], ...] }
 */
window.exportRouteHTML = function(raceName, gpxData) {
    if (!gpxData || !gpxData.points || gpxData.points.length === 0) {
        showToast('Nessuna traccia GPX disponibile da esportare', 'warning');
        return;
    }

    if (typeof ROUTE_VISUALIZER_HTML === 'undefined') {
        showToast('Modulo Route non caricato — impossibile esportare', 'error');
        return;
    }

    // ── 1. Ricostruisci il GPX text dai punti salvati ──────────────────────
    let gpxText = '<?xml version="1.0" encoding="UTF-8"?>\n';
    gpxText += '<gpx version="1.1" creator="bTeam"><trk><trkseg>\n';
    for (const p of gpxData.points) {
        gpxText += `<trkpt lat="${p[0]}" lon="${p[1]}"><ele>${p[2]}</ele></trkpt>\n`;
    }
    gpxText += '</trkseg></trk></gpx>';

    // ── 2. Codifica in base64 ──────────────────────────────────────────────
    const gpxB64 = btoa(unescape(encodeURIComponent(gpxText)));
    const gpxName = (raceName.replace(/[^a-zA-Z0-9_\-]/g, '_') || 'route') + '.gpx';

    // ── 3. Parti dall'HTML del visualizzatore embedded ────────────────────
    let html = ROUTE_VISUALIZER_HTML;

    // ── 4. <title> ─────────────────────────────────────────────────────────
    html = html.replace(/<title>[^<]*<\/title>/, `<title>${raceName}</title>`);

    // ── 5. #data-content: forza display:block (era none) ──────────────────
    html = html.replace(
        /(#data-content\s*\{[^}]*)display\s*:\s*none/,
        '$1display: block'
    );
    // Rimuovi anche eventuale style inline display:none
    html = html.replace(
        /(<div id="data-content")[^>]*style="[^"]*display\s*:\s*none[^"]*"/,
        '$1'
    );

    // ── 6. Barra titolo sopra il container ────────────────────────────────
    const titleBar = `<div id="report-title-bar" style="
        text-align:center;
        padding: 18px 24px 10px;
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.02em;
        border-bottom: 2px solid #fc5200;
        margin-bottom: 0;
    ">${raceName}</div>`;

    html = html.replace(
        '<div class="container">',
        '<div class="container">\n' + titleBar,
    );

    // ── 7. Script di autoload GPX iniettato prima di </body> ──────────────
    const autoload = `<!--GPXREPORT_START-->
<script>
(function(){
    var GPX_B64 = "${gpxB64}";
    var GPX_NAME = "${gpxName.replace(/"/g, '\\"')}";
    var gpxText = decodeURIComponent(escape(atob(GPX_B64)));
    window._gpxRawText = gpxText;
    window._gpxFileName = GPX_NAME;
    // Attende che parseGPX sia disponibile (caricamento asincrono delle lib)
    function tryLoad() {
        if (typeof parseGPX === 'function') {
            parseGPX(gpxText);
        } else {
            setTimeout(tryLoad, 100);
        }
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', tryLoad);
    } else {
        tryLoad();
    }
})();
<\/script>
<!--GPXREPORT_END-->`;

    html = html.replace('</body>', autoload + '\n</body>');

    // ── 8. Download ────────────────────────────────────────────────────────
    const safeName = raceName.replace(/[^a-zA-Z0-9_\-]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '');
    const filename = (safeName || 'route_report') + '.html';

    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast(`✅ Report esportato: ${filename}`, 'success');
};