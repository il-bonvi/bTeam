# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QDialogButtonBox,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
)

from intervals_sync import IntervalsSyncService


class IntervalsDialog(QDialog):
    """Dialog per importare attività da Intervals.icu"""
    
    def __init__(self, parent=None, athletes=None):
        super().__init__(parent)
        self.setWindowTitle("Importa Intervals.icu")
        athletes = athletes or []

        layout = QVBoxLayout(self)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)

        self.athlete_combo = QComboBox()
        for ath in athletes:
            full_name = f"{ath.get('last_name', '')} {ath.get('first_name', '')}".strip()
            self.athlete_combo.addItem(full_name, ath["id"])

        layout.addWidget(QLabel("API Key"))
        layout.addWidget(self.api_key_edit)
        layout.addWidget(QLabel("Atleta"))
        layout.addWidget(self.athlete_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return self.api_key_edit.text(), self.athlete_combo.currentData()


class SyncIntervalsDialog(QDialog):
    """Dialog per sincronizzare attività da Intervals.icu"""
    
    def __init__(self, parent=None, sync_service=None, storage=None):
        super().__init__(parent)
        self.setWindowTitle("Sincronizza Intervals.icu")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.sync_service = sync_service
        self.storage = storage

        layout = QVBoxLayout(self)

        # ===== API Key Section =====
        api_section = QGroupBox("Configurazione Intervals.icu")
        api_layout = QVBoxLayout(api_section)
        
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("API Key:"))
        self.api_key_edit = QLineEdit()
        if sync_service and sync_service.api_key:
            self.api_key_edit.setText(sync_service.api_key)
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        key_row.addWidget(self.api_key_edit, stretch=1)
        api_layout.addLayout(key_row)

        # Test connessione
        btn_test = QPushButton("Test connessione")
        btn_test.clicked.connect(self._test_connection)
        api_layout.addWidget(btn_test)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        api_layout.addWidget(self.status_label)
        
        if sync_service and sync_service.is_connected():
            self.status_label.setText("✅ Connesso a Intervals.icu")
            self.status_label.setStyleSheet("color: #22c55e; font-size: 11px;")

        layout.addWidget(api_section)

        # ===== Settings Section =====
        settings_section = QGroupBox("Impostazioni sincronizzazione")
        settings_layout = QVBoxLayout(settings_section)

        # Atleta
        settings_layout.addWidget(QLabel("Atleta di destinazione:"))
        self.athlete_combo = QComboBox()
        if storage:
            athletes = storage.list_athletes()
            for ath in athletes:
                full_name = f"{ath.get('last_name', '')} {ath.get('first_name', '')}".strip()
                self.athlete_combo.addItem(full_name, ath["id"])
        
        if self.athlete_combo.count() == 0:
            self.athlete_combo.addItem("-- Aggiungi un atleta prima --", None)
        settings_layout.addWidget(self.athlete_combo)

        # Giorni indietro
        settings_layout.addWidget(QLabel("Scarica attività degli ultimi X giorni:"))
        self.days_spin = QDoubleSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        self.days_spin.setDecimals(0)
        settings_layout.addWidget(self.days_spin)

        layout.addWidget(settings_section)

        # ===== Preview Section =====
        preview_section = QGroupBox("Anteprima attività da importare")
        preview_layout = QVBoxLayout(preview_section)
        
        btn_preview = QPushButton("Visualizza attività disponibili")
        btn_preview.clicked.connect(self._preview_activities)
        preview_layout.addWidget(btn_preview)

        self.activities_list = QTableWidget(0, 4)
        self.activities_list.setHorizontalHeaderLabels(["Data", "Nome", "Tipo", "Distanza (km)"])
        self.activities_list.setMaximumHeight(200)
        self.activities_list.horizontalHeader().setStretchLastSection(True)
        preview_layout.addWidget(self.activities_list)

        layout.addWidget(preview_section)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _test_connection(self):
        """Testa la connessione con Intervals.icu"""
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            self.status_label.setText("❌ Inserisci una API key")
            self.status_label.setStyleSheet("color: #ef4444; font-size: 11px;")
            return
        
        self.status_label.setText("🔄 Test in corso...")
        self.status_label.setStyleSheet("color: #f59e0b; font-size: 11px;")

        # Test della connessione
        test_service = IntervalsSyncService(api_key=api_key)
        if test_service.is_connected():
            self.status_label.setText("✅ Connesso a Intervals.icu")
            self.status_label.setStyleSheet("color: #22c55e; font-size: 11px;")
            # Aggiorna il servizio principale
            self.sync_service.set_api_key(api_key)
        else:
            self.status_label.setText("❌ Connessione fallita. Verifica la API key")
            self.status_label.setStyleSheet("color: #ef4444; font-size: 11px;")

    def _preview_activities(self):
        """Visualizza le attività disponibili"""
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            info = QDialog(self)
            info.setWindowTitle("API Key richiesta")
            layout = QVBoxLayout(info)
            layout.addWidget(QLabel("Inserisci una API key per visualizzare le attività"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(info.accept)
            layout.addWidget(buttons)
            info.exec()
            return

        # Aggiorna il servizio con la nuova key se cambiata
        if api_key != self.sync_service.api_key:
            self.sync_service.set_api_key(api_key)

        if not self.sync_service.is_connected():
            info = QDialog(self)
            info.setWindowTitle("Connessione fallita")
            layout = QVBoxLayout(info)
            layout.addWidget(QLabel("Impossibile connettersi a Intervals.icu. Verifica la API key"))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(info.accept)
            layout.addWidget(buttons)
            info.exec()
            return

        # Scarica le attività
        days_back = int(self.days_spin.value())
        activities, message = self.sync_service.fetch_activities(days_back=days_back, include_intervals=False)

        # Popola la tabella
        self.activities_list.setRowCount(len(activities))
        for row_idx, activity in enumerate(activities):
            date_str = activity.get('start_date_local', '')[:10]
            name = activity.get('name', '')
            type_ = activity.get('type', '')
            distance_km = (activity.get('distance', 0) or 0) / 1000

            self.activities_list.setItem(row_idx, 0, QTableWidgetItem(date_str))
            self.activities_list.setItem(row_idx, 1, QTableWidgetItem(name))
            self.activities_list.setItem(row_idx, 2, QTableWidgetItem(type_))
            self.activities_list.setItem(row_idx, 3, QTableWidgetItem(f"{distance_km:.1f}"))

        info = QDialog(self)
        info.setWindowTitle("Risultato")
        layout = QVBoxLayout(info)
        layout.addWidget(QLabel(f"{message}\n\nSeleziona 'OK' per importare tutte queste attività"))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(info.accept)
        layout.addWidget(buttons)
        info.exec()

    def get_api_key(self) -> str:
        return self.api_key_edit.text().strip()

    def get_selected_athlete(self) -> Optional[int]:
        return self.athlete_combo.currentData()

    def get_days_back(self) -> int:
        return int(self.days_spin.value())
