# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from __future__ import annotations

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit, QDoubleSpinBox,
    QSpinBox, QTextEdit, QComboBox, QPushButton
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from storage_bteam import BTeamStorage


def build_details_tab(race_data: dict, storage: BTeamStorage) -> tuple[QWidget, dict]:
    """Costruisce il tab Dettagli della gara"""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(10)
    
    controls = {}
    
    # Nome
    layout.addWidget(QLabel("Nome gara:"))
    controls['name_edit'] = QLineEdit()
    controls['name_edit'].setText(race_data.get("name", ""))
    layout.addWidget(controls['name_edit'])
    
    # Data
    layout.addWidget(QLabel("Data:"))
    controls['date_edit'] = QDateEdit()
    race_date = race_data.get("race_date", "")
    if len(race_date) == 10:
        controls['date_edit'].setDate(datetime.strptime(race_date, "%Y-%m-%d").date())
    controls['date_edit'].setCalendarPopup(True)
    layout.addWidget(controls['date_edit'])
    
    # Genere e Categoria
    gender_layout = QHBoxLayout()
    gender_layout.addWidget(QLabel("Genere:"))
    controls['gender_combo'] = QComboBox()
    controls['gender_combo'].addItems(["Femminile", "Maschile"])
    controls['gender_combo'].setCurrentText(race_data.get("gender", "Femminile"))
    gender_layout.addWidget(controls['gender_combo'])
    
    gender_layout.addWidget(QLabel("Categoria:"))
    controls['category_combo'] = QComboBox()
    # Inizializza subito le categorie in base al genere corrente
    update_categories(controls['gender_combo'], controls['category_combo'])
    
    # Applica l'eventuale categoria salvata, altrimenti usa un default
    saved_category = race_data.get("category", "")
    if saved_category:
        idx = controls['category_combo'].findText(saved_category)
        if idx >= 0:
            controls['category_combo'].setCurrentIndex(idx)
        elif controls['category_combo'].count() > 0:
            controls['category_combo'].setCurrentIndex(0)
    else:
        if controls['category_combo'].count() > 0:
            controls['category_combo'].setCurrentIndex(0)
    
    controls['gender_combo'].currentIndexChanged.connect(
        lambda: update_categories(controls['gender_combo'], controls['category_combo'])
    )
    gender_layout.addStretch()
    gender_layout.addWidget(controls['category_combo'])
    layout.addLayout(gender_layout)
    
    # Distanza
    distance_layout = QHBoxLayout()
    distance_layout.addWidget(QLabel("Distanza (km):"))
    controls['distance_spin'] = QDoubleSpinBox()
    controls['distance_spin'].setMinimum(0.1)
    controls['distance_spin'].setMaximum(500)
    controls['distance_spin'].setSingleStep(1)
    controls['distance_spin'].setDecimals(1)
    controls['distance_spin'].setValue(race_data.get("distance_km", 100))
    distance_layout.addWidget(controls['distance_spin'])
    
    distance_layout.addWidget(QLabel("Dislivello (m):"))
    controls['elevation_spin'] = QSpinBox()
    controls['elevation_spin'].setMinimum(0)
    controls['elevation_spin'].setMaximum(10000)
    controls['elevation_spin'].setSingleStep(50)
    controls['elevation_spin'].setValue(int(race_data.get("elevation_m", 0) or 0))
    distance_layout.addWidget(controls['elevation_spin'])
    distance_layout.addStretch()
    layout.addLayout(distance_layout)
    
    # Media prevista e Durata
    media_layout = QHBoxLayout()
    media_layout.addWidget(QLabel("Media prevista (km/h):"))
    controls['speed_spin'] = QDoubleSpinBox()
    controls['speed_spin'].setMinimum(1)
    controls['speed_spin'].setMaximum(60)
    controls['speed_spin'].setSingleStep(0.5)
    controls['speed_spin'].setDecimals(1)
    controls['speed_spin'].setValue(race_data.get("avg_speed_kmh", 25))
    media_layout.addWidget(controls['speed_spin'])
    
    media_layout.addWidget(QLabel("Durata prevista (h:m):"))
    controls['duration_edit'] = QLineEdit()
    controls['duration_edit'].setReadOnly(True)
    controls['duration_edit'].setStyleSheet("background-color: #f0f0f0; color: #4ade80; font-weight: bold;")
    duration_minutes = race_data.get("predicted_duration_minutes", 0) or 0
    hours = int(duration_minutes // 60)
    minutes = int(duration_minutes % 60)
    controls['duration_edit'].setText(f"{hours}h {minutes}m" if duration_minutes > 0 else "--")
    media_layout.addWidget(controls['duration_edit'])
    media_layout.addStretch()
    layout.addLayout(media_layout)
    
    # Note
    layout.addWidget(QLabel("Note:"))
    controls['notes_edit'] = QTextEdit()
    controls['notes_edit'].setPlainText(race_data.get("notes", ""))
    controls['notes_edit'].setMaximumHeight(80)
    layout.addWidget(controls['notes_edit'])
    
    # ===== Sezione Traccia =====
    layout.addWidget(QLabel("📊 Traccia Gara"))
    
    trace_layout = QHBoxLayout()
    trace_layout.addWidget(QLabel("File:"))
    
    trace_file_label = QLineEdit()
    trace_file_label.setReadOnly(True)
    trace_file_label.setPlaceholderText("Nessun file importato")
    trace_file_label.setMaximumWidth(200)  # Limita larghezza del campo file
    trace_layout.addWidget(trace_file_label)
    controls['trace_file_label'] = trace_file_label
    
    import_trace_btn = QPushButton("Importa GPX/FIT/TCX")
    import_trace_btn.setMaximumWidth(120)  # Ridotto da 150 a 120
    import_trace_btn.clicked.connect(lambda: on_import_trace(trace_file_label, controls['distance_spin'], controls['elevation_spin'], controls.get('map_view')))
    trace_layout.addWidget(import_trace_btn)
    layout.addLayout(trace_layout)
    
    # Minimap
    map_label = QLabel("Mappa traccia:")
    map_label.setStyleSheet("font-weight: bold;")  # Più piccolo
    layout.addWidget(map_label)
    controls['map_view'] = QWebEngineView()
    controls['map_view'].setMaximumHeight(500)  # Aumentato da 300 a 500
    controls['map_view'].setHtml("<html><body><p>Importa un file traccia per visualizzare la mappa</p></body></html>")
    layout.addWidget(controls['map_view'])
    
    layout.addStretch()
    return widget, controls


def update_categories(gender_combo: QComboBox, category_combo: QComboBox) -> None:
    """Aggiorna le categorie in base al genere"""
    gender = gender_combo.currentText()
    categories = {
        "Femminile": ["Allieve", "Junior", "Junior 1NC", "Junior 2NC", "Junior (OPEN)", "OPEN"],
        "Maschile": ["U23"]
    }
    
    category_combo.blockSignals(True)
    category_combo.clear()
    category_combo.addItems(categories.get(gender, []))
    category_combo.blockSignals(False)


def update_predictions(distance_spin: QDoubleSpinBox, speed_spin: QDoubleSpinBox, 
                      duration_edit: QLineEdit, storage: BTeamStorage, on_duration_changed=None) -> None:
    """Aggiorna previsioni di durata"""
    distance_km = distance_spin.value()
    speed_kmh = speed_spin.value()
    
    if speed_kmh <= 0:
        duration_edit.setText("--")
        if on_duration_changed:
            on_duration_changed(0)
        return
    
    # Calcola durata
    duration_minutes = (distance_km / speed_kmh) * 60
    hours = int(duration_minutes // 60)
    minutes = int(duration_minutes % 60)
    duration_edit.setText(f"{hours}h {minutes}m")
    
    # Chiama callback con durata in ore
    if on_duration_changed:
        on_duration_changed(duration_minutes / 60)


def on_import_trace(trace_file_label, distance_spin, elevation_spin, map_view=None) -> Optional[str]:
    """Importa il file traccia GPX/FIT/TCX e aggiorna distanza/dislivello"""
    from pathlib import Path
    from typing import Optional
    from PySide6.QtWidgets import QFileDialog
    
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Seleziona file traccia",
        "",
        "GPX Files (*.gpx);;FIT Files (*.fit);;TCX Files (*.tcx);;All Files (*)"
    )
    if file_path:
        filename = Path(file_path).name
        trace_file_label.setText(filename)
        
        # Leggi il file e aggiorna i campi
        try:
            ext = Path(file_path).suffix.lower()
            total_distance = 0.0
            elevation_gain = 0.0
            
            if ext == '.gpx':
                import gpxpy
                with open(file_path, 'r', encoding='utf-8') as gpx_file:
                    gpx = gpxpy.parse(gpx_file)
                    
                    prev_elevation = None
                    for track in gpx.tracks:
                        for segment in track.segments:
                            total_distance += segment.length_2d() / 1000  # Convert to km
                            for point in segment.points:
                                if point.elevation is not None:
                                    if prev_elevation is not None:
                                        diff = point.elevation - prev_elevation
                                        if diff > 0:
                                            elevation_gain += diff
                                    prev_elevation = point.elevation
                    
            elif ext == '.fit':
                from fitparse import FitFile
                fitfile = FitFile(file_path)
                records = list(fitfile.get_messages('record'))
                prev_elevation = None
                for record in records:
                    if record.get_value('distance') is not None:
                        total_distance = max(total_distance, record.get_value('distance') / 1000)  # Convert to km
                    if record.get_value('altitude') is not None:
                        elevation = record.get_value('altitude')
                        if prev_elevation is not None:
                            diff = elevation - prev_elevation
                            if diff > 0:
                                elevation_gain += diff
                        prev_elevation = elevation
                    
            elif ext == '.tcx':
                import tcxparser
                tcx = tcxparser.TCXParser(file_path)
                total_distance = tcx.distance / 1000  # Convert to km
                # Calculate elevation gain from trackpoints
                prev_elevation = None
                for activity in tcx.activity_list:
                    for lap in activity.laps:
                        for trackpoint in lap.trackpoints:
                            if trackpoint.elevation is not None:
                                elevation = trackpoint.elevation
                                if prev_elevation is not None:
                                    diff = elevation - prev_elevation
                                    if diff > 0:
                                        elevation_gain += diff
                                prev_elevation = elevation
            
            # Generate map if map_view is provided
            if map_view and ext == '.gpx':
                try:
                    import folium
                    
                    # Extract coordinates from GPX
                    coordinates = []
                    for track in gpx.tracks:
                        for segment in track.segments:
                            for point in segment.points:
                                coordinates.append([point.latitude, point.longitude])
                    
                    if coordinates:
                        # Calculate bounds for auto-zoom
                        lats = [coord[0] for coord in coordinates]
                        lons = [coord[1] for coord in coordinates]
                        lat_min, lat_max = min(lats), max(lats)
                        lon_min, lon_max = min(lons), max(lons)
                        
                        # Create map with auto-fit bounds
                        m = folium.Map()
                        
                        # Add track
                        folium.PolyLine(coordinates, color='red', weight=3, opacity=0.7).add_to(m)
                        
                        # Add start marker
                        folium.Marker(coordinates[0], popup='Start', icon=folium.Icon(color='green')).add_to(m)
                        
                        # Add end marker
                        folium.Marker(coordinates[-1], popup='Finish', icon=folium.Icon(color='red')).add_to(m)
                        
                        # Fit bounds to show entire track
                        m.fit_bounds([[lat_min, lon_min], [lat_max, lon_max]])
                        
                        # Get HTML directly
                        html_string = m.get_root().render()
                        
                        # Load in QWebEngineView
                        map_view.setHtml(html_string)
                        
                except ImportError:
                    print("[bTeam] folium non installato. Installa con: pip install folium")
                    map_view.setHtml("<html><body><p>Installa folium per visualizzare la mappa: pip install folium</p></body></html>")
                except Exception as e:
                    print(f"[bTeam] Errore generazione mappa: {e}")
                    map_view.setHtml(f"<html><body><p>Errore caricamento mappa: {e}</p></body></html>")
            
            # Aggiorna i campi
            if total_distance > 0:
                distance_spin.setValue(total_distance)
            if elevation_gain > 0:
                elevation_spin.setValue(int(elevation_gain))
                
            print(f"[bTeam] Traccia importata: {filename}, Distanza: {total_distance:.1f}km, Dislivello: {elevation_gain:.0f}m")
                
        except ImportError as e:
            print(f"[bTeam] Libreria mancante: {e}. Installa con pip install gpxpy fitparse tcxparser")
        except Exception as e:
            print(f"[bTeam] Errore lettura traccia: {e}")
        
        return file_path
    return None
