# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List, Dict
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QDoubleSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QTextEdit,
    QSpinBox,
)

from storage_bteam import BTeamStorage


class RaceDetailsDialog(QDialog):
    """Dialog per modificare i dettagli di una gara."""
    
    def __init__(self, parent, storage: BTeamStorage, race_id: int):
        super().__init__(parent)
        self.setWindowTitle("Modifica Gara")
        self.setMinimumSize(600, 500)
        self.storage = storage
        self.race_id = race_id
        self.race_data = None
        
        self._load_race_data()
        self._build_ui()
    
    def _load_race_data(self) -> None:
        """Carica i dati della gara dal database."""
        self.race_data = self.storage.get_race(self.race_id)
    
    def _build_ui(self) -> None:
        """Costruisce l'interfaccia del dialog."""
        if not self.race_data:
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Gara non trovata"))
            return
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Nome
        layout.addWidget(QLabel("Nome gara:"))
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.race_data.get("name", ""))
        layout.addWidget(self.name_edit)
        
        # Data
        layout.addWidget(QLabel("Data:"))
        self.date_edit = QDateEdit()
        race_date = self.race_data.get("race_date", "")
        if len(race_date) == 10:
            self.date_edit.setDate(datetime.strptime(race_date, "%Y-%m-%d").date())
        self.date_edit.setCalendarPopup(True)
        layout.addWidget(self.date_edit)
        
        # Genere e Categoria
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(QLabel("Genere:"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Femminile", "Maschile"])
        self.gender_combo.setCurrentText(self.race_data.get("gender", "Femminile"))
        # NON collegare il signal ancora, lo farò dopo aver caricato le categorie
        gender_layout.addWidget(self.gender_combo)
        
        gender_layout.addWidget(QLabel("Categoria:"))
        self.category_combo = QComboBox()
        # Prima popola le categorie
        self._update_categories()
        # Poi imposta la categoria salvata
        saved_category = self.race_data.get("category", "")
        if saved_category:
            idx = self.category_combo.findText(saved_category)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
        # Ora collega il signal
        self.gender_combo.currentIndexChanged.connect(self._update_categories)
        gender_layout.addStretch()
        layout.addLayout(gender_layout)
        
        # Distanza
        distance_layout = QHBoxLayout()
        distance_layout.addWidget(QLabel("Distanza (km):"))
        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setMinimum(0.1)
        self.distance_spin.setMaximum(500)
        self.distance_spin.setSingleStep(1)
        self.distance_spin.setDecimals(1)
        self.distance_spin.setValue(self.race_data.get("distance_km", 100))
        self.distance_spin.valueChanged.connect(self._update_predictions)
        distance_layout.addWidget(self.distance_spin)
        
        distance_layout.addWidget(QLabel("Dislivello (m):"))
        self.elevation_spin = QSpinBox()
        self.elevation_spin.setMinimum(0)
        self.elevation_spin.setMaximum(10000)
        self.elevation_spin.setSingleStep(50)
        self.elevation_spin.setValue(int(self.race_data.get("elevation_m", 0) or 0))
        distance_layout.addWidget(self.elevation_spin)
        distance_layout.addStretch()
        layout.addLayout(distance_layout)
        
        # Media prevista e Durata prevista
        media_layout = QHBoxLayout()
        media_layout.addWidget(QLabel("Media prevista (km/h):"))
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setMinimum(1)
        self.speed_spin.setMaximum(60)
        self.speed_spin.setSingleStep(0.5)
        self.speed_spin.setDecimals(1)
        self.speed_spin.setValue(self.race_data.get("avg_speed_kmh", 25))
        self.speed_spin.valueChanged.connect(self._update_predictions)
        media_layout.addWidget(self.speed_spin)
        
        media_layout.addWidget(QLabel("Durata prevista (h:m):"))
        self.duration_edit = QLineEdit()
        self.duration_edit.setReadOnly(True)
        self.duration_edit.setStyleSheet("background-color: #f0f0f0; color: #4ade80; font-weight: bold;")
        duration_minutes = self.race_data.get("predicted_duration_minutes", 0) or 0
        hours = int(duration_minutes // 60)
        minutes = int(duration_minutes % 60)
        self.duration_edit.setText(f"{hours}h {minutes}m" if duration_minutes > 0 else "--")
        media_layout.addWidget(self.duration_edit)
        media_layout.addStretch()
        layout.addLayout(media_layout)
        
        # Note
        layout.addWidget(QLabel("Note:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(self.race_data.get("notes", ""))
        self.notes_edit.setMaximumHeight(80)
        layout.addWidget(self.notes_edit)
        
        # KJ previsti (read-only)
        kj_layout = QHBoxLayout()
        kj_layout.addWidget(QLabel("KJ previsti (media):"))
        self.kj_edit = QLineEdit()
        self.kj_edit.setReadOnly(True)
        self.kj_edit.setStyleSheet("background-color: #f0f0f0; color: #60a5fa; font-weight: bold;")
        kj = self.race_data.get("predicted_kj", 0)
        self.kj_edit.setText(f"{kj:.0f}" if kj else "--")
        kj_layout.addWidget(self.kj_edit)
        kj_layout.addStretch()
        layout.addLayout(kj_layout)
        
        layout.addStretch()
        
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
    
    def _update_categories(self) -> None:
        """Aggiorna le categorie in base al genere."""
        gender = self.gender_combo.currentText()
        categories = {
            "Femminile": ["Allieve", "Junior", "Junior 1NC", "Junior 2NC", "Junior (OPEN)", "OPEN"],
            "Maschile": ["U23"]
        }
        
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItems(categories.get(gender, []))
        self.category_combo.blockSignals(False)
    
    def _update_predictions(self) -> None:
        """Aggiorna previsioni di durata e KJ quando cambia media o distanza."""
        distance_km = self.distance_spin.value()
        speed_kmh = self.speed_spin.value()
        
        if speed_kmh <= 0:
            self.duration_edit.setText("--")
            self.kj_edit.setText("--")
            return
        
        # Calcola durata
        duration_minutes = (distance_km / speed_kmh) * 60
        hours = int(duration_minutes // 60)
        minutes = int(duration_minutes % 60)
        self.duration_edit.setText(f"{hours}h {minutes}m")
        
        # Calcola KJ
        duration_hours = duration_minutes / 60
        athletes = self.storage.list_athletes()
        
        if athletes:
            total_kj = 0
            for athlete in athletes:
                weight_kg = athlete.get("weight_kg", 70) or 70
                kj_per_hora_per_kg = athlete.get("kj_per_hour_per_kg", 1.0) or 1.0
                total_kj += kj_per_hora_per_kg * duration_hours * weight_kg
            avg_kj = total_kj / len(athletes)
            self.kj_edit.setText(f"{avg_kj:.0f}")
        else:
            self.kj_edit.setText("--")
    
    def _save_changes(self) -> None:
        """Salva le modifiche nel database."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Campo obbligatorio", "Inserisci il nome della gara")
            return
        
        race_date = self.date_edit.date().toString("yyyy-MM-dd")
        distance_km = self.distance_spin.value()
        elevation_m = self.elevation_spin.value()
        speed_kmh = self.speed_spin.value()
        gender = self.gender_combo.currentText()
        category = self.category_combo.currentText()
        notes = self.notes_edit.toPlainText().strip()
        
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
        
        # Aggiorna nel database
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


class RacesDialog(QDialog):
    """Dialog per gestire gare pianificate (standalone, non vincolate a atleta)."""
    
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
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # ===== FORM NUOVA GARA =====
        form_label = QLabel("Crea Nuova Gara")
        form_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(form_label)
        
        form_layout = QVBoxLayout()
        
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
        form_layout.addLayout(row1_layout)
        
        # Row 2: Genere, Categoria
        row2_layout = QHBoxLayout()
        row2_layout.addWidget(QLabel("Genere:"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Femminile", "Maschile"])
        self.gender_combo.currentIndexChanged.connect(self._update_categories)
        row2_layout.addWidget(self.gender_combo)
        
        row2_layout.addWidget(QLabel("Categoria:"))
        self.category_combo = QComboBox()
        self._update_categories()  # Popola le categorie
        row2_layout.addWidget(self.category_combo)
        form_layout.addLayout(row2_layout)
        
        # Row 3: Km
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
        form_layout.addLayout(row3_layout)
        
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
        form_layout.addLayout(row4_layout)
        
        # Row 5: Previsioni calcolate
        row5_layout = QHBoxLayout()
        self.duration_label = QLabel("Durata prevista: --")
        self.duration_label.setStyleSheet("font-weight: bold; color: #4ade80;")
        row5_layout.addWidget(self.duration_label)
        
        self.kj_label = QLabel("KJ previsti: --")
        self.kj_label.setStyleSheet("font-weight: bold; color: #60a5fa;")
        row5_layout.addWidget(self.kj_label)
        form_layout.addLayout(row5_layout)
        
        # Row 6: Note e file percorso
        row6_layout = QHBoxLayout()
        row6_layout.addWidget(QLabel("Note:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        row6_layout.addWidget(self.notes_edit)
        
        row6_layout.addWidget(QLabel("Percorso:"))
        self.route_label = QLabel("Nessun file")
        self.route_label.setStyleSheet("color: #999;")
        route_btn = QPushButton("Seleziona GPX/FIT/TCX")
        route_btn.clicked.connect(self._select_route_file)
        route_col = QVBoxLayout()
        route_col.addWidget(self.route_label)
        route_col.addWidget(route_btn)
        row6_layout.addLayout(route_col)
        form_layout.addLayout(row6_layout)
        
        # Pulsante Crea gara
        create_btn = QPushButton("✓ Crea Gara")
        create_btn.setStyleSheet("background-color: #4ade80; color: black; font-weight: bold; padding: 8px;")
        create_btn.clicked.connect(self._create_race)
        form_layout.addWidget(create_btn)
        
        layout.addLayout(form_layout)
        
        # Divider
        layout.addWidget(QLabel("-" * 100))
        
        # ===== LISTA GARE =====
        races_label = QLabel("Gare Pianificate")
        races_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(races_label)
        
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
    
    def _update_predictions(self) -> None:
        """Aggiorna le previsioni di durata e KJ (usando media di tutti gli atleti)."""
        distance_km = self.distance_spin.value()
        speed_kmh = self.speed_spin.value()
        
        if speed_kmh <= 0:
            self.duration_label.setText("Durata prevista: --")
            self.kj_label.setText("KJ previsti: --")
            return
        
        # Calcola durata in minuti
        duration_minutes = (distance_km / speed_kmh) * 60
        hours = int(duration_minutes // 60)
        minutes = int(duration_minutes % 60)
        
        self.duration_label.setText(f"Durata prevista: {hours}h {minutes}m")
        
        # Calcola KJ previsti usando media di tutti gli atleti
        # KJ = kj_per_ora_per_kg * durata_ore * peso_atleta
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
    
    def _select_route_file(self) -> None:
        """Seleziona un file percorso GPX/FIT/TCX."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona file percorso",
            "",
            "Route Files (*.gpx *.fit *.tcx);;All Files (*)"
        )
        if file_path:
            self.selected_race_file = file_path
            filename = Path(file_path).name
            self.route_label.setText(filename)
    
    def _create_race(self) -> None:
        """Crea una nuova gara (standalone)."""
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
        
        # Calcola durata e KJ (usando media di tutti gli atleti)
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
        
        # Crea la gara nel database (standalone, senza athlete_id)
        try:
            race_id = self.storage.add_race(
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
            
            # Reset form
            self.name_edit.clear()
            self.date_edit.setDate(date.today())
            self.category_combo.setCurrentIndex(0)
            self.distance_spin.setValue(100)
            self.speed_spin.setValue(25)
            self.elevation_spin.setValue(500)
            self.notes_edit.clear()
            self.selected_race_file = None
            self.route_label.setText("Nessun file")
            
            # Ricarica tabella
            self._load_races()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore creazione gara: {str(e)}")
    
    def _load_races(self) -> None:
        """Carica tutte le gare (non filtrate per atleta)."""
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
    
    def _update_categories(self) -> None:
        """Aggiorna le categorie disponibili in base al genere selezionato"""
        gender = self.gender_combo.currentText()
        
        # Definisci le categorie per genere
        categories = {
            "Femminile": ["Allieve", "Junior", "Junior 1NC", "Junior 2NC", "Junior (OPEN)", "OPEN"],
            "Maschile": ["U23"]
        }
        
        # Popola il combo
        current_category = self.category_combo.currentText()
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItems(categories.get(gender, []))
        
        # Ripristina la selezione se possibile
        if current_category and current_category in categories.get(gender, []):
            idx = self.category_combo.findText(current_category)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
        
        self.category_combo.blockSignals(False)
    
    def _on_race_table_double_click(self, row: int, column: int) -> None:
        """Apre il dialog dettagli della gara al doppio clic su una cella."""
        # Non apre il dialog se si clicca sul bottone Elimina (colonna 9)
        if column == 9:
            return
        
        # Ottiene la race_id dalla prima cella della riga (Data)
        try:
            races = self.storage.list_races()
            if row < len(races):
                race_id = races[row].get("id")
                self._open_race_details(race_id)
        except Exception as e:
            print(f"[bTeam] Errore apertura dettagli gara: {e}")
    
    def _open_race_details(self, race_id: int) -> None:
        """Apre il dialog per modificare i dettagli della gara."""
        dialog = RaceDetailsDialog(self, self.storage, race_id)
        if dialog.exec():
            # Ricarica la tabella se le modifiche sono state salvate
            self._load_races()
    
    def _delete_race(self, race_id: int) -> None:
        """Elimina una gara dopo conferma."""
        confirm = QMessageBox.question(
            self,
            "Conferma eliminazione",
            "Sei sicuro di voler eliminare questa gara?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            if self.storage.delete_race(race_id):
                self._load_races()
                QMessageBox.information(self, "Eliminata", "Gara eliminata con successo!")
