# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QComboBox, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt
from storage_bteam import BTeamStorage


def build_riders_tab(storage: BTeamStorage, race_id: int, on_riders_changed) -> tuple[QWidget, dict]:
    """Costruisce il tab Riders della gara"""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # Header con bottone Add
    header_layout = QHBoxLayout()
    header_layout.addWidget(QLabel("🚴 Atleti partecipanti"))
    
    controls = {}
    
    add_rider_btn = QPushButton("+ Aggiungi Atleta")
    add_rider_btn.setMaximumWidth(150)
    add_rider_btn.clicked.connect(lambda: on_add_rider(storage, race_id, riders_table, controls))
    header_layout.addStretch()
    header_layout.addWidget(add_rider_btn)
    layout.addLayout(header_layout)
    
    # Tabella atleti
    riders_table = QTableWidget(0, 6)
    riders_table.setHorizontalHeaderLabels(["Nome", "Squadra", "kJ/h/kg", "Obbiettivo", "Note", "Azioni"])
    riders_table.setColumnWidth(0, 200)
    riders_table.setColumnWidth(1, 150)
    riders_table.setColumnWidth(2, 80)
    riders_table.setColumnWidth(3, 80)
    riders_table.setColumnWidth(4, 200)
    riders_table.setColumnWidth(5, 80)
    layout.addWidget(riders_table)
    controls['riders_table'] = riders_table
    
    # Riepilogo KJ
    summary_layout = QHBoxLayout()
    summary_layout.addWidget(QLabel("KJ totali stimati:"))
    riders_kj_total = QLineEdit()
    riders_kj_total.setReadOnly(True)
    riders_kj_total.setStyleSheet("background-color: #f0f0f0; color: #60a5fa; font-weight: bold;")
    riders_kj_total.setText("--")
    riders_kj_total.setMaximumWidth(150)
    summary_layout.addWidget(riders_kj_total)
    summary_layout.addStretch()
    layout.addLayout(summary_layout)
    controls['riders_kj_total'] = riders_kj_total
    
    # Carica atleti
    load_riders(storage, race_id, riders_table, riders_kj_total)
    
    return widget, controls


def load_riders(storage: BTeamStorage, race_id: int, riders_table: QTableWidget, riders_kj_total) -> None:
    """Carica gli atleti partecipanti"""
    race_athletes = storage.get_race_athletes(race_id)
    
    # Mappa athlete_id -> team_name
    all_athletes = storage.list_athletes()
    athlete_team_map = {}
    for athlete in all_athletes:
        athlete_team_map[athlete.get("id")] = athlete.get("team_name", "")
    
    riders_table.setRowCount(len(race_athletes))
    for row_idx, ra in enumerate(race_athletes):
        athlete_id = ra.get("athlete_id")
        athlete_name = ra.get("athlete_name", "")
        kj_per_hour_per_kg = ra.get("kj_per_hour_per_kg", 10.0)
        objective = ra.get("objective", "C")
        
        riders_table.setItem(row_idx, 0, QTableWidgetItem(athlete_name))
        team_name = athlete_team_map.get(athlete_id, "")
        riders_table.setItem(row_idx, 1, QTableWidgetItem(team_name))
        riders_table.setItem(row_idx, 2, QTableWidgetItem(f"{kj_per_hour_per_kg:.2f}"))
        riders_table.setItem(row_idx, 3, QTableWidgetItem(objective))
        riders_table.setItem(row_idx, 4, QTableWidgetItem(""))
        
        delete_btn = QPushButton("Elimina")
        delete_btn.setMaximumWidth(80)
        delete_btn.clicked.connect(lambda checked, aid=athlete_id: on_remove_rider(storage, race_id, aid, riders_table, riders_kj_total))
        riders_table.setCellWidget(row_idx, 5, delete_btn)
    
    update_riders_kj_total(riders_table, riders_kj_total)


