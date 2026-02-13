# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox


def handle_sort_column_click(column: int, current_sort_column: int, current_sort_order: Qt.SortOrder) -> tuple[int, Qt.SortOrder]:
    """Gestisce il click sul header della tabella per ordinare"""
    
    if column == current_sort_column:
        # Se clicco la stessa colonna, inverti l'ordine
        new_order = Qt.AscendingOrder if current_sort_order == Qt.DescendingOrder else Qt.DescendingOrder
    else:
        # Se clicco una colonna diversa, ordina in descending
        current_sort_column = column
        new_order = Qt.DescendingOrder
    
    return current_sort_column, new_order


def apply_activity_filters(
    all_activities: list,
    tag_filter_combo: QComboBox,
    current_sort_column: int,
    current_sort_order: Qt.SortOrder
) -> list:
    """Applica i filtri alle attività (tag)"""
    selected_tag = tag_filter_combo.currentData()
    
    # Filtra le attività
    filtered = all_activities
    
    if selected_tag:
        filtered = [a for a in filtered if selected_tag in a.get("tags", [])]
    
    # Applica l'ordinamento personalizzato
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
        filtered = sorted(filtered, key=get_sort_key, reverse=reverse)
    except Exception as e:
        print(f"[bTeam] Errore ordinamento: {e}")
    
    return filtered
