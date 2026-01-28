# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLineEdit,
    QDialogButtonBox,
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
    ManageTeamsDialog,
)

# Sezioni modularizzate
from sections import ui_builder, tables, filters
from sections.dialogs_handlers import show_error_dialog, show_confirmation_dialog
from sections.activity_handlers import (
    show_activity_details,
    delete_activity_with_confirmation,
    download_fit_file,
)
from sections.sync_handlers import (
    show_sync_intervals_dialog,
    show_wellness_dialog,
    show_plan_week_dialog,
    show_races_dialog,
    show_export_import_dialog,
)


class BTeamApp(QMainWindow):
    """Applicazione principale bTeam - Team Dashboard"""
    
    def __init__(self, theme: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("bTeam - Team Dashboard")
        self.setMinimumSize(1100, 800)
        self.current_theme = theme or "Forest Green"
        self.setStyleSheet(get_style(self.current_theme))

        # ===== Inizializzazione servizi =====
        self.storage_dir = ensure_storage_dir()
        self.storage = BTeamStorage(self.storage_dir)
        self.intervals_client = IntervalsClient()
        
        api_key = get_intervals_api_key()
        self.sync_service = IntervalsSyncService(api_key=api_key)
        
        # Stato applicazione
        self.all_activities = []
        self.filtered_activities = []
        self.current_sort_column = 1
        self.current_sort_order = Qt.DescendingOrder
        
        print(f"[bTeam] Cartella dati: {self.storage_dir}")
        print(f"[bTeam] Database: {self.storage_dir / 'bteam.db'}")
        print(f"[bTeam] Intervals.icu: {'[OK] Connesso' if self.sync_service.is_connected() else '[NO] Non connesso'}")

        self._build_ui()
        self._refresh_tables()
        self._refresh_stats()

    # ===== UI BUILDER =====
    
    def _build_ui(self) -> None:
        """Costruisce l'interfaccia utente delegando ai builder"""
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        header = QLabel("bTeam | Dashboard Squadra")
        header.setAlignment(Qt.AlignLeft)
        header.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(header)

        # Path section
        path_layout, self.path_label = ui_builder.build_path_section(
            self.storage_dir, 
            self._choose_storage_dir
        )
        layout.addLayout(path_layout)

        # Stats section
        stats_layout, self.stats_label = ui_builder.build_stats_section()
        layout.addLayout(stats_layout)

        # Filter section
        filter_layout, self.filter_team_combo = ui_builder.build_filter_section(
            self._refresh_tables,
            self._manage_teams_dialog,
            self._sync_intervals_dialog
        )
        layout.addLayout(filter_layout)

        # Action buttons
        action_layout = ui_builder.build_action_buttons(
            self._add_team_dialog,
            self._add_athlete_dialog,
            self._delete_athlete,
            self._add_activity_dialog
        )
        layout.addLayout(action_layout)

        # Tools toolbar
        tools_layout = ui_builder.build_tools_toolbar(
            self._races_dialog,
            self._wellness_dialog,
            self._plan_week_dialog,
            self._export_import_dialog
        )
        layout.addLayout(tools_layout)

        # Main content: Tables
        grid = QGridLayout()
        grid.setSpacing(12)

        # Athletes table
        self.athletes_table, _ = ui_builder.build_athletes_table()
        self.athletes_table.itemDoubleClicked.connect(self._edit_athlete)
        grid.addWidget(QLabel("Atleti"), 0, 0)
        grid.addWidget(self.athletes_table, 1, 0)

        # Activities table
        self.activities_table = ui_builder.build_activities_table()
        self.activities_table.itemDoubleClicked.connect(self._show_activity_details)
        self.activities_table.horizontalHeader().sectionClicked.connect(self._on_table_header_clicked)

        # Activity filters
        filter_act_layout = QHBoxLayout()
        filter_act_layout.addWidget(QLabel("Filtra tag:"))
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("-- Tutti --", None)
        self.tag_filter_combo.currentIndexChanged.connect(self._apply_activity_filters)
        filter_act_layout.addWidget(self.tag_filter_combo)
        filter_act_layout.addStretch()
        btn_reset_filters = QPushButton("Ripristina")
        btn_reset_filters.clicked.connect(self._reset_activity_filters)
        filter_act_layout.addWidget(btn_reset_filters)
        
        grid.addLayout(filter_act_layout, 0, 1)
        grid.addWidget(self.activities_table, 1, 1)

        layout.addLayout(grid)
        
        # Races recap
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

    # ===== REFRESH TABLES SECTION =====
    
    def _refresh_stats(self) -> None:
        """Aggiorna le statistiche e il dropdown squadre"""
        stats = self.storage.stats()
        self.stats_label.setText(f"Atleti: {stats['athletes']} | Attività: {stats['activities']}")
        
        # Aggiorna filtro squadre
        current_team = self.filter_team_combo.currentData()
        self.filter_team_combo.blockSignals(True)
        self.filter_team_combo.clear()
        self.filter_team_combo.addItem("Tutte", None)
        for team in self.storage.list_teams():
            self.filter_team_combo.addItem(team["name"], team["id"])
        
        if current_team:
            idx = self.filter_team_combo.findData(current_team)
            if idx >= 0:
                self.filter_team_combo.setCurrentIndex(idx)
        self.filter_team_combo.blockSignals(False)

    def _refresh_tables(self) -> None:
        """Ricarica tabelle atleti e attività"""
        selected_team = self.filter_team_combo.currentData()
        all_athletes = self.storage.list_athletes()
        
        # Filtra per squadra se selezionato
        if selected_team:
            athletes = [a for a in all_athletes if a.get("team_id") == selected_team]
        else:
            athletes = all_athletes
        
        # Popola tabella atleti
        tables.refresh_athletes_table(self.storage, self.athletes_table, athletes)

        # Ricarica attività
        self._refresh_activities_table()
        
        # Aggiorna recap gare
        tables.update_races_recap(self.storage, self.races_recap_label)

    def _refresh_activities_table(self) -> None:
        """Ricarica la tabella attività con ordinamento personalizzato"""
        all_activities = self.storage.list_activities()
        
        tables.refresh_activities_table(
            self.storage,
            self.activities_table,
            all_activities,
            self.current_sort_column,
            self.current_sort_order,
            self._delete_activity
        )
        
        # Memorizza tutte le attività
        self.all_activities = all_activities
        
        # Popola tag filter
        tables.populate_tag_filter(self.tag_filter_combo, all_activities)
        
        # Applica filtri
        self._apply_activity_filters()

    # ===== FILTER SECTION =====
    
    def _on_table_header_clicked(self, column: int) -> None:
        """Gestisce il click sul header della tabella per ordinare"""
        self.current_sort_column, self.current_sort_order = filters.handle_sort_column_click(
            column, self.current_sort_column, self.current_sort_order
        )
        self.activities_table.horizontalHeader().setSortIndicator(column, self.current_sort_order)
        self._refresh_activities_table()

    def _apply_activity_filters(self) -> None:
        """Applica i filtri alle attività (tag)"""
        filtered = filters.apply_activity_filters(
            self.all_activities,
            self.tag_filter_combo,
            self.current_sort_column,
            self.current_sort_order
        )
        
        self.filtered_activities = filtered
        
        # Aggiorna tabella con dati filtrati
        self.activities_table.setRowCount(len(filtered))
        for row_idx, activity in enumerate(filtered):
            activity_id = activity["id"]
            self.activities_table.setItem(row_idx, 0, QTableWidgetItem(activity.get("athlete_name", "")))
            
            formatted_date = tables.format_date(activity.get("activity_date", ""))
            self.activities_table.setItem(row_idx, 1, QTableWidgetItem(formatted_date))
            self.activities_table.setItem(row_idx, 2, QTableWidgetItem(activity.get("title", "")))
            self.activities_table.setItem(row_idx, 3, QTableWidgetItem(tables.fmt_duration(activity.get("duration_minutes"))))
            self.activities_table.setItem(row_idx, 4, QTableWidgetItem(tables.fmt_num(activity.get("distance_km"))))
            
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

    # ===== DIALOG HANDLERS SECTION =====
    
    def _add_team_dialog(self) -> None:
        """Dialogo per aggiungere una squadra"""
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
                self._refresh_stats()

    def _add_athlete_dialog(self) -> None:
        """Dialogo per aggiungere un atleta"""
        dialog = SimpleAthleteDialog(self, self.storage.list_teams())
        if dialog.exec():
            first_name, last_name, team_id = dialog.values()
            if not first_name.strip() or not last_name.strip():
                show_error_dialog(self, "Campo obbligatorio", "Inserisci nome e cognome atleta")
                return
            print(f"[bTeam] Inserimento atleta: {last_name} {first_name}, squadra: {team_id}")
            athlete_id = self.storage.add_athlete(first_name=first_name, last_name=last_name, team_id=team_id)
            print(f"[bTeam] Atleta creato con ID: {athlete_id}")
            self._refresh_tables()
            self._refresh_stats()

    def _manage_teams_dialog(self) -> None:
        """Dialogo per gestire squadre"""
        dialog = ManageTeamsDialog(self, self.storage)
        dialog.exec()
        self._refresh_tables()
        self._refresh_stats()

    def _edit_athlete(self, item) -> None:
        """Modifica dettagli atleta dal doppio click"""
        row = item.row()
        athlete_id_item = self.athletes_table.item(row, 0)
        if athlete_id_item:
            athlete_id = int(athlete_id_item.text())
            self._edit_athlete_details(athlete_id)

    def _edit_athlete_details(self, athlete_id: int) -> None:
        """Dialogo dettagli atleta"""
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
        """Elimina atleta selezionato"""
        current_row = self.athletes_table.currentRow()
        if current_row < 0:
            show_error_dialog(self, "Seleziona un atleta", "Seleziona un atleta da eliminare")
            return
        
        athlete_id_item = self.athletes_table.item(current_row, 0)
        rider_name_item = self.athletes_table.item(current_row, 1)
        
        if not athlete_id_item or not rider_name_item:
            return
        
        athlete_id = int(athlete_id_item.text())
        rider_name = rider_name_item.text()
        
        # Conferma eliminazione
        if show_confirmation_dialog(self, "Conferma eliminazione", 
                                   f"Eliminare l'atleta {rider_name}?\nQuesta azione non può essere annullata."):
            self.storage.delete_athlete(athlete_id)
            self._refresh_tables()
            self._refresh_stats()

    def _add_activity_dialog(self) -> None:
        """Dialogo per aggiungere un'attività"""
        athletes = self.storage.list_athletes()
        if not athletes:
            show_error_dialog(self, "Nessun atleta", "Aggiungi un atleta prima di inserire attività")
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

    # ===== ACTIVITY HANDLERS SECTION =====
    
    def _show_activity_details(self, item: QTableWidgetItem) -> None:
        """Mostra dettagli attività"""
        row = item.row()
        athlete_item = self.activities_table.item(row, 0)
        title_item = self.activities_table.item(row, 2)
        date_item = self.activities_table.item(row, 1)
        
        if not (athlete_item and title_item and date_item):
            return
        
        try:
            athlete_name = athlete_item.text()
            title = title_item.text()
            activity_date = date_item.text()
            
            # Cerca l'attività
            all_activities = self.storage.list_activities()
            activity = None
            for act in all_activities:
                if (act.get("athlete_name") == athlete_name and 
                    act.get("title") == title):
                    activity = act
                    break
            
            if activity:
                show_activity_details(
                    self, 
                    self.storage, 
                    activity.get("id"), 
                    self._on_download_fit
                )
        except Exception as e:
            print(f"[bTeam] Errore mostra dettagli: {e}")

    def _delete_activity(self, activity_id: int) -> None:
        """Elimina un'attività"""
        if delete_activity_with_confirmation(self, self.storage, activity_id):
            self._refresh_tables()
            self._refresh_stats()

    def _on_download_fit(self, activity_id: int, intervals_id: str, activity_title: str, athlete_name: str, details_dialog) -> None:
        """Callback per il download FIT"""
        download_fit_file(self, self.storage, self.sync_service, activity_id, intervals_id, activity_title, athlete_name)
        details_dialog.close()

    # ===== SYNC HANDLERS SECTION =====
    
    def _sync_intervals_dialog(self) -> None:
        """Dialogo sincronizzazione Intervals"""
        show_sync_intervals_dialog(self, self.sync_service, self.storage, self._on_sync_complete)

    def _on_sync_complete(self) -> None:
        """Callback al termine della sincronizzazione"""
        self._refresh_tables()
        self._refresh_stats()

    def _races_dialog(self) -> None:
        """Dialogo gestione gare"""
        show_races_dialog(self, self.storage)
        self._refresh_tables()

    def _wellness_dialog(self) -> None:
        """Dialogo tracking benessere"""
        show_wellness_dialog(self, self.sync_service)

    def _plan_week_dialog(self) -> None:
        """Dialogo pianificazione settimana"""
        show_plan_week_dialog(self, self.sync_service, self._on_plan_created)

    def _on_plan_created(self) -> None:
        """Callback al termine della pianificazione"""
        pass

    def _export_import_dialog(self) -> None:
        """Dialogo export/import"""
        show_export_import_dialog(self, self.storage)

    # ===== UTILITIES SECTION =====
    
    def _choose_storage_dir(self) -> None:
        """Scegli cartella dati"""
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
