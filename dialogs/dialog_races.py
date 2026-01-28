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
    QTabWidget,
    QWidget,
)

from storage_bteam import BTeamStorage


class RaceDetailsDialog(QDialog):
    """Dialog per modificare i dettagli di una gara."""
    
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
        """Carica i dati della gara dal database."""
        self.race_data = self.storage.get_race(self.race_id)
    
    def _build_ui(self) -> None:
        """Costruisce l'interfaccia del dialog con tab."""
        if not self.race_data:
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Gara non trovata"))
            return
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Tab 1: Dettagli
        tabs.addTab(self._build_details_tab(), "📋 Dettagli")
        
        # Tab 2: Riders
        tabs.addTab(self._build_riders_tab(), "🚴 Riders")
        
        # Tab 3: Metrics
        tabs.addTab(self._build_metrics_tab(), "📊 Metrics")
        
        layout.addWidget(tabs)
        
        # Bottoni di salvataggio/annullamento
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
    
    def _build_details_tab(self) -> QWidget:
        """Costruisce il tab Dettagli."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
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
        gender_layout.addWidget(self.gender_combo)
        
        gender_layout.addWidget(QLabel("Categoria:"))
        self.category_combo = QComboBox()
        self._update_categories()
        saved_category = self.race_data.get("category", "")
        if saved_category:
            idx = self.category_combo.findText(saved_category)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
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
        return widget
    
    def _build_riders_tab(self) -> QWidget:
        """Costruisce il tab Riders."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header con bottone Add
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🚴 Atleti partecipanti"))
        
        add_rider_btn = QPushButton("+ Aggiungi Atleta")
        add_rider_btn.setMaximumWidth(150)
        add_rider_btn.clicked.connect(self._on_add_rider)
        header_layout.addStretch()
        header_layout.addWidget(add_rider_btn)
        layout.addLayout(header_layout)
        
        # Tabella atleti con colonne: Nome, Squadra, kJ/h/kg, Obbiettivo, Note, Azioni
        self.riders_table = QTableWidget(0, 6)
        self.riders_table.setHorizontalHeaderLabels(["Nome", "Squadra", "kJ/h/kg", "Obbiettivo", "Note", "Azioni"])
        self.riders_table.setColumnWidth(0, 200)
        self.riders_table.setColumnWidth(1, 150)
        self.riders_table.setColumnWidth(2, 80)
        self.riders_table.setColumnWidth(3, 80)
        self.riders_table.setColumnWidth(4, 200)
        self.riders_table.setColumnWidth(5, 80)
        layout.addWidget(self.riders_table)
        
        # Riepilogo KJ
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(QLabel("KJ totali stimati:"))
        self.riders_kj_total = QLineEdit()
        self.riders_kj_total.setReadOnly(True)
        self.riders_kj_total.setStyleSheet("background-color: #f0f0f0; color: #60a5fa; font-weight: bold;")
        self.riders_kj_total.setText("--")
        self.riders_kj_total.setMaximumWidth(150)
        summary_layout.addWidget(self.riders_kj_total)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)
        
        # Carica gli atleti
        self._load_riders()
        
        return widget
    
    def _load_riders(self) -> None:
        """Carica gli atleti partecipanti alla gara."""
        race_athletes = self.storage.get_race_athletes(self.race_id)
        
        # Build a map of athlete_id -> team_name for quick lookup
        all_athletes = self.storage.list_athletes()
        athlete_team_map = {}
        for athlete in all_athletes:
            athlete_team_map[athlete.get("id")] = athlete.get("team_name", "")
        
        self.riders_table.setRowCount(len(race_athletes))
        for row_idx, ra in enumerate(race_athletes):
            athlete_id = ra.get("athlete_id")
            athlete_name = ra.get("athlete_name", "")
            kj_per_hour_per_kg = ra.get("kj_per_hour_per_kg", 10.0)
            objective = ra.get("objective", "C")
            
            # Nome atleta
            self.riders_table.setItem(row_idx, 0, QTableWidgetItem(athlete_name))
            
            # Squadra (da mappa athlete_id -> team_name)
            team_name = athlete_team_map.get(athlete_id, "")
            self.riders_table.setItem(row_idx, 1, QTableWidgetItem(team_name))
            
            # kJ/h/kg
            self.riders_table.setItem(row_idx, 2, QTableWidgetItem(f"{kj_per_hour_per_kg:.2f}"))
            
            # Obbiettivo
            self.riders_table.setItem(row_idx, 3, QTableWidgetItem(objective))
            
            # Note (placeholder)
            self.riders_table.setItem(row_idx, 4, QTableWidgetItem(""))
            
            # Bottone elimina
            delete_btn = QPushButton("Elimina")
            delete_btn.setMaximumWidth(80)
            delete_btn.clicked.connect(lambda checked, aid=athlete_id: self._on_remove_rider(aid))
            self.riders_table.setCellWidget(row_idx, 5, delete_btn)
        
        # Aggiorna KJ totali
        self._update_riders_kj_total()
    
    def _on_add_rider(self) -> None:
        """Aggiunge atleti alla gara (selezione multipla)."""
        # Leggi lista atleti disponibili
        athletes = self.storage.list_athletes()
        
        if not athletes:
            QMessageBox.warning(self, "Nessun atleta", "Non ci sono atleti disponibili. Creane uno prima.")
            return
        
        # Dialogo per selezionare atleti (multipla)
        dialog = QDialog(self)
        dialog.setWindowTitle("Aggiungi Atleti")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Seleziona gli atleti da aggiungere (puoi sceglierne più di uno):"))
        
        # Tabella con atleti
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["✓", "Nome", "Squadra"])
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.MultiSelection)
        table.setColumnWidth(0, 40)
        table.setColumnWidth(1, 200)
        table.setColumnWidth(2, 200)
        table.horizontalHeader().setStretchLastSection(True)
        
        # Popola tabella
        table.setRowCount(len(athletes))
        for row_idx, athlete in enumerate(athletes):
            # Checkbox (colonna 0)
            checkbox = QTableWidgetItem()
            checkbox.setFlags(checkbox.flags() | Qt.ItemIsUserCheckable)
            checkbox.setCheckState(Qt.Unchecked)
            table.setItem(row_idx, 0, checkbox)
            
            # Nome atleta (colonna 1)
            name_item = QTableWidgetItem(f"{athlete.get('last_name')} {athlete.get('first_name')}")
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 1, name_item)
            
            # Squadra (colonna 2)
            team_name = athlete.get("team_name", "")
            team_item = QTableWidgetItem(team_name)
            team_item.setFlags(team_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, 2, team_item)
            
            # Salva athlete_id come dato nascosto
            table.item(row_idx, 0).athlete_id = athlete.get("id")
        
        layout.addWidget(table)
        
        layout.addWidget(QLabel("Obbiettivo (A/B/C):"))
        objective_combo = QComboBox()
        objective_combo.addItems(["A", "B", "C"])
        objective_combo.setCurrentText("C")  # Default C
        layout.addWidget(objective_combo)
        
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("✓ Aggiungi Selezionati")
        add_btn.setStyleSheet("background-color: #4ade80; color: black; font-weight: bold;")
        cancel_btn = QPushButton("Annulla")
        buttons_layout.addStretch()
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        def add_clicked():
            # Raccogli tutti gli atleti selezionati (checkbox checked)
            selected_athletes = []
            for row_idx in range(table.rowCount()):
                checkbox = table.item(row_idx, 0)
                if checkbox.checkState() == Qt.Checked:
                    selected_athletes.append(checkbox.athlete_id)
            
            if not selected_athletes:
                QMessageBox.warning(dialog, "Nessuna selezione", "Seleziona almeno un atleta")
                return
            
            # Prendi l'obiettivo selezionato
            objective = objective_combo.currentText()
            
            # Aggiungi tutti gli atleti selezionati con obiettivo e kJ/h/kg = 10
            added_count = 0
            for athlete_id in selected_athletes:
                if self.storage.add_athlete_to_race(self.race_id, athlete_id, objective=objective, kj_per_hour_per_kg=10.0):
                    added_count += 1
            
            if added_count > 0:
                QMessageBox.information(dialog, "Aggiunto", f"{added_count} atleta/i aggiunto/i alla gara!")
                dialog.accept()
                self._load_riders()
            else:
                QMessageBox.warning(dialog, "Errore", "Gli atleti selezionati sono già nella gara")
        
        add_btn.clicked.connect(add_clicked)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def _on_remove_rider(self, athlete_id: int) -> None:
        """Rimuove un atleta dalla gara."""
        confirm = QMessageBox.question(
            self,
            "Conferma rimozione",
            "Sei sicuro di voler rimuovere questo atleta dalla gara?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            if self.storage.remove_athlete_from_race(self.race_id, athlete_id):
                self._load_riders()
                QMessageBox.information(self, "Rimosso", "Atleta rimosso dalla gara!")
    
    def _update_riders_kj_total(self) -> None:
        """Aggiorna il totale KJ dalla durata della gara."""
        if hasattr(self, 'duration_edit'):
            duration_text = self.duration_edit.text()
            if duration_text != "--":
                # Estrai ore da formato "Xh Ym"
                try:
                    parts = duration_text.split('h')
                    hours = int(parts[0])
                    minutes = int(parts[1].strip().rstrip('m')) if len(parts) > 1 else 0
                    duration_hours = hours + minutes / 60
                    
                    athletes = self.storage.list_athletes()
                    if athletes:
                        total_kj = 0
                        for athlete in athletes:
                            weight_kg = athlete.get("weight_kg", 70) or 70
                            kj_per_hora_per_kg = athlete.get("kj_per_hour_per_kg", 1.0) or 1.0
                            total_kj += kj_per_hora_per_kg * duration_hours * weight_kg
                        
                        avg_kj = total_kj / len(athletes)
                        self.riders_kj_total.setText(f"{avg_kj:.0f}")
                    else:
                        self.riders_kj_total.setText("--")
                except:
                    self.riders_kj_total.setText("--")
            else:
                self.riders_kj_total.setText("--")
    
    def _build_metrics_tab(self) -> QWidget:
        """Costruisce il tab Metrics."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Sezione Traccia
        layout.addWidget(QLabel("📊 Traccia Gara"))
        
        trace_layout = QHBoxLayout()
        trace_layout.addWidget(QLabel("File:"))
        self.trace_file_label = QLineEdit()
        self.trace_file_label.setReadOnly(True)
        self.trace_file_label.setPlaceholderText("Nessun file importato")
        trace_layout.addWidget(self.trace_file_label)
        
        import_trace_btn = QPushButton("Importa GPX/FIT/TCX")
        import_trace_btn.setMaximumWidth(150)
        import_trace_btn.clicked.connect(self._on_import_trace)
        trace_layout.addWidget(import_trace_btn)
        layout.addLayout(trace_layout)
        
        layout.addWidget(QLabel("-" * 50))
        
        # Sezione TV (Traguardi Volanti)
        layout.addWidget(QLabel("🎯 Traguardi Volanti (TV)"))
        
        tv_layout = QHBoxLayout()
        tv_layout.addWidget(QLabel("Aggiungi TV:"))
        tv_layout.addWidget(QLabel("km:"))
        self.tv_km_spin = QDoubleSpinBox()
        self.tv_km_spin.setMinimum(0)
        self.tv_km_spin.setMaximum(500)
        self.tv_km_spin.setDecimals(1)
        self.tv_km_spin.setValue(0)
        tv_layout.addWidget(self.tv_km_spin)
        
        add_tv_btn = QPushButton("Aggiungi TV")
        add_tv_btn.setMaximumWidth(100)
        add_tv_btn.clicked.connect(self._on_add_tv)
        tv_layout.addWidget(add_tv_btn)
        tv_layout.addStretch()
        layout.addLayout(tv_layout)
        
        # Tabella TV
        self.tv_table = QTableWidget(0, 2)
        self.tv_table.setHorizontalHeaderLabels(["km", "Elimina"])
        self.tv_table.setColumnWidth(0, 100)
        self.tv_table.setColumnWidth(1, 80)
        layout.addWidget(self.tv_table)
        
        layout.addWidget(QLabel("-" * 50))
        
        # Sezione GPM (Gran Premi di Montagna)
        layout.addWidget(QLabel("⛰️ Gran Premi di Montagna (GPM)"))
        
        gpm_layout = QHBoxLayout()
        gpm_layout.addWidget(QLabel("Aggiungi GPM:"))
        gpm_layout.addWidget(QLabel("km:"))
        self.gpm_km_spin = QDoubleSpinBox()
        self.gpm_km_spin.setMinimum(0)
        self.gpm_km_spin.setMaximum(500)
        self.gpm_km_spin.setDecimals(1)
        self.gpm_km_spin.setValue(0)
        gpm_layout.addWidget(self.gpm_km_spin)
        
        add_gpm_btn = QPushButton("Aggiungi GPM")
        add_gpm_btn.setMaximumWidth(100)
        add_gpm_btn.clicked.connect(self._on_add_gpm)
        gpm_layout.addWidget(add_gpm_btn)
        gpm_layout.addStretch()
        layout.addLayout(gpm_layout)
        
        # Tabella GPM
        self.gpm_table = QTableWidget(0, 2)
        self.gpm_table.setHorizontalHeaderLabels(["km", "Elimina"])
        self.gpm_table.setColumnWidth(0, 100)
        self.gpm_table.setColumnWidth(1, 80)
        layout.addWidget(self.gpm_table)
        
        layout.addStretch()
        
        return widget
    
    def _on_import_trace(self) -> None:
        """Importa il file traccia GPX/FIT/TCX."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona file traccia",
            "",
            "Trace Files (*.gpx *.fit *.tcx);;All Files (*)"
        )
        if file_path:
            self.trace_file_path = file_path
            filename = Path(file_path).name
            self.trace_file_label.setText(filename)
    
    def _on_add_tv(self) -> None:
        """Aggiunge un traguardo volante."""
        km = self.tv_km_spin.value()
        row = self.tv_table.rowCount()
        self.tv_table.insertRow(row)
        self.tv_table.setItem(row, 0, QTableWidgetItem(f"{km:.1f}"))
        
        delete_btn = QPushButton("Elimina")
        delete_btn.setMaximumWidth(80)
        delete_btn.clicked.connect(lambda: self._delete_tv_row(row))
        self.tv_table.setCellWidget(row, 1, delete_btn)
        
        self.tv_km_spin.setValue(0)
    
    def _delete_tv_row(self, row: int) -> None:
        """Elimina una riga dalla tabella TV."""
        self.tv_table.removeRow(row)
    
    def _on_add_gpm(self) -> None:
        """Aggiunge un gran premio di montagna."""
        km = self.gpm_km_spin.value()
        row = self.gpm_table.rowCount()
        self.gpm_table.insertRow(row)
        self.gpm_table.setItem(row, 0, QTableWidgetItem(f"{km:.1f}"))
        
        delete_btn = QPushButton("Elimina")
        delete_btn.setMaximumWidth(80)
        delete_btn.clicked.connect(lambda: self._delete_gpm_row(row))
        self.gpm_table.setCellWidget(row, 1, delete_btn)
        
        self.gpm_km_spin.setValue(0)
    
    def _delete_gpm_row(self, row: int) -> None:
        """Elimina una riga dalla tabella GPM."""
        self.gpm_table.removeRow(row)
    
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
        try:
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
        except Exception as e:
            print(f"[bTeam] Errore salvataggio gara: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Errore", f"Errore nel salvataggio: {str(e)}")


class RaceCreateDialog(QDialog):
    """Dialog per creare una nuova gara."""
    
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
        
        # Row 5: Previsioni calcolate
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
    
    def _update_predictions(self) -> None:
        """Aggiorna le previsioni di durata e KJ."""
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
    
    def _create_race(self) -> None:
        """Crea una nuova gara."""
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
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore creazione gara: {str(e)}")


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
        """Apre il dialog per creare una nuova gara."""
        dialog = RaceCreateDialog(self, self.storage)
        if dialog.exec():
            # Ricarica la tabella se una gara è stata creata
            self._load_races()
    
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
        try:
            dialog = RaceDetailsDialog(self, self.storage, race_id)
            if dialog.exec():
                # Ricarica la tabella se le modifiche sono state salvate
                self._load_races()
        except Exception as e:
            print(f"[bTeam] Errore apertura dettagli gara: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Errore", f"Errore apertura gara: {str(e)}")
    
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
