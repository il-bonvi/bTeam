# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget

def build_header(storage_dir) -> QVBoxLayout:
    """Costruisce la sezione header con titolo e cartella dati"""
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)

    header = QLabel("bTeam | Dashboard Squadra")
    header.setAlignment(Qt.AlignLeft)
    header.setStyleSheet("font-size: 22px; font-weight: 700;")
    layout.addWidget(header)

    return layout


def build_path_section(storage_dir, on_change_path_clicked) -> tuple[QHBoxLayout, QLabel]:
    """Costruisce la sezione percorso cartella dati"""
    path_layout = QHBoxLayout()
    
    path_label = QLabel(str(storage_dir))
    path_label.setStyleSheet("color: #e2e8f0; font-size: 12px;")
    
    btn_change_path = QPushButton("Imposta cartella dati")
    btn_change_path.clicked.connect(on_change_path_clicked)
    
    path_layout.addWidget(QLabel("Cartella dati:"))
    path_layout.addWidget(path_label, stretch=1)
    path_layout.addWidget(btn_change_path)
    
    return path_layout, path_label


def build_stats_section() -> tuple[QHBoxLayout, QLabel]:
    """Costruisce la sezione statistiche"""
    stats_layout = QHBoxLayout()
    stats_label = QLabel("")
    stats_layout.addWidget(stats_label)
    stats_layout.addStretch()
    
    return stats_layout, stats_label


def build_filter_section(on_team_changed, on_manage_teams, on_sync_intervals) -> tuple[QHBoxLayout, QComboBox]:
    """Costruisce la sezione filtri squadre"""
    filter_layout = QHBoxLayout()
    
    filter_layout.addWidget(QLabel("Filtra per squadra:"))
    
    filter_team_combo = QComboBox()
    filter_team_combo.addItem("Tutte", None)
    filter_team_combo.currentIndexChanged.connect(on_team_changed)
    filter_layout.addWidget(filter_team_combo)
    
    btn_manage_teams = QPushButton("Gestisci squadre")
    btn_manage_teams.clicked.connect(on_manage_teams)
    filter_layout.addWidget(btn_manage_teams)
    
    btn_sync_intervals = QPushButton("🔄 Sincronizza Intervals")
    btn_sync_intervals.clicked.connect(on_sync_intervals)
    filter_layout.addWidget(btn_sync_intervals)
    
    filter_layout.addStretch()
    
    return filter_layout, filter_team_combo


def build_action_buttons(
    on_add_team, on_add_athlete, on_delete_athlete, on_add_activity
) -> QHBoxLayout:
    """Costruisce la toolbar azioni principali"""
    action_layout = QHBoxLayout()
    
    btn_add_team = QPushButton("Aggiungi squadra")
    btn_add_team.clicked.connect(on_add_team)
    
    btn_add_athlete = QPushButton("Aggiungi atleta")
    btn_add_athlete.clicked.connect(on_add_athlete)
    
    btn_delete_athlete = QPushButton("🗑️ Elimina atleta")
    btn_delete_athlete.clicked.connect(on_delete_athlete)
    
    btn_add_activity = QPushButton("Aggiungi attività")
    btn_add_activity.clicked.connect(on_add_activity)
    
    action_layout.addWidget(btn_add_team)
    action_layout.addWidget(btn_add_athlete)
    action_layout.addWidget(btn_delete_athlete)
    action_layout.addWidget(btn_add_activity)
    action_layout.addStretch()
    
    return action_layout


def build_tools_toolbar(
    on_races, on_wellness, on_plan_week, on_export_import
) -> QHBoxLayout:
    """Costruisce la toolbar tools"""
    tools_layout = QHBoxLayout()
    
    btn_races = QPushButton("🏁 Race")
    btn_races.clicked.connect(on_races)
    
    btn_wellness = QPushButton("❤️ Tracking Benessere")
    btn_wellness.clicked.connect(on_wellness)
    
    btn_plan_week = QPushButton("📅 Pianifica Settimana")
    btn_plan_week.clicked.connect(on_plan_week)
    
    btn_export = QPushButton("💾 Export/Import")
    btn_export.clicked.connect(on_export_import)
    
    tools_layout.addWidget(btn_races)
    tools_layout.addWidget(btn_wellness)
    tools_layout.addWidget(btn_plan_week)
    tools_layout.addWidget(btn_export)
    tools_layout.addStretch()
    
    return tools_layout


def build_athletes_table() -> tuple[QTableWidget, None]:
    """Costruisce la tabella atleti"""
    athletes_table = QTableWidget(0, 4)
    athletes_table.setHorizontalHeaderLabels(["ID", "Rider", "Squadra", "Note"])
    athletes_table.horizontalHeader().setStretchLastSection(True)
    
    return athletes_table, None


def build_activities_table() -> QTableWidget:
    """Costruisce la tabella attività"""
    activities_table = QTableWidget(0, 8)
    activities_table.setHorizontalHeaderLabels(
        ["Atleta", "Data", "Titolo", "Durata (min)", "Distanza km", "Gara", "Tag", "Azioni"]
    )
    activities_table.horizontalHeader().setStretchLastSection(True)
    activities_table.horizontalHeader().setSortIndicatorShown(True)
    activities_table.setSortingEnabled(False)
    activities_table.setColumnWidth(7, 80)
    
    return activities_table
