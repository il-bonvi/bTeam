# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QTableWidgetItem, QPushButton, QComboBox, QHBoxLayout, QLabel
)


def refresh_athletes_table(storage, athletes_table, athletes_data) -> list:
    """Popola la tabella atleti"""
    athletes = athletes_data
    print(f"[bTeam] Atleti caricati: {len(athletes)}")
    athletes_table.setRowCount(len(athletes))
    
    for row_idx, athlete in enumerate(athletes):
        athletes_table.setItem(row_idx, 0, QTableWidgetItem(str(athlete["id"])))
        rider_name = f"{athlete.get('last_name', '')} {athlete.get('first_name', '')}"
        athletes_table.setItem(row_idx, 1, QTableWidgetItem(rider_name))
        athletes_table.setItem(row_idx, 2, QTableWidgetItem(athlete.get("team_name", "")))
        athletes_table.setItem(row_idx, 3, QTableWidgetItem(athlete.get("notes", "")))
    
    return athletes


def refresh_activities_table(
    storage,
    activities_table,
    all_activities,
    current_sort_column,
    current_sort_order,
    on_delete_clicked
) -> None:
    """Popola la tabella attività con ordinamento personalizzato"""
    
    def get_sort_key(activity):
        if current_sort_column == 0:  # Atleta
            return activity.get("athlete_name", "").lower()
        elif current_sort_column == 1:  # Data
            return activity.get("activity_date", "")[:10]
        elif current_sort_column == 2:  # Titolo
            return activity.get("title", "").lower()
        elif current_sort_column == 3:  # Durata
            return activity.get("duration_minutes") or 0
        elif current_sort_column == 4:  # Distanza
            return activity.get("distance_km") or 0
        return ""
    
    reverse = (current_sort_order == Qt.DescendingOrder)
    try:
        activities = sorted(all_activities, key=get_sort_key, reverse=reverse)
    except Exception as e:
        print(f"[bTeam] Errore ordinamento: {e}")
        activities = all_activities
    
    activities_table.setRowCount(len(activities))
    for row_idx, activity in enumerate(activities):
        activity_id = activity["id"]
        activities_table.setItem(row_idx, 0, QTableWidgetItem(activity.get("athlete_name", "")))
        
        # Formatta data
        activity_date = activity.get("activity_date", "")
        formatted_date = format_date(activity_date)
        activities_table.setItem(row_idx, 1, QTableWidgetItem(formatted_date))
        
        activities_table.setItem(row_idx, 2, QTableWidgetItem(activity.get("title", "")))
        activities_table.setItem(row_idx, 3, QTableWidgetItem(fmt_duration(activity.get("duration_minutes"))))
        activities_table.setItem(row_idx, 4, QTableWidgetItem(fmt_num(activity.get("distance_km"))))
        
        # Colonna 5: Is Race
        is_race = activity.get("is_race", False)
        race_text = "✓ Gara" if is_race else ""
        race_item = QTableWidgetItem(race_text)
        if is_race:
            race_item.setBackground(Qt.yellow)
        activities_table.setItem(row_idx, 5, race_item)
        
        # Colonna 6: Tags
        tags = activity.get("tags", [])
        tags_str = ", ".join(tags) if tags else ""
        activities_table.setItem(row_idx, 6, QTableWidgetItem(tags_str))
        
        # Colonna 7: Delete button
        delete_btn = QPushButton("Elimina")
        delete_btn.setMaximumWidth(70)
        delete_btn.clicked.connect(lambda checked, aid=activity_id: on_delete_clicked(aid))
        activities_table.setCellWidget(row_idx, 7, delete_btn)


def format_date(activity_date: str) -> str:
    """Formatta data ISO a formato IT"""
    if not activity_date:
        return ""
    
    try:
        if "T" in activity_date:
            date_obj = datetime.fromisoformat(activity_date.replace("Z", "+00:00"))
            return date_obj.strftime("%d/%m/%Y")
        elif len(activity_date) == 10:
            date_obj = datetime.strptime(activity_date, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
    except Exception as e:
        print(f"[bTeam] Errore formattazione data: {e}")
    
    return activity_date


def fmt_num(value: Optional[float]) -> str:
    """Formatta numero decimale"""
    return "" if value is None else f"{value:.1f}"


def fmt_duration(minutes: Optional[float]) -> str:
    """Formatta durata da minuti a HH:MM:SS"""
    if minutes is None or minutes < 0:
        return ""
    
    total_seconds = int(minutes * 60)
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    mins = remaining_seconds // 60
    secs = remaining_seconds % 60
    
    return f"{hours}:{mins:02d}:{secs:02d}"


def populate_tag_filter(tag_filter_combo: QComboBox, all_activities: list) -> None:
    """Popola il dropdown dei tag"""
    all_tags = set()
    for activity in all_activities:
        tags = activity.get("tags", [])
        if tags:
            all_tags.update(tags)
    
    all_tags = sorted(list(all_tags))
    
    # Preserve current selection
    current_tag = tag_filter_combo.currentData()
    
    # Clear and rebuild
    tag_filter_combo.blockSignals(True)
    tag_filter_combo.clear()
    tag_filter_combo.addItem("-- Tutti --", None)
    for tag in all_tags:
        tag_filter_combo.addItem(tag, tag)
    
    # Restore selection
    if current_tag:
        idx = tag_filter_combo.findData(current_tag)
        if idx >= 0:
            tag_filter_combo.setCurrentIndex(idx)
    
    tag_filter_combo.blockSignals(False)


def update_races_recap(storage, races_recap_label: QLabel) -> None:
    """Aggiorna il recap veloce delle prossime gare"""
    all_activities = storage.list_activities()
    races = [a for a in all_activities if a.get("is_race", False)]
    
    if not races:
        races_recap_label.setText("Nessuna gara pianificata")
        return
    
    # Ordina per data crescente
    races = sorted(races, key=lambda x: x.get("activity_date", "")[:10])
    
    # Mostra le prossime 3 gare
    recap_items = []
    for race in races[:3]:
        title = race.get("title", "")[:30]
        athlete = race.get("athlete_name", "").split()[0]
        date_str = race.get("activity_date", "")[:10]
        recap_items.append(f"{athlete} - {date_str}: {title}")
    
    recap_text = " | ".join(recap_items)
    races_recap_label.setText(recap_text)
