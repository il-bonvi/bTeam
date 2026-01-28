# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QDialogButtonBox,
    QMessageBox,
    QDateEdit,
    QPushButton,
)
from PySide6.QtCore import Qt, QDate
from datetime import date as date_module


class WellnessDialog(QDialog):
    """Dialog per loggare dati wellness (peso, FC riposo, HRV)"""
    
    def __init__(self, parent=None, sync_service=None):
        super().__init__(parent)
        self.setWindowTitle("Tracking Benessere")
        self.setMinimumWidth(500)
        self.sync_service = sync_service
        
        layout = QVBoxLayout(self)
        
        # Seleziona data
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Data:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(date_module.today())
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