def on_add_rider(storage: BTeamStorage, race_id: int, riders_table: QTableWidget, controls) -> None:
    """Aggiunge atleti alla gara"""
    athletes = storage.list_athletes()
    
    if not athletes:
        QMessageBox.warning(None, "Nessun atleta", "Non ci sono atleti disponibili. Creane uno prima.")
        return
    
    dialog = QDialog()
    dialog.setWindowTitle("Aggiungi Atleti")
    dialog.setMinimumSize(500, 400)
    
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("Seleziona gli atleti da aggiungere:"))
    
    # Tabella con checkbox
    table = QTableWidget()
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels(["✓", "Nome", "Squadra"])
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.MultiSelection)
    table.setColumnWidth(0, 40)
    table.setColumnWidth(1, 200)
    table.setColumnWidth(2, 200)
    table.horizontalHeader().setStretchLastSection(True)
    
    table.setRowCount(len(athletes))
    for row_idx, athlete in enumerate(athletes):
        checkbox = QTableWidgetItem()
        checkbox.setFlags(checkbox.flags() | Qt.ItemIsUserCheckable)
        checkbox.setCheckState(Qt.Unchecked)
        table.setItem(row_idx, 0, checkbox)
        
        name_item = QTableWidgetItem(f"{athlete.get('last_name')} {athlete.get('first_name')}")
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        table.setItem(row_idx, 1, name_item)
        
        team_item = QTableWidgetItem(athlete.get("team_name", ""))
        team_item.setFlags(team_item.flags() & ~Qt.ItemIsEditable)
        table.setItem(row_idx, 2, team_item)
        
        table.item(row_idx, 0).athlete_id = athlete.get("id")
    
    layout.addWidget(table)
    
    layout.addWidget(QLabel("Obbiettivo (A/B/C):"))
    objective_combo = QComboBox()
    objective_combo.addItems(["A", "B", "C"])
    objective_combo.setCurrentText("C")
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
        selected_athletes = []
        for row_idx in range(table.rowCount()):
            checkbox = table.item(row_idx, 0)
            if checkbox.checkState() == Qt.Checked:
                selected_athletes.append(checkbox.athlete_id)
        
        if not selected_athletes:
            QMessageBox.warning(dialog, "Nessuna selezione", "Seleziona almeno un atleta")
            return
        
        objective = objective_combo.currentText()
        
        added_count = 0
        for athlete_id in selected_athletes:
            if storage.add_athlete_to_race(race_id, athlete_id, objective=objective, kj_per_hour_per_kg=10.0):
                added_count += 1
        
        if added_count > 0:
            QMessageBox.information(dialog, "Aggiunto", f"{added_count} atleta/i aggiunto/i alla gara!")
            dialog.accept()
            load_riders(storage, race_id, riders_table, controls['riders_kj_total'])
        else:
            QMessageBox.warning(dialog, "Errore", "Gli atleti selezionati sono già nella gara")
    
    add_btn.clicked.connect(add_clicked)
    cancel_btn.clicked.connect(dialog.reject)
    
    dialog.exec()


def on_remove_rider(storage: BTeamStorage, race_id: int, athlete_id: int, 
                    riders_table: QTableWidget, riders_kj_total) -> None:
    """Rimuove un atleta dalla gara"""
    confirm = QMessageBox.question(
        None,
        "Conferma rimozione",
        "Sei sicuro di voler rimuovere questo atleta dalla gara?",
        QMessageBox.Yes | QMessageBox.No
    )
    if confirm == QMessageBox.Yes:
        if storage.remove_athlete_from_race(race_id, athlete_id):
            load_riders(storage, race_id, riders_table, riders_kj_total)
            QMessageBox.information(None, "Rimosso", "Atleta rimosso dalla gara!")


def update_riders_kj_total(riders_table: QTableWidget, riders_kj_total) -> None:
    """Aggiorna il totale KJ in base ai valori kJ/h/kg presenti in tabella."""
    total_kj_per_h_per_kg = 0.0
    for row_idx in range(riders_table.rowCount()):
        item = riders_table.item(row_idx, 2)  # colonna "kJ/h/kg"
        if item is None:
            continue
        text = item.text().strip()
        if not text:
            continue
        try:
            value = float(text.replace(",", "."))
        except ValueError:
            continue
        total_kj_per_h_per_kg += value

    if total_kj_per_h_per_kg > 0:
        riders_kj_total.setText(f"{total_kj_per_h_per_kg:.1f}")
    else:
        riders_kj_total.setText("--")
