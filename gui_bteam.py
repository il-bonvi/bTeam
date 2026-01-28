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
    QTextEdit,
    QProgressBar,
)

from shared.styles import get_style
from config_bteam import ensure_storage_dir, set_storage_dir, get_intervals_api_key, set_intervals_api_key
from intervals_client import IntervalsClient
from intervals_sync import IntervalsSyncService
from storage_bteam import BTeamStorage
from dialogs import (
    SimpleAthleteDialog,
    AthleteDetailsDialog,
    SimpleActivityDialog,
    ActivityDetailsDialog,
    ManageTeamsDialog,
    IntervalsDialog,
    SyncIntervalsDialog,
    WellnessDialog,
    PlanWeekDialog,
    ExportImportDialog,
    RacesDialog,
)


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
        
        # Memorizza attività non filtrate per i filtri
        self.all_activities = []
        self.filtered_activities = []
        
        print(f"[bTeam] Cartella dati: {self.storage_dir}")
        print(f"[bTeam] Database: {self.storage_dir / 'bteam.db'}")
        print(f"[bTeam] Intervals.icu: {'[OK] Connesso' if self.sync_service.is_connected() else '[NO] Non connesso'}")

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
        btn_races = QPushButton("🏁 Race")
        btn_races.clicked.connect(self._races_dialog)
        btn_wellness = QPushButton("❤️ Tracking Benessere")
        btn_wellness.clicked.connect(self._wellness_dialog)
        btn_plan_week = QPushButton("📅 Pianifica Settimana")
        btn_plan_week.clicked.connect(self._plan_week_dialog)
        btn_export = QPushButton("💾 Export/Import")
        btn_export.clicked.connect(self._export_import_dialog)
        tools_layout.addWidget(btn_races)
        tools_layout.addWidget(btn_wellness)
        tools_layout.addWidget(btn_plan_week)
        tools_layout.addWidget(btn_export)
        tools_layout.addStretch()
        layout.addLayout(tools_layout)

        # ===== Main Content =====
        grid = QGridLayout()
        grid.setSpacing(12)

        self.athletes_table = QTableWidget(0, 4)
        self.athletes_table.setHorizontalHeaderLabels(["ID", "Rider", "Squadra", "Note"])
        self.athletes_table.horizontalHeader().setStretchLastSection(True)
        self.athletes_table.itemDoubleClicked.connect(self._edit_athlete)
        grid.addWidget(QLabel("Atleti"), 0, 0)
        grid.addWidget(self.athletes_table, 1, 0)

        self.activities_table = QTableWidget(0, 8)
        self.activities_table.setHorizontalHeaderLabels(
            ["Atleta", "Data", "Titolo", "Durata (min)", "Distanza km", "Gara", "Tag", "Azioni"]
        )
        self.activities_table.horizontalHeader().setStretchLastSection(True)
        self.activities_table.horizontalHeader().setSortIndicatorShown(True)
        self.activities_table.setSortingEnabled(False)
        self.activities_table.horizontalHeader().sectionClicked.connect(self._on_table_header_clicked)
        self.activities_table.setColumnWidth(7, 80)
        self.activities_table.itemDoubleClicked.connect(self._show_activity_details)
        self.current_sort_column = 1
        self.current_sort_order = Qt.DescendingOrder
        
        # ===== Filtri Attività =====
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtra tag:"))
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("-- Tutti --", None)
        self.tag_filter_combo.currentIndexChanged.connect(self._apply_activity_filters)
        filter_layout.addWidget(self.tag_filter_combo)
        filter_layout.addStretch()
        btn_reset_filters = QPushButton("Ripristina")
        btn_reset_filters.clicked.connect(self._reset_activity_filters)
        filter_layout.addWidget(btn_reset_filters)
        
        grid.addLayout(filter_layout, 0, 1)
        grid.addWidget(self.activities_table, 1, 1)

        layout.addLayout(grid)
        
        # ===== Recap Gare (compatto) =====
        races_recap_layout = QHBoxLayout()
        races_recap_layout.setContentsMargins(0, 10, 0, 0)
        races_recap_label = QLabel("🏁 Prossime Gare:")
        races_recap_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        races_recap_layout.addWidget(races_recap_label)
        
        self.races_recap_label = QLabel("")
        self.races_recap_label.setStyleSheet("font-size: 11px; color: #e2e8f0;")
        races_recap_layout.addWidget(self.races_recap_label)
        races_recap_layout.addStretch()
        
        layout.addLayout(races_recap_layout)
        
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
            # Colonna Rider: Cognome Nome
            rider_name = f"{athlete.get('last_name', '')} {athlete.get('first_name', '')}"
            self.athletes_table.setItem(row_idx, 1, QTableWidgetItem(rider_name))
            self.athletes_table.setItem(row_idx, 2, QTableWidgetItem(athlete.get("team_name", "")))
            self.athletes_table.setItem(row_idx, 3, QTableWidgetItem(athlete.get("notes", "")))

        # Ricarica la tabella attività con ordinamento personalizzato
        self._refresh_activities_table()
        
        # Aggiorna recap gare
        self._update_races_recap()
        
        # Ordinamento personalizzato rimane disabilitato

    def _update_races_recap(self) -> None:
        """Aggiorna il recap veloce delle prossime gare"""
        all_activities = self.storage.list_activities()
        races = [a for a in all_activities if a.get("is_race", False)]
        
        if not races:
            self.races_recap_label.setText("Nessuna gara pianificata")
            return
        
        # Ordina per data crescente (gare prossime prima)
        races = sorted(races, key=lambda x: x.get("activity_date", "")[:10])
        
        # Mostra le prossime 3 gare
        recap_items = []
        for race in races[:3]:
            title = race.get("title", "")[:30]  # Limita lunghezza titolo
            athlete = race.get("athlete_name", "").split()[0]  # Solo primo nome
            date_str = race.get("activity_date", "")[:10]
            recap_items.append(f"{athlete} - {date_str}: {title}")
        
        recap_text = " | ".join(recap_items)
        self.races_recap_label.setText(recap_text)

    def _on_table_header_clicked(self, column: int) -> None:
        """Gestisce il click sul header della tabella per ordinare"""
        # Se clicco la stessa colonna, inverti l'ordine
        if column == self.current_sort_column:
            self.current_sort_order = Qt.AscendingOrder if self.current_sort_order == Qt.DescendingOrder else Qt.DescendingOrder
        else:
            # Se clicco una colonna diversa, ordina per quella in descending
            self.current_sort_column = column
            self.current_sort_order = Qt.DescendingOrder
        
        # Aggiorna l'indicatore di sort nell'header
        self.activities_table.horizontalHeader().setSortIndicator(column, self.current_sort_order)
        
        # Ricarica la tabella con il nuovo ordine
        self._refresh_activities_table()

    def _refresh_activities_table(self) -> None:
        """Ricarica la tabella attività con ordinamento personalizzato"""
        activities = self.storage.list_activities()
        
        # Funzione per estrarre il valore di sort in base alla colonna
        def get_sort_key(activity):
            if self.current_sort_column == 0:  # Atleta
                return activity.get("athlete_name", "").lower()
            elif self.current_sort_column == 1:  # Data
                return activity.get("activity_date", "")[:10]  # YYYY-MM-DD
            elif self.current_sort_column == 2:  # Titolo
                return activity.get("title", "").lower()
            elif self.current_sort_column == 3:  # Durata
                return activity.get("duration_minutes") or 0
            elif self.current_sort_column == 4:  # Distanza
                return activity.get("distance_km") or 0
            return ""
        
        # Ordina in base alla colonna e all'ordine selezionati
        reverse = (self.current_sort_order == Qt.DescendingOrder)
        try:
            activities = sorted(activities, key=get_sort_key, reverse=reverse)
        except Exception as e:
            print(f"[bTeam] Errore ordinamento: {e}")
        
        # Disabilita sorting durante l'inserimento dati per evitare problemi
        self.activities_table.setRowCount(len(activities))
        for row_idx, activity in enumerate(activities):
            activity_id = activity["id"]
            self.activities_table.setItem(row_idx, 0, QTableWidgetItem(activity.get("athlete_name", "")))
            
            # Formatta la data dal timestamp ISO (YYYY-MM-DDTHH:MM:SS) a GG/MM/AAAA
            activity_date = activity.get("activity_date", "")
            formatted_date = activity_date  # Default
            
            try:
                if activity_date:
                    # Se è un timestamp ISO completo, estrailo direttamente
                    if "T" in activity_date:
                        date_obj = datetime.fromisoformat(activity_date.replace("Z", "+00:00"))
                        formatted_date = date_obj.strftime("%d/%m/%Y")
                    # Se è solo YYYY-MM-DD
                    elif len(activity_date) == 10:
                        date_obj = datetime.strptime(activity_date, "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%d/%m/%Y")
            except Exception as e:
                print(f"[bTeam] Errore formattazione data: {e}")
            
            self.activities_table.setItem(row_idx, 1, QTableWidgetItem(formatted_date))
            self.activities_table.setItem(row_idx, 2, QTableWidgetItem(activity.get("title", "")))
            self.activities_table.setItem(row_idx, 3, QTableWidgetItem(self._fmt_duration(activity.get("duration_minutes"))))
            self.activities_table.setItem(row_idx, 4, QTableWidgetItem(self._fmt_num(activity.get("distance_km"))))
            
            # Colonna 5: Is Race (flag)
            is_race = activity.get("is_race", False)
            race_text = "✓ Gara" if is_race else ""
            race_item = QTableWidgetItem(race_text)
            if is_race:
                race_item.setBackground(Qt.yellow)
            self.activities_table.setItem(row_idx, 5, race_item)
            
            # Colonna 6: Tags (come stringa separata da virgole)
            tags = activity.get("tags", [])
            tags_str = ", ".join(tags) if tags else ""
            self.activities_table.setItem(row_idx, 6, QTableWidgetItem(tags_str))
            
            # Aggiungi pulsante di eliminazione (colonna 7)
            delete_btn = QPushButton("Elimina")
            delete_btn.setMaximumWidth(70)
            delete_btn.clicked.connect(lambda checked, aid=activity_id: self._delete_activity(aid))
            self.activities_table.setCellWidget(row_idx, 7, delete_btn)
        
        # Memorizza tutte le attività per il filtraggio
        self.all_activities = self.storage.list_activities()
        
        # Popola il dropdown tag dal database
        self._populate_tag_filter()
        
        # Applica filtri se attivi
        self._apply_activity_filters()

    def _populate_tag_filter(self) -> None:
        """Popola il dropdown dei tag con tutti i tag unici del database"""
        all_tags = set()
        for activity in self.all_activities:
            tags = activity.get("tags", [])
            if tags:
                all_tags.update(tags)
        
        all_tags = sorted(list(all_tags))
        
        # Preserve current selection
        current_tag = self.tag_filter_combo.currentData()
        
        # Clear and rebuild
        self.tag_filter_combo.blockSignals(True)
        self.tag_filter_combo.clear()
        self.tag_filter_combo.addItem("-- Tutti --", None)
        for tag in all_tags:
            self.tag_filter_combo.addItem(tag, tag)
        
        # Restore selection
        if current_tag:
            idx = self.tag_filter_combo.findData(current_tag)
            if idx >= 0:
                self.tag_filter_combo.setCurrentIndex(idx)
        
        self.tag_filter_combo.blockSignals(False)

    def _apply_activity_filters(self) -> None:
        """Applica i filtri alle attività (tag)"""
        selected_tag = self.tag_filter_combo.currentData()
        
        # Filtra le attività
        filtered = self.all_activities
        
        if selected_tag:
            filtered = [a for a in filtered if selected_tag in a.get("tags", [])]
        
        self.filtered_activities = filtered
        
        # Applica l'ordinamento personalizzato
        def get_sort_key(activity):
            if self.current_sort_column == 0:  # Atleta
                return activity.get("athlete_name", "").lower()
            elif self.current_sort_column == 1:  # Data
                return activity.get("activity_date", "")[:10]
            elif self.current_sort_column == 2:  # Titolo
                return activity.get("title", "").lower()
            elif self.current_sort_column == 3:  # Durata
                return activity.get("duration_minutes") or 0
            elif self.current_sort_column == 4:  # Distanza
                return activity.get("distance_km") or 0
            return ""
        
        reverse = (self.current_sort_order == Qt.DescendingOrder)
        try:
            filtered = sorted(filtered, key=get_sort_key, reverse=reverse)
        except Exception as e:
            print(f"[bTeam] Errore ordinamento: {e}")
        
        # Aggiorna la tabella con i dati filtrati
        self.activities_table.setRowCount(len(filtered))
        for row_idx, activity in enumerate(filtered):
            activity_id = activity["id"]
            self.activities_table.setItem(row_idx, 0, QTableWidgetItem(activity.get("athlete_name", "")))
            
            # Formatta data
            activity_date = activity.get("activity_date", "")
            formatted_date = activity_date
            try:
                if activity_date:
                    if "T" in activity_date:
                        date_obj = datetime.fromisoformat(activity_date.replace("Z", "+00:00"))
                        formatted_date = date_obj.strftime("%d/%m/%Y")
                    elif len(activity_date) == 10:
                        date_obj = datetime.strptime(activity_date, "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%d/%m/%Y")
            except Exception as e:
                print(f"[bTeam] Errore formattazione data: {e}")
            
            self.activities_table.setItem(row_idx, 1, QTableWidgetItem(formatted_date))
            self.activities_table.setItem(row_idx, 2, QTableWidgetItem(activity.get("title", "")))
            self.activities_table.setItem(row_idx, 3, QTableWidgetItem(self._fmt_duration(activity.get("duration_minutes"))))
            self.activities_table.setItem(row_idx, 4, QTableWidgetItem(self._fmt_num(activity.get("distance_km"))))
            
            # Colonna 5: Is Race
            is_race = activity.get("is_race", False)
            race_text = "✓ Gara" if is_race else ""
            race_item = QTableWidgetItem(race_text)
            if is_race:
                race_item.setBackground(Qt.yellow)
            self.activities_table.setItem(row_idx, 5, race_item)
            
            # Colonna 6: Tags
            tags = activity.get("tags", [])
            tags_str = ", ".join(tags) if tags else ""
            self.activities_table.setItem(row_idx, 6, QTableWidgetItem(tags_str))
            
            # Colonna 7: Delete button
            delete_btn = QPushButton("Elimina")
            delete_btn.setMaximumWidth(70)
            delete_btn.clicked.connect(lambda checked, aid=activity_id: self._delete_activity(aid))
            self.activities_table.setCellWidget(row_idx, 7, delete_btn)

    def _reset_activity_filters(self) -> None:
        """Reimposta il filtro tag"""
        self.tag_filter_combo.setCurrentIndex(0)
        self._apply_activity_filters()

    @staticmethod
    def _fmt_num(value: Optional[float]) -> str:
        return "" if value is None else f"{value:.1f}"

    @staticmethod
    def _fmt_duration(minutes: Optional[float]) -> str:
        """Formatta durata da minuti a HH:MM:SS"""
        if minutes is None or minutes < 0:
            return ""
        
        total_seconds = int(minutes * 60)
        hours = total_seconds // 3600
        remaining_seconds = total_seconds % 3600
        mins = remaining_seconds // 60
        secs = remaining_seconds % 60
        
        return f"{hours}:{mins:02d}:{secs:02d}"

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
            print(f"[bTeam] Inserimento atleta: {last_name} {first_name}, squadra: {team_id}")
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
        rider_name_item = self.athletes_table.item(current_row, 1)
        
        if not athlete_id_item or not rider_name_item:
            return
        
        athlete_id = int(athlete_id_item.text())
        # Rider name è "Cognome Nome", lo splitto
        rider_name = rider_name_item.text()
        name_parts = rider_name.split(' ', 1)
        last_name = name_parts[0] if len(name_parts) > 0 else ""
        first_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Conferma eliminazione
        confirm = QDialog(self)
        confirm.setWindowTitle("Conferma eliminazione")
        layout = QVBoxLayout(confirm)
        layout.addWidget(QLabel(f"Eliminare l'atleta {last_name} {first_name}?\nQuesta azione non può essere annullata."))
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

    def _delete_activity(self, activity_id: int) -> None:
        """Elimina un'attività dopo conferma"""
        confirm_dialog = QDialog(self)
        confirm_dialog.setWindowTitle("Conferma eliminazione")
        confirm_dialog.setMinimumWidth(300)
        layout = QVBoxLayout(confirm_dialog)
        
        layout.addWidget(QLabel("Sei sicuro di voler eliminare questa attività?"))
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(confirm_dialog.accept)
        buttons.rejected.connect(confirm_dialog.reject)
        layout.addWidget(buttons)
        
        if confirm_dialog.exec():
            if self.storage.delete_activity(activity_id):
                self._refresh_tables()
                self._refresh_stats()
                print(f"[bTeam] Attività {activity_id} eliminata")
            else:
                error_dialog = QDialog(self)
                error_dialog.setWindowTitle("Errore")
                error_layout = QVBoxLayout(error_dialog)
                error_layout.addWidget(QLabel("Errore durante l'eliminazione dell'attività"))
                error_buttons = QDialogButtonBox(QDialogButtonBox.Ok)
                error_buttons.accepted.connect(error_dialog.accept)
                error_layout.addWidget(error_buttons)
                error_dialog.exec()

    def _download_fit_file(self, activity_id: int, intervals_id: str, activity_title: str, athlete_name: str, details_dialog: QDialog) -> None:
        """Scarica il file FIT da Intervals.icu e lo salva localmente"""
        try:
            if not self.sync_service.is_connected():
                QMessageBox.warning(self, "Errore", "Non connesso a Intervals.icu")
                return
            
            # Crea cartella fit_library se non esiste
            fit_library = self.storage.storage_dir / "fit_library"
            fit_library.mkdir(parents=True, exist_ok=True)
            
            # Struttura cartella: fit_library/{athlete_name}/{YYYY}/{MM}/
            from datetime import datetime
            activity = self.storage.get_activity(activity_id)
            if not activity:
                QMessageBox.warning(self, "Errore", "Attività non trovata nel database")
                return
            
            # Parse activity date
            activity_date_str = activity.get("activity_date", "")
            try:
                if "T" in activity_date_str:
                    date_obj = datetime.fromisoformat(activity_date_str.replace("Z", "+00:00"))
                elif len(activity_date_str) == 10:
                    date_obj = datetime.strptime(activity_date_str, "%Y-%m-%d")
                else:
                    date_obj = datetime.now()
            except:
                date_obj = datetime.now()
            
            # Crea struttura cartella
            year_month_dir = fit_library / athlete_name / str(date_obj.year) / f"{date_obj.month:02d}"
            year_month_dir.mkdir(parents=True, exist_ok=True)
            
            # Nome file: {activity_id}_{title}.fit
            sanitized_title = activity_title.replace("/", "_").replace("\\", "_")[:50]
            fit_filename = f"{activity_id}_{sanitized_title}.fit"
            fit_path = year_month_dir / fit_filename
            
            # Mostra progress dialog
            progress = QDialog(self)
            progress.setWindowTitle("Download FIT")
            progress.setMinimumWidth(300)
            progress_layout = QVBoxLayout(progress)
            progress_layout.addWidget(QLabel(f"Scaricamento: {activity_title}..."))
            progress_bar = QProgressBar()
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(0)  # Indeterminate
            progress_layout.addWidget(progress_bar)
            progress.show()
            
            # Scarica file FIT
            print(f"[bTeam] Scaricamento FIT da Intervals per attività {intervals_id}...")
            fit_content = self.sync_service.api_client.download_activity_fit_file(
                activity_id=str(intervals_id),
                save_path=str(fit_path)
            )
            
            # Salva nel database
            from datetime import datetime as dt
            file_size_kb = len(fit_content) / 1024
            now = dt.utcnow().isoformat()
            self.storage.session.execute(
                f"""INSERT INTO fit_files (activity_id, file_path, file_size_kb, downloaded_at, intervals_id, created_at)
                   VALUES ({activity_id}, '{fit_path.relative_to(self.storage.storage_dir)}', {file_size_kb}, '{now}', '{intervals_id}', '{now}')"""
            )
            self.storage.session.commit()
            
            progress.close()
            
            QMessageBox.information(
                self, 
                "Download completato",
                f"FIT salvato in:\n{fit_path}"
            )
            
            print(f"[bTeam] FIT scaricato e salvato: {fit_path}")
            
        except Exception as e:
            print(f"[bTeam] Errore download FIT: {e}")
            QMessageBox.critical(self, "Errore", f"Errore durante il download: {str(e)}")

    def _show_activity_details(self, item: QTableWidgetItem) -> None:
        """Mostra i dettagli dell'attività in un dialog"""
        row = item.row()
        # Estrai i dati della riga per identificare l'attività
        athlete_item = self.activities_table.item(row, 0)
        title_item = self.activities_table.item(row, 2)
        date_item = self.activities_table.item(row, 1)
        
        if not (athlete_item and title_item and date_item):
            return
        
        # Cerca l'attività nel database basandosi su atleta, data e titolo
        try:
            athlete_name = athlete_item.text()
            title = title_item.text()
            activity_date = date_item.text()
            
            # Cerca l'attività
            all_activities = self.storage.list_activities()
            activity = None
            for act in all_activities:
                if (act.get("athlete_name") == athlete_name and 
                    act.get("title") == title and 
                    act.get("activity_date") == activity_date):
                    activity = act
                    break
            
            if not activity:
                return
            
            # Crea dialog dettagli
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle("Dettagli Attività")
            details_dialog.setMinimumWidth(500)
            layout = QVBoxLayout(details_dialog)
            
            # Titolo principale
            title_label = QLabel(activity.get("title", ""))
            title_font = title_label.font()
            title_font.setBold(True)
            title_font.setPointSize(12)
            title_label.setFont(title_font)
            layout.addWidget(title_label)
            
            # Divider
            divider = QLabel("-" * 50)
            divider.setStyleSheet("color: #999;")
            layout.addWidget(divider)
            
            # Info grid
            grid = QGridLayout()
            grid.setSpacing(10)
            grid.setColumnMinimumWidth(1, 250)
            
            row_idx = 0
            fields = [
                ("ID", str(activity.get("id", ""))),
                ("Atleta", activity.get("athlete_name", "")),
                ("Data", activity.get("activity_date", "")),
                ("Durata (min)", self._fmt_num(activity.get("duration_minutes"))),
                ("Distanza (km)", self._fmt_num(activity.get("distance_km"))),
                ("TSS", self._fmt_num(activity.get("tss"))),
                ("Fonte", activity.get("source", "manual").capitalize()),
                ("Creato il", activity.get("created_at", "")),
                ("Gara", "✓ Sì" if activity.get("is_race") else "No"),
                ("Tag", ", ".join(activity.get("tags", []))),
            ]
            
            for label_text, value_text in fields:
                label = QLabel(f"{label_text}:")
                label.setStyleSheet("font-weight: bold;")
                value = QLabel(value_text)
                grid.addWidget(label, row_idx, 0)
                grid.addWidget(value, row_idx, 1)
                row_idx += 1
            
            layout.addLayout(grid)
            
            # Payload JSON (se disponibile)
            if activity.get("intervals_payload"):
                layout.addSpacing(10)
                payload_label = QLabel("Dati Intervals:")
                payload_label.setStyleSheet("font-weight: bold;")
                layout.addWidget(payload_label)
                
                payload_text = QTextEdit()
                payload_text.setReadOnly(True)
                payload_text.setMaximumHeight(150)
                try:
                    import json
                    payload_data = json.loads(activity.get("intervals_payload"))
                    payload_text.setPlainText(json.dumps(payload_data, indent=2, ensure_ascii=False))
                except:
                    payload_text.setPlainText(activity.get("intervals_payload", ""))
                layout.addWidget(payload_text)
            
            layout.addStretch()
            
            # Pulsanti personalizzati
            buttons_layout = QHBoxLayout()
            
            # Pulsante download FIT (se attività da Intervals)
            if activity.get("source") == "intervals":
                fit_btn = QPushButton("💾 Scarica FIT")
                fit_btn.clicked.connect(lambda: self._download_fit_file(
                    activity_id=activity.get("id"),
                    intervals_id=activity.get("id"),  # ID Intervals
                    activity_title=activity.get("title"),
                    athlete_name=activity.get("athlete_name"),
                    details_dialog=details_dialog
                ))
                buttons_layout.addWidget(fit_btn)
            
            buttons_layout.addStretch()
            
            # Pulsante chiusura
            close_btn = QPushButton("Chiudi")
            close_btn.clicked.connect(details_dialog.accept)
            buttons_layout.addWidget(close_btn)
            
            layout.addLayout(buttons_layout)
            
            details_dialog.exec()
            
        except Exception as e:
            print(f"[bTeam] Errore mostra dettagli: {e}")

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
        activities, fetch_message = self.sync_service.fetch_activities(days_back=days_back)
        
        new_count = 0
        duplicate_count = 0
        error_count = 0
        
        if activities:
            # Salva le attività nell'app
            for activity in activities:
                try:
                    formatted = IntervalsSyncService.format_activity_for_storage(activity)
                    activity_id, is_new = self.storage.add_activity(
                        athlete_id=athlete_id,
                        title=formatted['name'],
                        activity_date=formatted['start_date'],
                        duration_minutes=formatted['moving_time_minutes'],
                        distance_km=formatted['distance_km'],
                        tss=None,  # Non disponibile da Intervals
                        source='intervals',
                        intervals_id=str(formatted['intervals_id']),
                        # 🆕 Nuovi campi dalla sincronizzazione
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
                    print(f"[bTeam] Errore inserimento attività: {e}")
            
            # Costruisci messaggio dettagliato
            parts = []
            if new_count > 0:
                parts.append(f"✅ {new_count} nuove attività")
            if duplicate_count > 0:
                parts.append(f"⚠️  {duplicate_count} già presenti (duplicate)")
            if error_count > 0:
                parts.append(f"❌ {error_count} errori")
            
            message = "Sincronizzazione completata:\n" + "\n".join(parts) if parts else "✅ Nessuna attività da sincronizzare"
        else:
            message = "✅ Nessuna attività trovata negli ultimi " + str(days_back) + " giorni"
        
        print(f"[bTeam] {message}")
        
        # Mostra risultato con dialog migliorato
        result_dialog = QDialog(self)
        result_dialog.setWindowTitle("Risultato sincronizzazione")
        result_dialog.setMinimumWidth(350)
        layout = QVBoxLayout(result_dialog)
        
        # Titolo
        title_label = QLabel("Sincronizzazione Intervals.icu")
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Messaggio
        msg_label = QLabel(message)
        msg_label.setStyleSheet("margin-top: 10px; margin-bottom: 10px;")
        layout.addWidget(msg_label)
        
        # Pulsanti
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(result_dialog.accept)
        layout.addWidget(buttons)
        
        result_dialog.exec()
        
        # Aggiorna tabelle
        self._refresh_tables()
        self._refresh_stats()

    def _races_dialog(self) -> None:
        """Apre il dialog per gestire gare pianificate (standalone, non vincolate a atleta)"""
        races_dialog = RacesDialog(self, self.storage)
        races_dialog.exec()

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


def main(theme: Optional[str] = None) -> None:
    """Main entry point for the bTeam application."""
    app = QApplication.instance() or QApplication([])
    window = BTeamApp(theme=theme)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
