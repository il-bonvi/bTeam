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
)


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
