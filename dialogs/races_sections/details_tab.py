# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from __future__ import annotations

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit, QDoubleSpinBox,
    QSpinBox, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox
)
from PySide6.QtCore import Qt
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
    saved_category = race_data.get("category", "")
    if saved_category:
        idx = controls['category_combo'].findText(saved_category)
        if idx >= 0:
            controls['category_combo'].setCurrentIndex(idx)
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
    
    # KJ previsti (read-only)
    kj_layout = QHBoxLayout()
    kj_layout.addWidget(QLabel("KJ previsti (media):"))
    controls['kj_edit'] = QLineEdit()
    controls['kj_edit'].setReadOnly(True)
    controls['kj_edit'].setStyleSheet("background-color: #f0f0f0; color: #60a5fa; font-weight: bold;")
    kj = race_data.get("predicted_kj", 0)
    controls['kj_edit'].setText(f"{kj:.0f}" if kj else "--")
    kj_layout.addWidget(controls['kj_edit'])
    kj_layout.addStretch()
    layout.addLayout(kj_layout)
    
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
                      duration_edit: QLineEdit, kj_edit: QLineEdit, storage: BTeamStorage) -> None:
    """Aggiorna previsioni di durata e KJ"""
    distance_km = distance_spin.value()
    speed_kmh = speed_spin.value()
    
    if speed_kmh <= 0:
        duration_edit.setText("--")
        kj_edit.setText("--")
        return
    
    # Calcola durata
    duration_minutes = (distance_km / speed_kmh) * 60
    hours = int(duration_minutes // 60)
    minutes = int(duration_minutes % 60)
    duration_edit.setText(f"{hours}h {minutes}m")
    
    # Calcola KJ
    duration_hours = duration_minutes / 60
    athletes = storage.list_athletes()
    
    if athletes:
        total_kj = 0
        for athlete in athletes:
            weight_kg = athlete.get("weight_kg", 70) or 70
            kj_per_hora_per_kg = athlete.get("kj_per_hour_per_kg", 1.0) or 1.0
            total_kj += kj_per_hora_per_kg * duration_hours * weight_kg
        avg_kj = total_kj / len(athletes)
        kj_edit.setText(f"{avg_kj:.0f}")
    else:
        kj_edit.setText("--")
