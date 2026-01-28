# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QMessageBox,
)

from shared.styles import get_style
from .config_bteam import ensure_storage_dir, set_storage_dir, get_intervals_api_key, set_intervals_api_key
from .intervals_client import IntervalsClient
from .intervals_sync import IntervalsSyncService
from .storage_bteam import BTeamStorage


class BTeamApp(QMainWindow):
    def __init__(self, theme: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("bTeam - Team Dashboard")
        self.setMinimumSize(1100, 800)
        self.current_theme = theme or "Forest Green"
        self.setStyleSheet(get_style(self.current_theme))

        self.storage_dir = ensure_storage_dir()
        self.storage = BTeamStorage(self.storage_dir)
        self.intervals_client = IntervalsClient()
        
        # Inizializza il servizio di sync Intervals.icu
        api_key = get_intervals_api_key()
        self.sync_service = IntervalsSyncService(api_key=api_key)
        
        print(f"[bTeam] Cartella dati: {self.storage_dir}")
        print(f"[bTeam] Database: {self.storage_dir / 'bteam.db'}")
        print(f"[bTeam] Intervals.icu: {'✓ Connesso' if self.sync_service.is_connected() else '✗ Non connesso'}")

        self._build_ui()
        self._refresh_tables()
        self._refresh_stats()

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("bTeam | Dashboard Squadra")
        header.setAlignment(Qt.AlignLeft)
        header.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(header)

        path_layout = QHBoxLayout()
        self.path_label = QLabel(str(self.storage_dir))
        self.path_label.setStyleSheet("color: #e2e8f0; font-size: 12px;")
        btn_change_path = QPushButton("Imposta cartella dati")
        btn_change_path.clicked.connect(self._choose_storage_dir)
        path_layout.addWidget(QLabel("Cartella dati:"))
        path_layout.addWidget(self.path_label, stretch=1)
        path_layout.addWidget(btn_change_path)
        layout.addLayout(path_layout)

        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # FILTRI E GESTIONE
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtra per squadra:"))
        self.filter_team_combo = QComboBox()
        self.filter_team_combo.addItem("Tutte", None)
        self.filter_team_combo.currentIndexChanged.connect(self._refresh_tables)
        filter_layout.addWidget(self.filter_team_combo)
        
        btn_manage_teams = QPushButton("Gestisci squadre")
        btn_manage_teams.clicked.connect(self._manage_teams_dialog)
        filter_layout.addWidget(btn_manage_teams)
        
        # Pulsante sincronizzazione Intervals.icu
        btn_sync_intervals = QPushButton("🔄 Sincronizza Intervals")
        btn_sync_intervals.clicked.connect(self._sync_intervals_dialog)
        filter_layout.addWidget(btn_sync_intervals)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        action_layout = QHBoxLayout()
        btn_add_team = QPushButton("Aggiungi squadra")
        btn_add_team.clicked.connect(self._add_team_dialog)
        btn_add_athlete = QPushButton("Aggiungi atleta")
        btn_add_athlete.clicked.connect(self._add_athlete_dialog)
        btn_add_activity = QPushButton("Aggiungi attività")
        btn_add_activity.clicked.connect(self._add_activity_dialog)
        action_layout.addWidget(btn_add_team)
        action_layout.addWidget(btn_add_athlete)
        action_layout.addWidget(btn_add_activity)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        grid = QGridLayout()
        grid.setSpacing(12)

        self.athletes_table = QTableWidget(0, 5)
        self.athletes_table.setHorizontalHeaderLabels(["ID", "Nome", "Cognome", "Squadra", "Note"])
        self.athletes_table.horizontalHeader().setStretchLastSection(True)
        self.athletes_table.itemDoubleClicked.connect(self._edit_athlete)
        grid.addWidget(QLabel("Atleti"), 0, 0)
        grid.addWidget(self.athletes_table, 1, 0)

        self.activities_table = QTableWidget(0, 7)
        self.activities_table.setHorizontalHeaderLabels(
            ["ID", "Atleta", "Data", "Titolo", "Durata (min)", "TSS", "Distanza km"]
        )
        self.activities_table.horizontalHeader().setStretchLastSection(True)
        grid.addWidget(QLabel("Attività"), 0, 1)
        grid.addWidget(self.activities_table, 1, 1)

        layout.addLayout(grid)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _refresh_stats(self) -> None:
        stats = self.storage.stats()
        self.stats_label.setText(f"Atleti: {stats['athletes']} | Attività: {stats['activities']}")
        
        # Aggiorna filtro squadre
        current_team = self.filter_team_combo.currentData()
        self.filter_team_combo.blockSignals(True)
        self.filter_team_combo.clear()
        self.filter_team_combo.addItem("Tutte", None)
        for team in self.storage.list_teams():
            self.filter_team_combo.addItem(team["name"], team["id"])
        
        # Ripristina selezione se possibile
        if current_team:
            idx = self.filter_team_combo.findData(current_team)
            if idx >= 0:
                self.filter_team_combo.setCurrentIndex(idx)
        self.filter_team_combo.blockSignals(False)

    def _refresh_tables(self) -> None:
        selected_team = self.filter_team_combo.currentData()
        all_athletes = self.storage.list_athletes()
        
        # Filtra per squadra se selezionato
        if selected_team:
            athletes = [a for a in all_athletes if a.get("team_id") == selected_team]
        else:
            athletes = all_athletes
        
        print(f"[bTeam] Atleti caricati: {len(athletes)}")
        self.athletes_table.setRowCount(len(athletes))
        for row_idx, athlete in enumerate(athletes):
            self.athletes_table.setItem(row_idx, 0, QTableWidgetItem(str(athlete["id"])))
            self.athletes_table.setItem(row_idx, 1, QTableWidgetItem(athlete.get("first_name", "")))
            self.athletes_table.setItem(row_idx, 2, QTableWidgetItem(athlete.get("last_name", "")))
            self.athletes_table.setItem(row_idx, 3, QTableWidgetItem(athlete.get("team_name", "")))
            self.athletes_table.setItem(row_idx, 4, QTableWidgetItem(athlete.get("notes", "")))

        activities = self.storage.list_activities()
        self.activities_table.setRowCount(len(activities))
        for row_idx, activity in enumerate(activities):
            self.activities_table.setItem(row_idx, 0, QTableWidgetItem(str(activity["id"])))
            self.activities_table.setItem(row_idx, 1, QTableWidgetItem(activity.get("athlete_name", "")))
            self.activities_table.setItem(row_idx, 2, QTableWidgetItem(activity.get("activity_date", "")))
            self.activities_table.setItem(row_idx, 3, QTableWidgetItem(activity.get("title", "")))
            self.activities_table.setItem(row_idx, 4, QTableWidgetItem(self._fmt_num(activity.get("duration_minutes"))))
            self.activities_table.setItem(row_idx, 5, QTableWidgetItem(self._fmt_num(activity.get("tss"))))
            self.activities_table.setItem(row_idx, 6, QTableWidgetItem(self._fmt_num(activity.get("distance_km"))))

    @staticmethod
    def _fmt_num(value: Optional[float]) -> str:
        return "" if value is None else f"{value:.1f}"

    def _add_team_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuova squadra")
        layout = QVBoxLayout(dialog)
        team_edit = QLineEdit()
        layout.addWidget(QLabel("Nome squadra"))
        layout.addWidget(team_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            team_name = team_edit.text().strip()
            if team_name:
                self.storage.add_team(team_name)
                self._refresh_tables()

    def _add_athlete_dialog(self) -> None:
        dialog = SimpleAthleteDialog(self, self.storage.list_teams())
        if dialog.exec():
            first_name, last_name, team_id = dialog.values()
            if not first_name.strip() or not last_name.strip():
                warning = QDialog(self)
                warning.setWindowTitle("Campo obbligatorio")
                layout = QVBoxLayout(warning)
                layout.addWidget(QLabel("Inserisci nome e cognome atleta"))
                buttons = QDialogButtonBox(QDialogButtonBox.Ok)
                buttons.accepted.connect(warning.accept)
                layout.addWidget(buttons)
                warning.exec()
                return
            print(f"[bTeam] Inserimento atleta: {first_name} {last_name}, squadra: {team_id}")
            athlete_id = self.storage.add_athlete(first_name=first_name, last_name=last_name, team_id=team_id)
            print(f"[bTeam] Atleta creato con ID: {athlete_id}")
            self._refresh_tables()
            self._refresh_stats()

    def _manage_teams_dialog(self) -> None:
        dialog = ManageTeamsDialog(self, self.storage)
        dialog.exec()
        self._refresh_tables()
        self._refresh_stats()

    def _edit_athlete(self, item) -> None:
        row = item.row()
        athlete_id_item = self.athletes_table.item(row, 0)
        if athlete_id_item:
            athlete_id = int(athlete_id_item.text())
            self._edit_athlete_details(athlete_id)

    def _edit_athlete_details(self, athlete_id: int) -> None:
        athletes = self.storage.list_athletes()
        athlete = next((a for a in athletes if a["id"] == athlete_id), None)
        if not athlete:
            return
        
        dialog = AthleteDetailsDialog(self, athlete, self.storage)
        if dialog.exec():
            values = dialog.values()
            self.storage.update_athlete(
                athlete_id=athlete_id,
                birth_date=values["birth_date"],
                weight_kg=values["weight_kg"],
                height_cm=values["height_cm"],
                cp=values["cp"],
                w_prime=values["w_prime"],
                api_key=values["api_key"],
                notes=values["notes"]
            )
            self._refresh_tables()
            self._refresh_stats()

    def _add_activity_dialog(self) -> None:
        athletes = self.storage.list_athletes()
        if not athletes:
            info = QDialog(self)
            info.setWindowTitle("Nessun atleta")
            layout = QVBoxLayout(info)
            layout.addWidget(QLabel("Aggiungi un atleta prima di inserire attività"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(info.accept)
            layout.addWidget(buttons)
            info.exec()
            return
        dialog = SimpleActivityDialog(self, athletes)
        if dialog.exec():
            payload = dialog.values()
            self.storage.add_activity(
                athlete_id=payload["athlete_id"],
                title=payload["title"],
                activity_date=payload["activity_date"],
                duration_minutes=payload["duration_minutes"],
                distance_km=payload["distance_km"],
                tss=payload["tss"],
            )
            self._refresh_tables()
            self._refresh_stats()

    def _sync_intervals_dialog(self) -> None:
        """Dialog per configurare e sincronizzare attività da Intervals.icu"""
        dialog = SyncIntervalsDialog(self, self.sync_service, self.storage)
        if dialog.exec():
            # Aggiorna la API key se modificata
            new_api_key = dialog.get_api_key()
            if new_api_key and new_api_key != self.sync_service.api_key:
                set_intervals_api_key(new_api_key)
                if self.sync_service.set_api_key(new_api_key):
                    print(f"[bTeam] API key Intervals.icu aggiornata")
            
            # Avvia la sincronizzazione
            selected_athlete_id = dialog.get_selected_athlete()
            days_back = dialog.get_days_back()
            
            if self.sync_service.is_connected() and selected_athlete_id:
                self._perform_sync(selected_athlete_id, days_back)

    def _perform_sync(self, athlete_id: int, days_back: int = 30) -> None:
        """Esegue la sincronizzazione delle attività"""
        activities, message = self.sync_service.fetch_activities(days_back=days_back)
        
        if activities:
            # Salva le attività nell'app
            count = 0
            for activity in activities:
                try:
                    formatted = IntervalsSyncService.format_activity_for_storage(activity)
                    self.storage.add_activity(
                        athlete_id=athlete_id,
                        title=formatted['name'],
                        activity_date=formatted['start_date'],
                        duration_minutes=formatted['moving_time_minutes'],
                        distance_km=formatted['distance_km'],
                        tss=None,  # Non disponibile da Intervals
                        source='intervals'
                    )
                    count += 1
                except Exception as e:
                    print(f"[bTeam] Errore inserimento attività: {e}")
            
            message = f"✅ Sincronizzate {count} attività da Intervals.icu"
            print(f"[bTeam] {message}")
        
        # Mostra risultato
        result_dialog = QDialog(self)
        result_dialog.setWindowTitle("Risultato sincronizzazione")
        layout = QVBoxLayout(result_dialog)
        layout.addWidget(QLabel(message))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(result_dialog.accept)
        layout.addWidget(buttons)
        result_dialog.exec()
        
        # Aggiorna tabelle
        self._refresh_tables()
        self._refresh_stats()

    def _choose_storage_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Seleziona cartella dati", str(self.storage_dir))
        if path:
            new_dir = Path(path)
            set_storage_dir(new_dir)
            self.storage_dir = new_dir
            self.storage.close()
            self.storage = BTeamStorage(self.storage_dir)
            self.path_label.setText(str(self.storage_dir))
            self._refresh_tables()
            self._refresh_stats()


class SimpleAthleteDialog(QDialog):
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


class SimpleActivityDialog(QDialog):
    def __init__(self, parent=None, athletes=None):
        super().__init__(parent)
        self.setWindowTitle("Nuova attività")
        athletes = athletes or []

        layout = QVBoxLayout(self)

        self.athlete_combo = QComboBox()
        for ath in athletes:
            self.athlete_combo.addItem(ath["name"], ath["id"])

        self.title_edit = QLineEdit()
        self.title_edit.setText("Allenamento")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(datetime.utcnow().date())

        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0, 2000)
        self.duration_spin.setDecimals(1)

        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(0, 1000)
        self.distance_spin.setDecimals(1)

        self.tss_spin = QDoubleSpinBox()
        self.tss_spin.setRange(0, 1000)
        self.tss_spin.setDecimals(1)

        layout.addWidget(QLabel("Atleta"))
        layout.addWidget(self.athlete_combo)
        layout.addWidget(QLabel("Titolo"))
        layout.addWidget(self.title_edit)
        layout.addWidget(QLabel("Data"))
        layout.addWidget(self.date_edit)
        layout.addWidget(QLabel("Durata (min)"))
        layout.addWidget(self.duration_spin)
        layout.addWidget(QLabel("Distanza (km)"))
        layout.addWidget(self.distance_spin)
        layout.addWidget(QLabel("TSS"))
        layout.addWidget(self.tss_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return {
            "athlete_id": self.athlete_combo.currentData(),
            "title": self.title_edit.text(),
            "activity_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "duration_minutes": self.duration_spin.value() or None,
            "distance_km": self.distance_spin.value() or None,
            "tss": self.tss_spin.value() or None,
        }


class IntervalsDialog(QDialog):
    def __init__(self, parent=None, athletes=None):
        super().__init__(parent)
        self.setWindowTitle("Importa Intervals.icu")
        athletes = athletes or []

        layout = QVBoxLayout(self)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)

        self.athlete_combo = QComboBox()
        for ath in athletes:
            full_name = f"{ath.get('first_name', '')} {ath.get('last_name', '')}".strip()
            self.athlete_combo.addItem(full_name, ath["id"])

        layout.addWidget(QLabel("API Key"))
        layout.addWidget(self.api_key_edit)
        layout.addWidget(QLabel("Atleta"))
        layout.addWidget(self.athlete_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return self.api_key_edit.text(), self.athlete_combo.currentData()


class AthleteDetailsDialog(QDialog):
    def __init__(self, parent=None, athlete=None, storage=None):
        super().__init__(parent)
        self.setWindowTitle(f"Dettagli atleta: {athlete.get('first_name', '')} {athlete.get('last_name', '')}")
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
            self.birth_date_edit.setDate(__import__('datetime').datetime.fromisoformat(athlete["birth_date"]).date())

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
        
        # Placeholder: implementare vera integrazione Intervals.icu
        self.workouts_list.clear()
        self.workouts_list.addItem("Loading... (Funzionalità in sviluppo)")
        self.workouts_list.addItem("Esempio: Allenamento 1 - 15/01/2026")
        self.workouts_list.addItem("Esempio: Allenamento 2 - 16/01/2026")
        self.workouts_list.addItem("Esempio: Allenamento 3 - 17/01/2026")

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

    def values(self):
        return {
            "birth_date": self.birth_date_edit.date().toString("yyyy-MM-dd"),
            "weight_kg": self.weight_spin.value() or None,
            "height_cm": self.height_spin.value() or None,
            "cp": self.cp_spin.value() or None,
            "w_prime": self.w_prime_spin.value() or None,
            "api_key": self.api_key_edit.text(),
            "notes": self.notes_edit.text()
        }


class ManageTeamsDialog(QDialog):
    def __init__(self, parent=None, storage=None):
        super().__init__(parent)
        self.setWindowTitle("Gestisci squadre")
        self.setMinimumSize(500, 400)
        self.storage = storage

        layout = QVBoxLayout(self)

        self.teams_list = QTableWidget(0, 2)
        self.teams_list.setHorizontalHeaderLabels(["ID", "Nome squadra"])
        self.teams_list.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.teams_list)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Aggiungi squadra")
        btn_add.clicked.connect(self._add_team)
        btn_edit = QPushButton("Modifica squadra")
        btn_edit.clicked.connect(self._edit_team)
        btn_delete = QPushButton("Elimina squadra")
        btn_delete.clicked.connect(self._delete_team)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        layout.addLayout(btn_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)

        self._refresh()

    def _refresh(self):
        teams = self.storage.list_teams()
        self.teams_list.setRowCount(len(teams))
        for row_idx, team in enumerate(teams):
            self.teams_list.setItem(row_idx, 0, QTableWidgetItem(str(team["id"])))
            self.teams_list.setItem(row_idx, 1, QTableWidgetItem(team["name"]))

    def _add_team(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Aggiungi squadra")
        layout = QVBoxLayout(dialog)
        name_edit = QLineEdit()
        layout.addWidget(QLabel("Nome squadra"))
        layout.addWidget(name_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip():
                self.storage.add_team(name_edit.text())
                self._refresh()

    def _edit_team(self):
        row = self.teams_list.currentRow()
        if row < 0:
            return
        team_id = int(self.teams_list.item(row, 0).text())
        old_name = self.teams_list.item(row, 1).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Modifica squadra")
        layout = QVBoxLayout(dialog)
        name_edit = QLineEdit()
        name_edit.setText(old_name)
        layout.addWidget(QLabel("Nome squadra"))
        layout.addWidget(name_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip():
                self.storage.update_team(team_id, name_edit.text())
                self._refresh()

    def _delete_team(self):
        row = self.teams_list.currentRow()
        if row < 0:
            return
        team_id = int(self.teams_list.item(row, 0).text())
        team_name = self.teams_list.item(row, 1).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Conferma eliminazione")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Eliminare la squadra '{team_name}'?\nGli atleti verranno mantenuti senza squadra."))
        buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            self.storage.delete_team(team_id)
            self._refresh()


class SyncIntervalsDialog(QDialog):
    """Dialog per sincronizzare attività da Intervals.icu"""
    
    def __init__(self, parent=None, sync_service=None, storage=None):
        super().__init__(parent)
        self.setWindowTitle("Sincronizza Intervals.icu")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.sync_service = sync_service
        self.storage = storage

        layout = QVBoxLayout(self)

        # ===== API Key Section =====
        api_section = QGroupBox("Configurazione Intervals.icu")
        api_layout = QVBoxLayout(api_section)
        
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("API Key:"))
        self.api_key_edit = QLineEdit()
        if sync_service and sync_service.api_key:
            self.api_key_edit.setText(sync_service.api_key)
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        key_row.addWidget(self.api_key_edit, stretch=1)
        api_layout.addLayout(key_row)

        # Test connessione
        btn_test = QPushButton("Test connessione")
        btn_test.clicked.connect(self._test_connection)
        api_layout.addWidget(btn_test)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        api_layout.addWidget(self.status_label)
        
        if sync_service and sync_service.is_connected():
            self.status_label.setText("✅ Connesso a Intervals.icu")
            self.status_label.setStyleSheet("color: #22c55e; font-size: 11px;")

        layout.addWidget(api_section)

        # ===== Settings Section =====
        settings_section = QGroupBox("Impostazioni sincronizzazione")
        settings_layout = QVBoxLayout(settings_section)

        # Atleta
        settings_layout.addWidget(QLabel("Atleta di destinazione:"))
        self.athlete_combo = QComboBox()
        if storage:
            athletes = storage.list_athletes()
            for ath in athletes:
                full_name = f"{ath.get('first_name', '')} {ath.get('last_name', '')}".strip()
                self.athlete_combo.addItem(full_name, ath["id"])
        
        if self.athlete_combo.count() == 0:
            self.athlete_combo.addItem("-- Aggiungi un atleta prima --", None)
        settings_layout.addWidget(self.athlete_combo)

        # Giorni indietro
        settings_layout.addWidget(QLabel("Scarica attività degli ultimi X giorni:"))
        self.days_spin = QDoubleSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        self.days_spin.setDecimals(0)
        settings_layout.addWidget(self.days_spin)

        layout.addWidget(settings_section)

        # ===== Preview Section =====
        preview_section = QGroupBox("Anteprima attività da importare")
        preview_layout = QVBoxLayout(preview_section)
        
        btn_preview = QPushButton("Visualizza attività disponibili")
        btn_preview.clicked.connect(self._preview_activities)
        preview_layout.addWidget(btn_preview)

        self.activities_list = QTableWidget(0, 4)
        self.activities_list.setHorizontalHeaderLabels(["Data", "Nome", "Tipo", "Distanza (km)"])
        self.activities_list.setMaximumHeight(200)
        self.activities_list.horizontalHeader().setStretchLastSection(True)
        preview_layout.addWidget(self.activities_list)

        layout.addWidget(preview_section)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _test_connection(self):
        """Testa la connessione con Intervals.icu"""
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            self.status_label.setText("❌ Inserisci una API key")
            self.status_label.setStyleSheet("color: #ef4444; font-size: 11px;")
            return
        
        self.status_label.setText("🔄 Test in corso...")
        self.status_label.setStyleSheet("color: #f59e0b; font-size: 11px;")

        # Test della connessione
        test_service = IntervalsSyncService(api_key=api_key)
        if test_service.is_connected():
            self.status_label.setText("✅ Connesso a Intervals.icu")
            self.status_label.setStyleSheet("color: #22c55e; font-size: 11px;")
            # Aggiorna il servizio principale
            self.sync_service.set_api_key(api_key)
        else:
            self.status_label.setText("❌ Connessione fallita. Verifica la API key")
            self.status_label.setStyleSheet("color: #ef4444; font-size: 11px;")

    def _preview_activities(self):
        """Visualizza le attività disponibili"""
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            info = QDialog(self)
            info.setWindowTitle("API Key richiesta")
            layout = QVBoxLayout(info)
            layout.addWidget(QLabel("Inserisci una API key per visualizzare le attività"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(info.accept)
            layout.addWidget(buttons)
            info.exec()
            return

        # Aggiorna il servizio con la nuova key se cambiata
        if api_key != self.sync_service.api_key:
            self.sync_service.set_api_key(api_key)

        if not self.sync_service.is_connected():
            info = QDialog(self)
            info.setWindowTitle("Connessione fallita")
            layout = QVBoxLayout(info)
            layout.addWidget(QLabel("Impossibile connettersi a Intervals.icu. Verifica la API key"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(info.accept)
            layout.addWidget(buttons)
            info.exec()
            return

        # Scarica le attività
        days_back = int(self.days_spin.value())
        activities, message = self.sync_service.fetch_activities(days_back=days_back, include_intervals=False)

        # Popola la tabella
        self.activities_list.setRowCount(len(activities))
        for row_idx, activity in enumerate(activities):
            date_str = activity.get('start_date_local', '')[:10]
            name = activity.get('name', '')
            type_ = activity.get('type', '')
            distance_km = (activity.get('distance', 0) or 0) / 1000

            self.activities_list.setItem(row_idx, 0, QTableWidgetItem(date_str))
            self.activities_list.setItem(row_idx, 1, QTableWidgetItem(name))
            self.activities_list.setItem(row_idx, 2, QTableWidgetItem(type_))
            self.activities_list.setItem(row_idx, 3, QTableWidgetItem(f"{distance_km:.1f}"))

        info = QDialog(self)
        info.setWindowTitle("Risultato")
        layout = QVBoxLayout(info)
        layout.addWidget(QLabel(f"{message}\n\nSeleziona 'OK' per importare tutte queste attività"))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(info.accept)
        layout.addWidget(buttons)
        info.exec()

    def get_api_key(self) -> str:
        return self.api_key_edit.text().strip()

    def get_selected_athlete(self) -> Optional[int]:
        return self.athlete_combo.currentData()

    def get_days_back(self) -> int:
        return int(self.days_spin.value())


if __name__ == "__main__":
    app = QApplication([])
    win = BTeamApp()
    win.show()
    app.exec()
