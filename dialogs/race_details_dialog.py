# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from __future__ import annotations

from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QTabWidget
)
from storage_bteam import BTeamStorage
from config_bteam import get_intervals_api_key, set_intervals_api_key
from intervals_client_v2 import IntervalsAPIClient


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
        
        sync_btn = QPushButton("🔄 Sync Race")
        sync_btn.setStyleSheet("background-color: #3b82f6; color: white; font-weight: bold; padding: 8px;")
        sync_btn.clicked.connect(self._sync_race_to_intervals)
        
        save_btn = QPushButton("✓ Salva")
        save_btn.setStyleSheet("background-color: #4ade80; color: black; font-weight: bold; padding: 8px;")
        save_btn.clicked.connect(self._save_changes)
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(sync_btn)
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
    
    def _sync_race_to_intervals(self) -> None:
        """Fa il push della gara su Intervals.icu"""
        try:
            # Prova a recuperare API key da un atleta
            api_key = None
            athlete_id_for_intervals = None
            athletes = self.storage.list_athletes()
            
            for athlete in athletes:
                if athlete.get("api_key"):
                    api_key = athlete["api_key"]
                    athlete_id_for_intervals = athlete.get("intervals_id") or "0"
                    break
            
            # Se non c'è API key negli atleti, offri di configurarla
            if not api_key:
                reply = QMessageBox.question(
                    self,
                    "API Key non trovata",
                    "Nessun atleta ha una API key configurata.\n\n"
                    "Vuoi configurarla ora?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Apri dialog per inserire API key
                    self._configure_api_key()
                    # Riprova dopo configurazione
                    athletes = self.storage.list_athletes()
                    for athlete in athletes:
                        if athlete.get("api_key"):
                            api_key = athlete["api_key"]
                            break
                
                if not api_key:
                    QMessageBox.warning(
                        self,
                        "API Key mancante",
                        "Configurazione annullata o non salvata.\n"
                        "Vai ai Dettagli di un atleta e aggiungi l'API key per Intervals.icu."
                    )
                    return
            
            # Recupera dati dalla UI
            name = self.details_controls['name_edit'].text().strip()
            race_date_str = self.details_controls['date_edit'].date().toString("yyyy-MM-dd")
            distance_km = self.details_controls['distance_spin'].value()
            speed_kmh = self.details_controls['speed_spin'].value()
            
            duration_minutes = (distance_km / speed_kmh) * 60 if speed_kmh > 0 else 0
            
            # La classe viene dall'obiettivo di ogni atleta nei riders
            # Leggi i riders della gara per trovare l'obiettivo
            riders = self.storage.get_race_athletes(self.race_id) or []
            
            # Per adesso, usa la classe del primo rider trovato (può essere esteso per sincronizzare tutti)
            athlete_classe = "C"  # Default
            if riders:
                # Prendi l'obiettivo dal primo rider
                athlete_classe = riders[0].get("objective", "C") or "C"
            
            # Crea il client Intervals
            client = IntervalsAPIClient(api_key=api_key)
            
            # Prepara il timestamp in formato ISO (solo data, no ora)
            start_date_local = f"{race_date_str}T00:00:00"
            duration_seconds = int(duration_minutes * 60)
            from datetime import datetime, timedelta
            start_dt = datetime.fromisoformat(start_date_local)
            end_dt = start_dt + timedelta(seconds=duration_seconds)
            end_date_local = end_dt.isoformat()
            
            # Push su Intervals
            print(f"[bTeam] Push race: {name} il {race_date_str}")
            print(f"[bTeam] Distanza: {distance_km}km, Durata: {duration_minutes:.0f}m")
            
            # Map classe atleta a categoria Intervals
            classe_map = {
                "A": "RACE_A",
                "B": "RACE_B",
                "C": "RACE_C",
            }
            
            intervals_category = classe_map.get(athlete_classe, "RACE_C")
            
            result = client.create_event(
                athlete_id=athlete_id_for_intervals,
                category=intervals_category,
                start_date_local=start_date_local,
                end_date_local=end_date_local,
                name=name,
                activity_type='Ride',
                distance=distance_km * 1000,  # Converti km → metri
                moving_time=int(duration_seconds),
                notes=f"{intervals_category.replace('RACE_', '')} Race"
            )
            
            print(f"[bTeam] Push completato: {result}")
            QMessageBox.information(
                self, 
                "✓ Sync completato", 
                f"Gara '{name}' pushata su Intervals.icu il {race_date_str}"
            )
            
        except Exception as e:
            print(f"[bTeam] Errore sync race: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Errore", f"Errore nel sync: {str(e)}")
    
    def _configure_api_key(self) -> None:
        """Dialog per configurare la API key di Intervals"""
        from dialogs import IntervalsDialog
        
        dialog = IntervalsDialog(self, athletes=[])
        if dialog.exec():
            api_key, _ = dialog.values()
            if api_key:
                from config_bteam import set_intervals_api_key
                set_intervals_api_key(api_key)
                QMessageBox.information(self, "✓ Configurato", "API key salvata!")
                print(f"[bTeam] API key configurata")


