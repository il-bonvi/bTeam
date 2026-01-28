# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from __future__ import annotations

from datetime import datetime, date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit, QDoubleSpinBox,
    QSpinBox, QTextEdit, QComboBox, QPushButton, QMessageBox, QTabWidget
)
from storage_bteam import BTeamStorage


class RaceDetailsDialog(QDialog):
    """Dialog per modificare i dettagli di una gara"""
    
    def __init__(self, parent, storage: BTeamStorage, race_id: int):
        super().__init__(parent)
        self.setWindowTitle("Modifica Gara")
        self.setMinimumSize(1000, 700)
        self.storage = storage
        self.race_id = race_id
        self.race_data = None
        self.trace_file_path = None
        
        self._load_race_data()
        self._build_ui()
    
    def _load_race_data(self) -> None:
        """Carica i dati della gara dal database"""
        self.race_data = self.storage.get_race(self.race_id)
    
    def _build_ui(self) -> None:
        """Costruisce l'interfaccia del dialog con tab"""
        if not self.race_data:
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Gara non trovata"))
            return
        
        layout = QVBoxLayout(self)
        
        # Import dai moduli sections
        from dialogs.races_sections.details_tab import build_details_tab, update_predictions, update_categories
        from dialogs.races_sections.riders_tab import build_riders_tab
        from dialogs.races_sections.metrics_tab import build_metrics_tab
        
        # Tab widget
        tabs = QTabWidget()
        
        # Tab 1: Dettagli
        details_widget, self.details_controls = build_details_tab(self.race_data, self.storage)
        tabs.addTab(details_widget, "📋 Dettagli")
        
        # Connetti gli update alle modifiche
        self.details_controls['distance_spin'].valueChanged.connect(
            lambda: update_predictions(
                self.details_controls['distance_spin'],
                self.details_controls['speed_spin'],
                self.details_controls['duration_edit'],
                self.details_controls['kj_edit'],
                self.storage
            )
        )
        self.details_controls['speed_spin'].valueChanged.connect(
            lambda: update_predictions(
                self.details_controls['distance_spin'],
                self.details_controls['speed_spin'],
                self.details_controls['duration_edit'],
                self.details_controls['kj_edit'],
                self.storage
            )
        )
        
        # Tab 2: Riders
        riders_widget, self.riders_controls = build_riders_tab(self.storage, self.race_id, None)
        tabs.addTab(riders_widget, "🚴 Riders")
        
        # Tab 3: Metrics
        metrics_widget, self.metrics_controls = build_metrics_tab()
        tabs.addTab(metrics_widget, "📊 Metrics")
        
        layout.addWidget(tabs)
        
        # Bottoni
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("✓ Salva")
        save_btn.setStyleSheet("background-color: #4ade80; color: black; font-weight: bold; padding: 8px;")
        save_btn.clicked.connect(self._save_changes)
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def _save_changes(self) -> None:
        """Salva le modifiche nel database"""
        try:
            name = self.details_controls['name_edit'].text().strip()
            if not name:
                QMessageBox.warning(self, "Campo obbligatorio", "Inserisci il nome della gara")
                return
            
            race_date = self.details_controls['date_edit'].date().toString("yyyy-MM-dd")
            distance_km = self.details_controls['distance_spin'].value()
            elevation_m = self.details_controls['elevation_spin'].value()
            speed_kmh = self.details_controls['speed_spin'].value()
            gender = self.details_controls['gender_combo'].currentText()
            category = self.details_controls['category_combo'].currentText()
            notes = self.details_controls['notes_edit'].toPlainText().strip()
            
            # Calcola durata e KJ
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
            
            # Aggiorna database
            if self.storage.update_race(
                race_id=self.race_id,
                name=name,
                race_date=race_date,
                distance_km=distance_km,
                elevation_m=elevation_m,
                avg_speed_kmh=speed_kmh,
                predicted_duration_minutes=duration_minutes,
                predicted_kj=predicted_kj,
                gender=gender,
                category=category,
                notes=notes
            ):
                QMessageBox.information(self, "Salvato", "Gara modificata con successo!")
                self.accept()
            else:
                QMessageBox.critical(self, "Errore", "Errore nel salvataggio della gara")
        except Exception as e:
            print(f"[bTeam] Errore salvataggio gara: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Errore", f"Errore nel salvataggio: {str(e)}")
