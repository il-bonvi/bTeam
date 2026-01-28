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
    QTextEdit,
)


class SimpleActivityDialog(QDialog):
    """Dialog per aggiungere una nuova attività"""
    
    def __init__(self, parent=None, athletes=None):
        super().__init__(parent)
        self.setWindowTitle("Nuova attività")
        athletes = athletes or []

        layout = QVBoxLayout(self)

        self.athlete_combo = QComboBox()
        for ath in athletes:
            full_name = f"{ath.get('last_name', '')} {ath.get('first_name', '')}".strip()
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


class ActivityDetailsDialog(QDialog):
    """Dialog per visualizzare i dettagli di un'attività"""
    
    def __init__(self, parent=None, activity=None):
        super().__init__(parent)
        self.setWindowTitle("Dettagli Attività")
        self.setMinimumWidth(500)
        
        activity = activity or {}
        layout = QVBoxLayout(self)
        
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
        from PySide6.QtWidgets import QGridLayout
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
        
        # Pulsante chiusura
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
    
    @staticmethod
    def _fmt_num(value: Optional[float]) -> str:
        return "" if value is None else f"{value:.1f}"
