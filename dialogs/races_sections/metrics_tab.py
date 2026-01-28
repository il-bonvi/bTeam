# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog
)


def build_metrics_tab() -> tuple[QWidget, dict]:
    """Costruisce il tab Metrics della gara"""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    controls = {}
    
    # ===== Sezione Traccia =====
    layout.addWidget(QLabel("📊 Traccia Gara"))
    
    trace_layout = QHBoxLayout()
    trace_layout.addWidget(QLabel("File:"))
    
    from PySide6.QtWidgets import QLineEdit
    trace_file_label = QLineEdit()
    trace_file_label.setReadOnly(True)
    trace_file_label.setPlaceholderText("Nessun file importato")
    trace_layout.addWidget(trace_file_label)
    controls['trace_file_label'] = trace_file_label
    
    import_trace_btn = QPushButton("Importa GPX/FIT/TCX")
    import_trace_btn.setMaximumWidth(150)
    import_trace_btn.clicked.connect(lambda: on_import_trace(trace_file_label))
    trace_layout.addWidget(import_trace_btn)
    layout.addLayout(trace_layout)
    
    layout.addWidget(QLabel("-" * 50))
    
    # ===== Sezione TV (Traguardi Volanti) =====
    layout.addWidget(QLabel("🎯 Traguardi Volanti (TV)"))
    
    tv_layout = QHBoxLayout()
    tv_layout.addWidget(QLabel("Aggiungi TV:"))
    tv_layout.addWidget(QLabel("km:"))
    tv_km_spin = QDoubleSpinBox()
    tv_km_spin.setMinimum(0)
    tv_km_spin.setMaximum(500)
    tv_km_spin.setDecimals(1)
    tv_km_spin.setValue(0)
    tv_layout.addWidget(tv_km_spin)
    controls['tv_km_spin'] = tv_km_spin
    
    add_tv_btn = QPushButton("Aggiungi TV")
    add_tv_btn.setMaximumWidth(100)
    
    tv_table = QTableWidget(0, 2)
    tv_table.setHorizontalHeaderLabels(["km", "Elimina"])
    tv_table.setColumnWidth(0, 100)
    tv_table.setColumnWidth(1, 80)
    controls['tv_table'] = tv_table
    
    add_tv_btn.clicked.connect(lambda: on_add_tv(tv_km_spin, tv_table))
    tv_layout.addWidget(add_tv_btn)
    tv_layout.addStretch()
    layout.addLayout(tv_layout)
    layout.addWidget(tv_table)
    
    layout.addWidget(QLabel("-" * 50))
    
    # ===== Sezione GPM (Gran Premi di Montagna) =====
    layout.addWidget(QLabel("⛰️ Gran Premi di Montagna (GPM)"))
    
    gpm_layout = QHBoxLayout()
    gpm_layout.addWidget(QLabel("Aggiungi GPM:"))
    gpm_layout.addWidget(QLabel("km:"))
    gpm_km_spin = QDoubleSpinBox()
    gpm_km_spin.setMinimum(0)
    gpm_km_spin.setMaximum(500)
    gpm_km_spin.setDecimals(1)
    gpm_km_spin.setValue(0)
    gpm_layout.addWidget(gpm_km_spin)
    controls['gpm_km_spin'] = gpm_km_spin
    
    add_gpm_btn = QPushButton("Aggiungi GPM")
    add_gpm_btn.setMaximumWidth(100)
    
    gpm_table = QTableWidget(0, 2)
    gpm_table.setHorizontalHeaderLabels(["km", "Elimina"])
    gpm_table.setColumnWidth(0, 100)
    gpm_table.setColumnWidth(1, 80)
    controls['gpm_table'] = gpm_table
    
    add_gpm_btn.clicked.connect(lambda: on_add_gpm(gpm_km_spin, gpm_table))
    gpm_layout.addWidget(add_gpm_btn)
    gpm_layout.addStretch()
    layout.addLayout(gpm_layout)
    layout.addWidget(gpm_table)
    
    layout.addStretch()
    
    return widget, controls


def on_import_trace(trace_file_label) -> Optional[str]:
    """Importa il file traccia GPX/FIT/TCX"""
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Seleziona file traccia",
        "",
        "Trace Files (*.gpx *.fit *.tcx);;All Files (*)"
    )
    if file_path:
        filename = Path(file_path).name
        trace_file_label.setText(filename)
        return file_path
    return None


def on_add_tv(tv_km_spin: QDoubleSpinBox, tv_table: QTableWidget) -> None:
    """Aggiunge un traguardo volante"""
    km = tv_km_spin.value()
    row = tv_table.rowCount()
    tv_table.insertRow(row)
    tv_table.setItem(row, 0, QTableWidgetItem(f"{km:.1f}"))
    
    delete_btn = QPushButton("Elimina")
    delete_btn.setMaximumWidth(80)
    delete_btn.clicked.connect(lambda: delete_tv_row(delete_btn, tv_table))
    tv_table.setCellWidget(row, 1, delete_btn)
    
    tv_km_spin.setValue(0)


def delete_tv_row(button: QPushButton, tv_table: QTableWidget) -> None:
    """Elimina una riga dalla tabella TV"""
    # Trova la riga corrente dal pulsante
    for row in range(tv_table.rowCount()):
        if tv_table.cellWidget(row, 1) == button:
            tv_table.removeRow(row)
            break


def on_add_gpm(gpm_km_spin: QDoubleSpinBox, gpm_table: QTableWidget) -> None:
    """Aggiunge un gran premio di montagna"""
    km = gpm_km_spin.value()
    row = gpm_table.rowCount()
    gpm_table.insertRow(row)
    gpm_table.setItem(row, 0, QTableWidgetItem(f"{km:.1f}"))
    
    delete_btn = QPushButton("Elimina")
    delete_btn.setMaximumWidth(80)
    delete_btn.clicked.connect(lambda: delete_gpm_row(delete_btn, gpm_table))
    gpm_table.setCellWidget(row, 1, delete_btn)
    
    gpm_km_spin.setValue(0)


def delete_gpm_row(button: QPushButton, gpm_table: QTableWidget) -> None:
    """Elimina una riga dalla tabella GPM"""
    # Trova la riga corrente dal pulsante
    for row in range(gpm_table.rowCount()):
        if gpm_table.cellWidget(row, 1) == button:
            gpm_table.removeRow(row)
            break
