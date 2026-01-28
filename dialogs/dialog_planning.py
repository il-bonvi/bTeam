# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QCheckBox,
    QDialogButtonBox,
    QTabWidget,
    QWidget,
    QPushButton,
    QFileDialog,
)


class PlanWeekDialog(QDialog):
    """Dialog per pianificare una settimana di allenamenti"""
    
    def __init__(self, parent=None, sync_service=None):
        super().__init__(parent)
        self.setWindowTitle("Pianifica Settimana di Allenamenti")
        self.setMinimumWidth(600)
        self.sync_service = sync_service
        
        layout = QVBoxLayout(self)
        
        # Data inizio (lunedì)
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Lunedì della settimana:"))
        self.start_date = QDateEdit()
        today = datetime.now().date()
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
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona file da importare",
            str(Path.home()),
            "CSV (*.csv);;JSON (*.json);;Tutti (*.*)"
        )
        if file_path:
            self.import_file_label.setText(file_path)
    
    def _do_export(self):
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
