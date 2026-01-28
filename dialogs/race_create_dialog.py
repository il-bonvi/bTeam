# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from __future__ import annotations

from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit, QDoubleSpinBox,
    QSpinBox, QTextEdit, QComboBox, QPushButton, QMessageBox
)
from storage_bteam import BTeamStorage


class RaceCreateDialog(QDialog):
    """Dialog per creare una nuova gara"""
    
    def __init__(self, parent, storage: BTeamStorage):
        super().__init__(parent)
        self.setWindowTitle("✨ Crea Nuova Gara")
        self.setMinimumSize(600, 500)
        self.storage = storage
        self.selected_race_file = None
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Row 1: Nome, Data
        row1_layout = QHBoxLayout()
        row1_layout.addWidget(QLabel("Nome gara:"))
        self.name_edit = QLineEdit()
        row1_layout.addWidget(self.name_edit)
        
        row1_layout.addWidget(QLabel("Data:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(date.today())
        self.date_edit.setCalendarPopup(True)
        row1_layout.addWidget(self.date_edit)
        layout.addLayout(row1_layout)
        
        # Row 2: Genere, Categoria
        row2_layout = QHBoxLayout()
        row2_layout.addWidget(QLabel("Genere:"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Femminile", "Maschile"])
        self.gender_combo.currentIndexChanged.connect(self._update_categories)
        row2_layout.addWidget(self.gender_combo)
        
        row2_layout.addWidget(QLabel("Categoria:"))
        self.category_combo = QComboBox()
        self._update_categories()
        row2_layout.addWidget(self.category_combo)
        layout.addLayout(row2_layout)
        
        # Row 3: Distanza
        row3_layout = QHBoxLayout()
        row3_layout.addWidget(QLabel("Distanza (km):"))
        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setMinimum(0.1)
        self.distance_spin.setMaximum(500)
        self.distance_spin.setSingleStep(1)
        self.distance_spin.setDecimals(1)
        self.distance_spin.setValue(100)
        self.distance_spin.valueChanged.connect(self._update_predictions)
        row3_layout.addWidget(self.distance_spin)
        layout.addLayout(row3_layout)
        
        # Row 4: Media prevista, Dislivello
        row4_layout = QHBoxLayout()
        row4_layout.addWidget(QLabel("Media prevista (km/h):"))
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setMinimum(1)
        self.speed_spin.setMaximum(60)
        self.speed_spin.setSingleStep(1)
        self.speed_spin.setDecimals(1)
        self.speed_spin.setValue(25)
        self.speed_spin.valueChanged.connect(self._update_predictions)
        row4_layout.addWidget(self.speed_spin)
        
        row4_layout.addWidget(QLabel("Dislivello (m):"))
        self.elevation_spin = QSpinBox()
        self.elevation_spin.setMinimum(0)
        self.elevation_spin.setMaximum(10000)
        self.elevation_spin.setSingleStep(50)
        self.elevation_spin.setValue(500)
        row4_layout.addWidget(self.elevation_spin)
        layout.addLayout(row4_layout)
        
        # Row 5: Previsioni
        row5_layout = QHBoxLayout()
        self.duration_label = QLabel("Durata prevista: --")
        self.duration_label.setStyleSheet("font-weight: bold; color: #4ade80;")
        row5_layout.addWidget(self.duration_label)
        
        self.kj_label = QLabel("KJ previsti: --")
        self.kj_label.setStyleSheet("font-weight: bold; color: #60a5fa;")
        row5_layout.addWidget(self.kj_label)
        layout.addLayout(row5_layout)
        
        # Row 6: Note
        layout.addWidget(QLabel("Note:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        layout.addWidget(self.notes_edit)
        
        layout.addStretch()
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        create_btn = QPushButton("✓ Crea Gara")
        create_btn.setStyleSheet("background-color: #4ade80; color: black; font-weight: bold; padding: 8px;")
        create_btn.clicked.connect(self._create_race)
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Aggiorna le previsioni iniziali
        self._update_predictions()
    
    def _update_predictions(self) -> None:
        """Aggiorna le previsioni di durata e KJ"""
        distance_km = self.distance_spin.value()
        speed_kmh = self.speed_spin.value()
        
        if speed_kmh <= 0:
            self.duration_label.setText("Durata prevista: --")
            self.kj_label.setText("KJ previsti: --")
            return
        
        duration_minutes = (distance_km / speed_kmh) * 60
        hours = int(duration_minutes // 60)
        minutes = int(duration_minutes % 60)
        
        self.duration_label.setText(f"Durata prevista: {hours}h {minutes}m")
        
        duration_hours = duration_minutes / 60
        athletes = self.storage.list_athletes()
        
        if athletes:
            total_kj = 0
            for athlete in athletes:
                weight_kg = athlete.get("weight_kg", 70) or 70
                kj_per_hora_per_kg = athlete.get("kj_per_hour_per_kg", 1.0) or 1.0
                total_kj += kj_per_hora_per_kg * duration_hours * weight_kg
            
            avg_kj = total_kj / len(athletes)
            self.kj_label.setText(f"KJ previsti (media): {avg_kj:.0f}")
        else:
            self.kj_label.setText("KJ previsti: --")
    
    def _update_categories(self) -> None:
        """Aggiorna le categorie in base al genere"""
        gender = self.gender_combo.currentText()
        
        categories = {
            "Femminile": ["Allieve", "Junior", "Junior 1NC", "Junior 2NC", "Junior (OPEN)", "OPEN"],
            "Maschile": ["U23"]
        }
        
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItems(categories.get(gender, []))
        self.category_combo.blockSignals(False)
    
    def _create_race(self) -> None:
        """Crea una nuova gara"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Campo obbligatorio", "Inserisci il nome della gara")
            return
        
        race_date = self.date_edit.date().toString("yyyy-MM-dd")
        gender = self.gender_combo.currentText()
        category = self.category_combo.currentText()
        distance_km = self.distance_spin.value()
        elevation_m = self.elevation_spin.value()
        speed_kmh = self.speed_spin.value()
        notes = self.notes_edit.toPlainText().strip()
        
        duration_minutes = (distance_km / speed_kmh) * 60 if speed_kmh > 0 else 0
        duration_hours = duration_minutes / 60
        
        athletes = self.storage.list_athletes()
        if athletes:
            total_kj = 0
            for athlete in athletes:
                weight_kg = athlete.get("weight_kg", 70) or 70
                kj_per_hora_per_kg = athlete.get("kj_per_hour_per_kg", 1.0) or 1.0
                total_kj += kj_per_hora_per_kg * duration_hours * weight_kg
            predicted_kj = total_kj / len(athletes)
        else:
            predicted_kj = 0
        
        try:
            self.storage.add_race(
                name=name,
                race_date=race_date,
                gender=gender,
                category=category,
                distance_km=distance_km,
                elevation_m=elevation_m,
                avg_speed_kmh=speed_kmh,
                predicted_duration_minutes=duration_minutes,
                predicted_kj=predicted_kj,
                route_file=self.selected_race_file,
                notes=notes,
            )
            
            QMessageBox.information(self, "Gara creata", f"Gara '{name}' creata con successo!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore creazione gara: {str(e)}")
