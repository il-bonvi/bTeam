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
    QTabWidget,
    QSpinBox,
    QCheckBox,
)

from shared.styles import get_style
from config_bteam import ensure_storage_dir, set_storage_dir, get_intervals_api_key, set_intervals_api_key
from intervals_client import IntervalsClient
from intervals_sync import IntervalsSyncService
from storage_bteam import BTeamStorage


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
        btn_delete_athlete = QPushButton("🗑️ Elimina atleta")
        btn_delete_athlete.clicked.connect(self._delete_athlete)
        btn_add_activity = QPushButton("Aggiungi attività")
        btn_add_activity.clicked.connect(self._add_activity_dialog)
        action_layout.addWidget(btn_add_team)
        action_layout.addWidget(btn_add_athlete)
        action_layout.addWidget(btn_delete_athlete)
        action_layout.addWidget(btn_add_activity)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        # ===== Tools Toolbar =====
        tools_layout = QHBoxLayout()
        btn_wellness = QPushButton("❤️ Tracking Benessere")
        btn_wellness.clicked.connect(self._wellness_dialog)
        btn_plan_week = QPushButton("📅 Pianifica Settimana")
        btn_plan_week.clicked.connect(self._plan_week_dialog)
        btn_export = QPushButton("💾 Export/Import")
        btn_export.clicked.connect(self._export_import_dialog)
        tools_layout.addWidget(btn_wellness)
        tools_layout.addWidget(btn_plan_week)
        tools_layout.addWidget(btn_export)
        tools_layout.addStretch()
        layout.addLayout(tools_layout)

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

    def _delete_athlete(self) -> None:
        """Delete selected athlete after confirmation."""
        current_row = self.athletes_table.currentRow()
        if current_row < 0:
            warning = QDialog(self)
            warning.setWindowTitle("Seleziona un atleta")
            layout = QVBoxLayout(warning)
            layout.addWidget(QLabel("Seleziona un atleta da eliminare"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(warning.accept)
            layout.addWidget(buttons)
            warning.exec()
            return
        
        athlete_id_item = self.athletes_table.item(current_row, 0)
        first_name_item = self.athletes_table.item(current_row, 1)
        last_name_item = self.athletes_table.item(current_row, 2)
        
        if not athlete_id_item:
            return
        
        athlete_id = int(athlete_id_item.text())
        first_name = first_name_item.text() if first_name_item else ""
        last_name = last_name_item.text() if last_name_item else ""
        
        # Conferma eliminazione
        confirm = QDialog(self)
        confirm.setWindowTitle("Conferma eliminazione")
        layout = QVBoxLayout(confirm)
        layout.addWidget(QLabel(f"Eliminare l'atleta {first_name} {last_name}?\nQuesta azione non può essere annullata."))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(confirm.accept)
        buttons.rejected.connect(confirm.reject)
        layout.addWidget(buttons)
        
        if confirm.exec():
            self.storage.delete_athlete(athlete_id)
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

    def _wellness_dialog(self) -> None:
        """Apre il dialog per tracciare dati wellness"""
        dialog = WellnessDialog(self, self.sync_service)
        if dialog.exec():
            values = dialog.values()
            print(f"[bTeam] Wellness logging: {values}")

    def _plan_week_dialog(self) -> None:
        """Apre il dialog per pianificare una settimana di allenamenti"""
        dialog = PlanWeekDialog(self, self.sync_service)
        if dialog.exec():
            plan = dialog.get_plan()
            
            if not self.sync_service.is_connected():
                error = QDialog(self)
                error.setWindowTitle("Errore")
                layout = QVBoxLayout(error)
                layout.addWidget(QLabel("Intervals.icu non è connesso. Configura l'API key prima."))
                buttons = QDialogButtonBox(QDialogButtonBox.Ok)
                buttons.accepted.connect(error.accept)
                layout.addWidget(buttons)
                error.exec()
                return
            
            # Crea i workout
            created = 0
            for workout in plan:
                success, msg = self.sync_service.create_workout(
                    date=workout['date'],
                    name=workout['name'],
                    description=workout['description'],
                    activity_type=workout['type']
                )
                if success:
                    created += 1
            
            result = QDialog(self)
            result.setWindowTitle("Pianificazione completata")
            layout = QVBoxLayout(result)
            layout.addWidget(QLabel(f"✅ {created} allenamenti creati su Intervals.icu"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(result.accept)
            layout.addWidget(buttons)
            result.exec()

    def _export_import_dialog(self) -> None:
        """Apre il dialog per esportare/importare dati"""
        dialog = ExportImportDialog(self, self.storage)
        dialog.exec()

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
            full_name = f"{ath.get('first_name', '')} {ath.get('last_name', '')}".strip()
            # Fallback to other identifiers if name is empty
            display_name = full_name or ath.get("name") or f"ID {ath.get('id')}" or "Unknown"
            self.athlete_combo.addItem(display_name, ath["id"])

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


class WellnessDialog(QDialog):
    """Dialog per loggare dati wellness (peso, FC riposo, HRV)"""
    
    def __init__(self, parent=None, sync_service=None):
        super().__init__(parent)
        self.setWindowTitle("Tracking Benessere")
        self.setMinimumWidth(500)
        self.sync_service = sync_service
        
        from datetime import date
        
        layout = QVBoxLayout(self)
        
        # Seleziona data
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Data:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(date.today())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Peso
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel("Peso (kg):"))
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(30, 200)
        self.weight_spin.setDecimals(1)
        weight_layout.addWidget(self.weight_spin)
        weight_layout.addStretch()
        layout.addLayout(weight_layout)
        
        # FC Riposo
        hr_layout = QHBoxLayout()
        hr_layout.addWidget(QLabel("FC Riposo (bpm):"))
        self.hr_spin = QSpinBox()
        self.hr_spin.setRange(30, 120)
        hr_layout.addWidget(self.hr_spin)
        hr_layout.addStretch()
        layout.addLayout(hr_layout)
        
        # HRV
        hrv_layout = QHBoxLayout()
        hrv_layout.addWidget(QLabel("HRV (ms):"))
        self.hrv_spin = QDoubleSpinBox()
        self.hrv_spin.setRange(0, 200)
        self.hrv_spin.setDecimals(1)
        hrv_layout.addWidget(self.hrv_spin)
        hrv_layout.addStretch()
        layout.addLayout(hrv_layout)
        
        # Note
        layout.addWidget(QLabel("Note (opzionali):"))
        self.notes_edit = QLineEdit()
        layout.addWidget(self.notes_edit)
        
        # Pulsante sincronizza con Intervals
        btn_sync = QPushButton("📤 Sincronizza con Intervals.icu")
        btn_sync.clicked.connect(self._sync_to_intervals)
        layout.addWidget(btn_sync)
        
        layout.addStretch()
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _sync_to_intervals(self):
        """Sincronizza i dati con Intervals.icu"""
        if not self.sync_service or not self.sync_service.is_connected():
            msg = QDialog(self)
            msg.setWindowTitle("Errore")
            layout = QVBoxLayout(msg)
            layout.addWidget(QLabel("Intervals.icu non è connesso. Configura l'API key prima."))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(msg.accept)
            layout.addWidget(buttons)
            msg.exec()
            return
        
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        success, result_msg = self.sync_service.update_wellness(
            date=date_str,
            weight=self.weight_spin.value() if self.weight_spin.value() > 0 else None,
            resting_hr=self.hr_spin.value() if self.hr_spin.value() > 0 else None,
            hrv=self.hrv_spin.value() if self.hrv_spin.value() > 0 else None,
            notes=self.notes_edit.text() if self.notes_edit.text() else None
        )
        
        result = QDialog(self)
        result.setWindowTitle("Risultato")
        layout = QVBoxLayout(result)
        layout.addWidget(QLabel(result_msg))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(result.accept)
        layout.addWidget(buttons)
        result.exec()
    
    def values(self):
        return {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'weight': self.weight_spin.value() if self.weight_spin.value() > 0 else None,
            'resting_hr': self.hr_spin.value() if self.hr_spin.value() > 0 else None,
            'hrv': self.hrv_spin.value() if self.hrv_spin.value() > 0 else None,
            'notes': self.notes_edit.text()
        }


class PlanWeekDialog(QDialog):
    """Dialog per pianificare una settimana di allenamenti"""
    
    def __init__(self, parent=None, sync_service=None):
        super().__init__(parent)
        self.setWindowTitle("Pianifica Settimana di Allenamenti")
        self.setMinimumWidth(600)
        self.sync_service = sync_service
        
        from datetime import date, timedelta
        
        layout = QVBoxLayout(self)
        
        # Data inizio (lunedì)
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Lunedì della settimana:"))
        self.start_date = QDateEdit()
        today = date.today()
        days_ahead = 0 - today.weekday()  # Lunedì scorso
        if days_ahead <= 0:
            days_ahead += 7  # Lunedì prossimo
        next_monday = today + timedelta(days=days_ahead)
        self.start_date.setDate(next_monday)
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Preset workouts
        layout.addWidget(QLabel("Allenamenti settimanali:"))
        
        self.workouts = []
        
        presets = [
            {'day': 'Lunedì', 'type': 'Endurance', 'desc': '60m @ 65%'},
            {'day': 'Mercoledì', 'type': 'VO2 Max', 'desc': '4x5min @ 120%'},
            {'day': 'Venerdì', 'type': 'Soglia', 'desc': '3x10min @ 95%'},
            {'day': 'Sabato', 'type': 'Lungo', 'desc': '120m @ 60%'}
        ]
        
        for preset in presets:
            row_layout = QHBoxLayout()
            row_layout.addWidget(QLabel(f"{preset['day']}:"))
            
            type_combo = QComboBox()
            type_combo.addItem("Riposo")
            type_combo.addItem(preset['type'])
            type_combo.setCurrentIndex(1)
            row_layout.addWidget(type_combo)
            
            desc_edit = QLineEdit()
            desc_edit.setText(preset['desc'])
            row_layout.addWidget(desc_edit)
            
            checkbox = QCheckBox("Abilitato")
            checkbox.setChecked(True)
            row_layout.addWidget(checkbox)
            
            self.workouts.append({
                'day': preset['day'],
                'combo': type_combo,
                'desc': desc_edit,
                'enabled': checkbox
            })
            
            layout.addLayout(row_layout)
        
        layout.addStretch()
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_plan(self):
        start_date = self.start_date.date()
        plan = []
        
        for i, workout in enumerate(self.workouts):
            if not workout['enabled'].isChecked():
                continue
            
            from datetime import timedelta
            workout_date = start_date.addDays(i * 2)  # Lunedì, Mercoledì, Venerdì, Sabato
            
            plan.append({
                'date': workout_date.toString("yyyy-MM-dd"),
                'name': workout['combo'].currentText(),
                'description': workout['desc'].text(),
                'type': 'Ride'
            })
        
        return plan


class ExportImportDialog(QDialog):
    """Dialog per esportare/importare dati"""
    
    def __init__(self, parent=None, storage=None):
        super().__init__(parent)
        self.setWindowTitle("Export / Import Dati")
        self.setMinimumWidth(500)
        self.storage = storage
        
        layout = QVBoxLayout(self)
        
        # Tabs
        tabs = QTabWidget()
        
        # ===== EXPORT TAB =====
        export_layout = QVBoxLayout()
        
        export_layout.addWidget(QLabel("Seleziona cosa esportare:"))
        
        self.export_athletes = QCheckBox("Atleti")
        self.export_athletes.setChecked(True)
        export_layout.addWidget(self.export_athletes)
        
        self.export_activities = QCheckBox("Attività")
        self.export_activities.setChecked(True)
        export_layout.addWidget(self.export_activities)
        
        self.export_wellness = QCheckBox("Dati Wellness")
        export_layout.addWidget(self.export_wellness)
        
        export_format_layout = QHBoxLayout()
        export_format_layout.addWidget(QLabel("Formato:"))
        self.export_format = QComboBox()
        self.export_format.addItem("CSV")
        self.export_format.addItem("JSON")
        export_format_layout.addWidget(self.export_format)
        export_format_layout.addStretch()
        export_layout.addLayout(export_format_layout)
        
        btn_export = QPushButton("💾 Esporta Dati")
        btn_export.clicked.connect(self._do_export)
        export_layout.addWidget(btn_export)
        
        export_layout.addStretch()
        
        export_widget = QWidget()
        export_widget.setLayout(export_layout)
        tabs.addTab(export_widget, "Export")
        
        # ===== IMPORT TAB =====
        import_layout = QVBoxLayout()
        
        import_layout.addWidget(QLabel("Importa dati da file:"))
        
        file_layout = QHBoxLayout()
        self.import_file_label = QLineEdit()
        self.import_file_label.setReadOnly(True)
        file_layout.addWidget(self.import_file_label)
        btn_browse = QPushButton("Sfoglia...")
        btn_browse.clicked.connect(self._browse_import_file)
        file_layout.addWidget(btn_browse)
        import_layout.addLayout(file_layout)
        
        import_layout.addWidget(QLabel("Merge mode (mantieni dati esistenti):"))
        self.import_merge = QCheckBox("Sì, unisci con i dati esistenti")
        self.import_merge.setChecked(True)
        import_layout.addWidget(self.import_merge)
        
        btn_import = QPushButton("📂 Importa Dati")
        btn_import.clicked.connect(self._do_import)
        import_layout.addWidget(btn_import)
        
        import_layout.addStretch()
        
        import_widget = QWidget()
        import_widget.setLayout(import_layout)
        tabs.addTab(import_widget, "Import")
        
        layout.addWidget(tabs)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _browse_import_file(self):
        from pathlib import Path
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona file da importare",
            str(Path.home()),
            "CSV (*.csv);;JSON (*.json);;Tutti (*.*)"
        )
        if file_path:
            self.import_file_label.setText(file_path)
    
    def _do_export(self):
        from pathlib import Path
        from datetime import datetime
        import csv
        import json
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        format_ext = "csv" if self.export_format.currentText() == "CSV" else "json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva esportazione",
            str(Path.home() / f"bteam_export_{timestamp}.{format_ext}"),
            f"{format_ext.upper()} (*.{format_ext})"
        )
        
        if not file_path:
            return
        
        try:
            data = {}
            
            if self.export_athletes.isChecked():
                data['athletes'] = self.storage.list_athletes()
            
            if self.export_activities.isChecked():
                data['activities'] = self.storage.list_activities()
            
            if self.export_format.currentText() == "JSON":
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            else:  # CSV
                # Semplice export CSV degli atleti
                if 'athletes' in data:
                    with open(file_path, 'w', newline='') as f:
                        if data['athletes']:
                            writer = csv.DictWriter(f, fieldnames=data['athletes'][0].keys())
                            writer.writeheader()
                            writer.writerows(data['athletes'])
            
            msg = QDialog(self)
            msg.setWindowTitle("Successo")
            layout = QVBoxLayout(msg)
            layout.addWidget(QLabel(f"✅ Dati esportati in:\n{file_path}"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(msg.accept)
            layout.addWidget(buttons)
            msg.exec()
        except Exception as e:
            msg = QDialog(self)
            msg.setWindowTitle("Errore")
            layout = QVBoxLayout(msg)
            layout.addWidget(QLabel(f"❌ Errore export: {str(e)}"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(msg.accept)
            layout.addWidget(buttons)
            msg.exec()
    
    def _do_import(self):
        msg = QDialog(self)
        msg.setWindowTitle("Info")
        layout = QVBoxLayout(msg)
        layout.addWidget(QLabel("Funzionalità import in sviluppo"))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(msg.accept)
        layout.addWidget(buttons)
        msg.exec()


