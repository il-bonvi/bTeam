# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QDialogButtonBox,
    QGroupBox,
    QListWidget,
    QPushButton,
    QMessageBox,
)
from intervals_sync import IntervalsSyncService


class SimpleAthleteDialog(QDialog):
    """Dialog per aggiungere un nuovo atleta"""
    
    def __init__(self, parent=None, teams=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo atleta")

        layout = QVBoxLayout(self)
        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.team_combo = QComboBox()
        teams = teams or []
        self.team_combo.addItem("Nessuna", None)
        for team in teams:
            self.team_combo.addItem(team["name"], team["id"])

        layout.addWidget(QLabel("Nome"))
        layout.addWidget(self.first_name_edit)
        layout.addWidget(QLabel("Cognome"))
        layout.addWidget(self.last_name_edit)
        layout.addWidget(QLabel("Squadra"))
        layout.addWidget(self.team_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return self.first_name_edit.text(), self.last_name_edit.text(), self.team_combo.currentData()


class AthleteDetailsDialog(QDialog):
    """Dialog per modificare i dettagli di un atleta"""
    
    def __init__(self, parent=None, athlete=None, storage=None):
        super().__init__(parent)
        self.setWindowTitle(f"Dettagli atleta: {athlete.get('last_name', '')} {athlete.get('first_name', '')}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        self.athlete_id = athlete.get("id")
        self.storage = storage
        athlete = athlete or {}

        layout = QVBoxLayout(self)

        # ===== API Key Section =====
        api_section = QGroupBox("Integrazione Intervals.icu")
        api_layout = QVBoxLayout(api_section)
        
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("API Key (visibile):"))
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(athlete.get("api_key", ""))
        self.api_key_edit.setEchoMode(QLineEdit.Normal)  # Visibile
        key_row.addWidget(self.api_key_edit, stretch=1)
        api_layout.addLayout(key_row)

        # Pulsante per visualizzare allenamenti disponibili
        btn_check = QPushButton("Visualizza allenamenti disponibili")
        btn_check.clicked.connect(self._check_available_workouts)
        api_layout.addWidget(btn_check)

        # Pulsante per sincronizzazione attività
        btn_sync = QPushButton("🔄 Sincronizza Intervals")
        btn_sync.setStyleSheet("background-color: #3b82f6; color: white; font-weight: bold; padding: 8px;")
        btn_sync.clicked.connect(self._sync_intervals)
        api_layout.addWidget(btn_sync)

        # Area dove mostrare gli allenamenti disponibili
        self.workouts_list = QListWidget()
        self.workouts_list.setMaximumHeight(200)
        api_layout.addWidget(QLabel("Allenamenti disponibili:"))
        api_layout.addWidget(self.workouts_list)

        # Pulsante per importare allenamenti selezionati
        btn_import = QPushButton("Importa allenamenti selezionati")
        btn_import.clicked.connect(self._import_selected_workouts)
        api_layout.addWidget(btn_import)

        layout.addWidget(api_section)

        # ===== Athlete Data Section =====
        data_section = QGroupBox("Dati atleta")
        data_layout = QVBoxLayout(data_section)

        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setCalendarPopup(True)
        if athlete.get("birth_date"):
            self.birth_date_edit.setDate(datetime.fromisoformat(athlete["birth_date"]).date())

        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 300)
        self.weight_spin.setDecimals(1)
        if athlete.get("weight_kg"):
            self.weight_spin.setValue(athlete["weight_kg"])

        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0, 250)
        self.height_spin.setDecimals(1)
        if athlete.get("height_cm"):
            self.height_spin.setValue(athlete["height_cm"])

        self.cp_spin = QDoubleSpinBox()
        self.cp_spin.setRange(0, 1000)
        self.cp_spin.setDecimals(1)
        if athlete.get("cp"):
            self.cp_spin.setValue(athlete["cp"])

        self.w_prime_spin = QDoubleSpinBox()
        self.w_prime_spin.setRange(0, 100000)
        self.w_prime_spin.setDecimals(1)
        if athlete.get("w_prime"):
            self.w_prime_spin.setValue(athlete["w_prime"])

        self.notes_edit = QLineEdit()
        self.notes_edit.setText(athlete.get("notes", ""))

        self.kj_per_hour_per_kg_spin = QDoubleSpinBox()
        self.kj_per_hour_per_kg_spin.setRange(0.5, 50.0)
        self.kj_per_hour_per_kg_spin.setDecimals(2)
        self.kj_per_hour_per_kg_spin.setSingleStep(0.1)
        if athlete.get("kj_per_hour_per_kg"):
            self.kj_per_hour_per_kg_spin.setValue(athlete["kj_per_hour_per_kg"])
        else:
            self.kj_per_hour_per_kg_spin.setValue(10.0)

        data_layout.addWidget(QLabel("Data di nascita (opzionale)"))
        data_layout.addWidget(self.birth_date_edit)
        data_layout.addWidget(QLabel("Peso (kg) - opzionale"))
        data_layout.addWidget(self.weight_spin)
        data_layout.addWidget(QLabel("Altezza (cm) - opzionale"))
        data_layout.addWidget(self.height_spin)
        data_layout.addWidget(QLabel("CP (W) - opzionale"))
        data_layout.addWidget(self.cp_spin)
        data_layout.addWidget(QLabel("W' (J) - opzionale"))
        data_layout.addWidget(self.w_prime_spin)
        data_layout.addWidget(QLabel("kJ/h/kg (default atleta) - opzionale"))
        data_layout.addWidget(self.kj_per_hour_per_kg_spin)
        data_layout.addWidget(QLabel("Note"))
        data_layout.addWidget(self.notes_edit)

        layout.addWidget(data_section)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _check_available_workouts(self):
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            info = QDialog(self)
            info.setWindowTitle("API Key richiesta")
            layout = QVBoxLayout(info)
            layout.addWidget(QLabel("Inserisci una API key per visualizzare gli allenamenti disponibili"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(info.accept)
            layout.addWidget(buttons)
            info.exec()
            return
        
        try:
            # Recupera allenamenti veri da Intervals.icu
            sync_service = IntervalsSyncService(api_key=api_key)
            if not sync_service.is_connected():
                QMessageBox.critical(
                    self,
                    "Errore connessione",
                    "Impossibile connettersi a Intervals.icu. Verifica la API key."
                )
                return
            
            # Mostra messaggio di caricamento
            self.workouts_list.clear()
            self.workouts_list.addItem("Caricamento allenamenti...")
            
            # Recupera attività ultimi 30 giorni
            activities, status_msg = sync_service.fetch_activities(days_back=30)
            
            self.workouts_list.clear()
            if activities:
                for activity in activities:
                    try:
                        formatted = IntervalsSyncService.format_activity_for_storage(activity)
                        date_str = formatted['start_date']
                        name = formatted.get('name', 'Allenamento')
                        duration = formatted['moving_time_minutes']
                        distance = formatted.get('distance_km', 0)
                        self.workouts_list.addItem(f"{name} - {date_str} ({int(duration)}min, {distance:.1f}km)")
                    except Exception as e:
                        print(f"[bTeam] Errore formattazione attività: {e}")
                        continue
            else:
                self.workouts_list.addItem(status_msg or "Nessun allenamento trovato negli ultimi 30 giorni")
        except Exception as e:
            print(f"[bTeam] Errore caricamento allenamenti: {e}")
            self.workouts_list.clear()
            self.workouts_list.addItem(f"Errore: {str(e)}")

    def _import_selected_workouts(self):
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            info = QDialog(self)
            info.setWindowTitle("API Key richiesta")
            layout = QVBoxLayout(info)
            layout.addWidget(QLabel("Inserisci una API key per importare gli allenamenti"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(info.accept)
            layout.addWidget(buttons)
            info.exec()
            return

        if not self.workouts_list.currentItem():
            info = QDialog(self)
            info.setWindowTitle("Seleziona allenamenti")
            layout = QVBoxLayout(info)
            layout.addWidget(QLabel("Seleziona almeno un allenamento da importare"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(info.accept)
            layout.addWidget(buttons)
            info.exec()
            return

        # Placeholder
        done = QDialog(self)
        done.setWindowTitle("Import")
        layout = QVBoxLayout(done)
        layout.addWidget(QLabel(f"Import degli allenamenti selezionati in corso...\n\nFunzionalità in sviluppo"))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(done.accept)
        layout.addWidget(buttons)
        done.exec()

    def _sync_intervals(self) -> None:
        """Sincronizza le attività di Intervals per questo atleta"""
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            QMessageBox.warning(
                self,
                "API Key richiesta",
                "Inserisci una API key valida per sincronizzare le attività"
            )
            return
        
        try:
            # Crea servizio sincronizzazione
            sync_service = IntervalsSyncService(api_key=api_key)
            
            # Verifica connessione
            if not sync_service.is_connected():
                QMessageBox.critical(
                    self,
                    "Errore connessione",
                    "Impossibile connettersi a Intervals.icu.\n\n"
                    "Verifica:\n"
                    "• Connessione internet\n"
                    "• API key corretta"
                )
                return
            
            # Mostra messaggio di inizio
            QMessageBox.information(
                self,
                "Sincronizzazione in corso",
                "Sincronizzazione in corso...\nAttendi il completamento."
            )
            
            # Recupera attività (restituisce tupla: (lista, messaggio))
            activities, status_msg = sync_service.fetch_activities(days_back=30)
            
            if not activities:
                QMessageBox.information(
                    self,
                    "Risultato sincronizzazione",
                    status_msg or "Non sono state trovate attività negli ultimi 30 giorni"
                )
                return
            
            # Salva nel database
            if self.storage:
                athlete_id = self.athlete_id
                new_count = 0
                duplicate_count = 0
                error_count = 0
                
                for activity in activities:
                    try:
                        formatted = IntervalsSyncService.format_activity_for_storage(activity)
                        activity_id, is_new = self.storage.add_activity(
                            athlete_id=athlete_id,
                            title=formatted['name'],
                            activity_date=formatted['start_date'],
                            duration_minutes=formatted['moving_time_minutes'],
                            distance_km=formatted['distance_km'],
                            tss=None,
                            source='intervals',
                            intervals_id=str(formatted['intervals_id']),
                            is_race=formatted.get('is_race'),
                            tags=formatted.get('tags', []),
                            avg_watts=formatted.get('avg_watts'),
                            normalized_watts=formatted.get('normalized_watts'),
                            avg_hr=formatted.get('avg_hr'),
                            max_hr=formatted.get('max_hr'),
                            avg_cadence=formatted.get('avg_cadence'),
                            training_load=formatted.get('training_load'),
                            intensity=formatted.get('intensity'),
                            feel=formatted.get('feel'),
                            calories=formatted.get('calories'),
                            activity_type=formatted.get('type'),
                        )
                        if is_new:
                            new_count += 1
                        else:
                            duplicate_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"[bTeam] Errore import attività: {e}")
                        continue
                
                # Costruisci messaggio dettagliato
                parts = []
                if new_count > 0:
                    parts.append(f"✅ {new_count} nuove attività")
                if duplicate_count > 0:
                    parts.append(f"⚠️  {duplicate_count} già presenti")
                if error_count > 0:
                    parts.append(f"❌ {error_count} errori")
                
                message = "Sincronizzazione completata:\n" + "\n".join(parts) if parts else "✅ Nessuna attività da sincronizzare"
                QMessageBox.information(
                    self,
                    "✓ Sincronizzazione completata",
                    message
                )
            else:
                QMessageBox.information(
                    self,
                    "✓ Attività recuperate",
                    f"Recuperate {len(activities)} attività (database non disponibile)"
                )
        
        except Exception as e:
            print(f"[bTeam] Errore sincronizzazione: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore durante la sincronizzazione:\n{str(e)}"
            )

    def values(self):
        return {
            "birth_date": self.birth_date_edit.date().toString("yyyy-MM-dd"),
            "weight_kg": self.weight_spin.value() or None,
            "height_cm": self.height_spin.value() or None,
            "cp": self.cp_spin.value() or None,
            "w_prime": self.w_prime_spin.value() or None,
            "api_key": self.api_key_edit.text(),
            "kj_per_hour_per_kg": self.kj_per_hour_per_kg_spin.value() or 10.0,
            "notes": self.notes_edit.text()
        }
