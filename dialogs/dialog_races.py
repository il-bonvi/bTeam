# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

from datetime import datetime
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)

from storage_bteam import BTeamStorage
from dialogs.race_create_dialog import RaceCreateDialog
from dialogs.race_details_dialog import RaceDetailsDialog


class RacesDialog(QDialog):
    """Dialog per gestire gare pianificate (standalone, non vincolate a atleta)"""
    
    def __init__(self, parent, storage: BTeamStorage):
        super().__init__(parent)
        self.setWindowTitle("🏁 Gestione Gare")
        self.setMinimumSize(1200, 800)
        self.storage = storage
        self.selected_race_file = None
        
        self._build_ui()
        self._load_races()
        
        # Mostra a schermo intero
        self.showMaximized()
    
    def _build_ui(self) -> None:
        """Costruisce l'interfaccia del dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Header con bottone Add Race
        header_layout = QHBoxLayout()
        races_label = QLabel("Gare Pianificate")
        races_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(races_label)
        
        add_btn = QPushButton("+ Add Race")
        add_btn.setStyleSheet("background-color: #4ade80; color: black; font-weight: bold; padding: 6px 12px;")
        add_btn.setMaximumWidth(150)
        add_btn.clicked.connect(self._on_add_race)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        # Tabella gare
        self.races_table = QTableWidget(0, 10)
        self.races_table.setHorizontalHeaderLabels([
            "Data", "Nome", "Genere", "Categoria", "Distanza (km)", "Dislivello (m)",
            "Media (km/h)", "Durata (h:m)", "KJ prev.", "Elimina"
        ])
        self.races_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.races_table.cellDoubleClicked.connect(self._on_race_table_double_click)
        self.races_table.horizontalHeader().setStretchLastSection(False)
        layout.addWidget(self.races_table)
        
        # Pulsanti inferiori
        buttons_layout = QHBoxLayout()
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
    
    def _on_add_race(self) -> None:
        """Apre il dialog per creare una nuova gara"""
        dialog = RaceCreateDialog(self, self.storage)
        if dialog.exec():
            self._load_races()
    
    def _load_races(self) -> None:
        """Carica tutte le gare"""
        races = self.storage.list_races()
        
        self.races_table.setRowCount(len(races))
        for row_idx, race in enumerate(races):
            race_id = race.get("id")
            
            # Formatta data
            race_date = race.get("race_date", "")
            try:
                if len(race_date) == 10:
                    date_obj = datetime.strptime(race_date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%d/%m/%Y")
            except:
                formatted_date = race_date
            
            # Formatta durata
            duration_minutes = race.get("predicted_duration_minutes", 0) or 0
            hours = int(duration_minutes // 60)
            minutes = int(duration_minutes % 60)
            duration_str = f"{hours}h {minutes}m" if duration_minutes > 0 else "--"
            
            # Formatta KJ
            kj = race.get("predicted_kj")
            kj_str = f"{kj:.0f}" if kj else "--"
            
            # Popola righe
            self.races_table.setItem(row_idx, 0, QTableWidgetItem(formatted_date))
            self.races_table.setItem(row_idx, 1, QTableWidgetItem(race.get("name", "")))
            self.races_table.setItem(row_idx, 2, QTableWidgetItem(race.get("gender", "")))
            self.races_table.setItem(row_idx, 3, QTableWidgetItem(race.get("category", "")))
            self.races_table.setItem(row_idx, 4, QTableWidgetItem(str(race.get("distance_km", ""))))
            self.races_table.setItem(row_idx, 5, QTableWidgetItem(str(race.get("elevation_m", ""))))
            self.races_table.setItem(row_idx, 6, QTableWidgetItem(str(race.get("avg_speed_kmh", ""))))
            self.races_table.setItem(row_idx, 7, QTableWidgetItem(duration_str))
            self.races_table.setItem(row_idx, 8, QTableWidgetItem(kj_str))
            
            # Pulsante elimina
            delete_btn = QPushButton("Elimina")
            delete_btn.setMaximumWidth(70)
            delete_btn.clicked.connect(lambda checked, rid=race_id: self._delete_race(rid))
            self.races_table.setCellWidget(row_idx, 9, delete_btn)
    
    def _on_race_table_double_click(self, row: int, column: int) -> None:
        """Apre il dialog dettagli della gara al doppio clic"""
        # Non apre il dialog se si clicca sul bottone Elimina (colonna 9)
        if column == 9:
            return
        
        try:
            races = self.storage.list_races()
            if row < len(races):
                race_id = races[row].get("id")
                self._open_race_details(race_id)
        except Exception as e:
            print(f"[bTeam] Errore apertura dettagli gara: {e}")
    
    def _open_race_details(self, race_id: int) -> None:
        """Apre il dialog per modificare i dettagli della gara"""
        try:
            dialog = RaceDetailsDialog(self, self.storage, race_id)
            if dialog.exec():
                self._load_races()
        except Exception as e:
            print(f"[bTeam] Errore apertura dettagli gara: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Errore", f"Errore apertura gara: {str(e)}")
    
    def _delete_race(self, race_id: int) -> None:
        """Elimina una gara dopo conferma"""
        confirm = QMessageBox.question(
            self,
            "Conferma eliminazione",
            "Sei sicuro di voler eliminare questa gara?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            # Prima elimina tutti gli atleti associati alla gara
            if not self.storage.delete_race_athletes_by_race_id(race_id):
                QMessageBox.warning(self, "Errore", "Errore nell'eliminazione degli atleti dalla gara")
                return
            
            # Poi elimina la gara
            if self.storage.delete_race(race_id):
                self._load_races()
                QMessageBox.information(self, "Eliminata", "Gara eliminata con successo!")
            else:
                QMessageBox.critical(self, "Errore", "Errore nell'eliminazione della gara")
