# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from config_bteam import set_intervals_api_key
from dialogs import SyncIntervalsDialog, WellnessDialog, PlanWeekDialog, RacesDialog, ExportImportDialog
from intervals_sync import IntervalsSyncService
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox


def show_sync_intervals_dialog(parent, sync_service, storage, on_sync_complete) -> None:
    """Dialog per configurare e sincronizzare attività da Intervals.icu"""
    dialog = SyncIntervalsDialog(parent, sync_service, storage)
    if dialog.exec():
        # Aggiorna la API key se modificata
        new_api_key = dialog.get_api_key()
        if new_api_key and new_api_key != sync_service.api_key:
            set_intervals_api_key(new_api_key)
            if sync_service.set_api_key(new_api_key):
                print(f"[bTeam] API key Intervals.icu aggiornata")
        
        # Avvia la sincronizzazione
        selected_athlete_id = dialog.get_selected_athlete()
        days_back = dialog.get_days_back()
        
        if sync_service.is_connected() and selected_athlete_id:
            perform_sync(parent, sync_service, storage, selected_athlete_id, days_back, on_sync_complete)


def perform_sync(parent, sync_service, storage, athlete_id: int, days_back: int = 30, on_complete=None) -> None:
    """Esegue la sincronizzazione delle attività"""
    activities, fetch_message = sync_service.fetch_activities(days_back=days_back)
    
    new_count = 0
    duplicate_count = 0
    error_count = 0
    
    if activities:
        # Salva le attività nell'app
        for activity in activities:
            try:
                formatted = IntervalsSyncService.format_activity_for_storage(activity)
                activity_id, is_new = storage.add_activity(
                    athlete_id=athlete_id,
                    title=formatted['name'],
                    activity_date=formatted['start_date'],
                    duration_minutes=formatted['moving_time_minutes'],
                    distance_km=formatted['distance_km'],
                    tss=None,
                    source='intervals',
                    intervals_id=str(formatted['intervals_id']),
                    is_race=formatted.get('is_race'),
                    tags=formatted.get('tags', []),
                    avg_watts=formatted.get('avg_watts'),
                    normalized_watts=formatted.get('normalized_watts'),
                    avg_hr=formatted.get('avg_hr'),
                    max_hr=formatted.get('max_hr'),
                    avg_cadence=formatted.get('avg_cadence'),
                    training_load=formatted.get('training_load'),
                    intensity=formatted.get('intensity'),
                    feel=formatted.get('feel'),
                    calories=formatted.get('calories'),
                    activity_type=formatted.get('type'),
                )
                if is_new:
                    new_count += 1
                else:
                    duplicate_count += 1
            except Exception as e:
                error_count += 1
                print(f"[bTeam] Errore inserimento attività: {e}")
        
        # Costruisci messaggio dettagliato
        parts = []
        if new_count > 0:
            parts.append(f"✅ {new_count} nuove attività")
        if duplicate_count > 0:
            parts.append(f"⚠️  {duplicate_count} già presenti (duplicate)")
        if error_count > 0:
            parts.append(f"❌ {error_count} errori")
        
        message = "Sincronizzazione completata:\n" + "\n".join(parts) if parts else "✅ Nessuna attività da sincronizzare"
    else:
        message = "✅ Nessuna attività trovata negli ultimi " + str(days_back) + " giorni"
    
    print(f"[bTeam] {message}")
    
    # Mostra risultato con dialog
    result_dialog = QDialog(parent)
    result_dialog.setWindowTitle("Risultato sincronizzazione")
    result_dialog.setMinimumWidth(350)
    layout = QVBoxLayout(result_dialog)
    
    # Titolo
    title_label = QLabel("Sincronizzazione Intervals.icu")
    title_font = title_label.font()
    title_font.setBold(True)
    title_font.setPointSize(11)
    title_label.setFont(title_font)
    layout.addWidget(title_label)
    
    # Messaggio
    msg_label = QLabel(message)
    msg_label.setStyleSheet("margin-top: 10px; margin-bottom: 10px;")
    layout.addWidget(msg_label)
    
    # Pulsanti
    buttons = QDialogButtonBox(QDialogButtonBox.Ok)
    buttons.accepted.connect(result_dialog.accept)
    layout.addWidget(buttons)
    
    result_dialog.exec()
    
    # Callback per refresh
    if on_complete:
        on_complete()


def show_wellness_dialog(parent, sync_service) -> None:
    """Apre il dialog per visualizzare dati wellness"""
    # Get athlete from parent (assuming parent is the main window)
    if not hasattr(parent, 'selected_athlete_id') or not parent.selected_athlete_id:
        return
    
    athlete_id = parent.selected_athlete_id
    athlete_name = parent.selected_athlete_name if hasattr(parent, 'selected_athlete_name') else ""
    
    dialog = WellnessDialog(
        parent, 
        athlete_id=athlete_id,
        athlete_name=athlete_name,
        storage=parent.storage if hasattr(parent, 'storage') else None,
        sync_service=sync_service
    )
    dialog.exec()


def show_plan_week_dialog(parent, sync_service, on_plan_created) -> None:
    """Apre il dialog per pianificare una settimana di allenamenti"""
    dialog = PlanWeekDialog(parent, sync_service)
    if dialog.exec():
        plan = dialog.get_plan()
        
        if not sync_service.is_connected():
            error = QDialog(parent)
            error.setWindowTitle("Errore")
            layout = QVBoxLayout(error)
            layout.addWidget(QLabel("Intervals.icu non è connesso. Configura l'API key prima."))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(error.accept)
            layout.addWidget(buttons)
            error.exec()
            return
        
        # Crea i workout
        created = 0
        for workout in plan:
            success, msg = sync_service.create_workout(
                date=workout['date'],
                name=workout['name'],
                description=workout['description'],
                activity_type=workout['type']
            )
            if success:
                created += 1
        
        result = QDialog(parent)
        result.setWindowTitle("Pianificazione completata")
        layout = QVBoxLayout(result)
        layout.addWidget(QLabel(f"✅ {created} allenamenti creati su Intervals.icu"))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(result.accept)
        layout.addWidget(buttons)
        result.exec()


def show_races_dialog(parent, storage) -> None:
    """Apre il dialog per gestire gare pianificate"""
    races_dialog = RacesDialog(parent, storage)
    races_dialog.exec()


def show_export_import_dialog(parent, storage) -> None:
    """Apre il dialog per esportare/importare dati"""
    dialog = ExportImportDialog(parent, storage)
    dialog.exec()
