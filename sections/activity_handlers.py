# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

import json
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidgetItem,
    QPushButton, QMessageBox, QTextEdit, QGridLayout, QProgressBar
)


def show_activity_details(parent, storage, activity_id: int, on_download_fit) -> None:
    """Mostra i dettagli di un'attività in un dialog"""
    activity = storage.get_activity(activity_id)
    
    if not activity:
        return
    
    details_dialog = QDialog(parent)
    details_dialog.setWindowTitle("Dettagli Attività")
    details_dialog.setMinimumWidth(500)
    layout = QVBoxLayout(details_dialog)
    
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
    grid = QGridLayout()
    grid.setSpacing(10)
    grid.setColumnMinimumWidth(1, 250)
    
    row_idx = 0
    fields = [
        ("ID", str(activity.get("id", ""))),
        ("Atleta", activity.get("athlete_name", "")),
        ("Data", activity.get("activity_date", "")),
        ("Durata (min)", format_num(activity.get("duration_minutes"))),
        ("Distanza (km)", format_num(activity.get("distance_km"))),
        ("TSS", format_num(activity.get("tss"))),
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
            payload_data = json.loads(activity.get("intervals_payload"))
            payload_text.setPlainText(json.dumps(payload_data, indent=2, ensure_ascii=False))
        except:
            payload_text.setPlainText(activity.get("intervals_payload", ""))
        layout.addWidget(payload_text)
    
    layout.addStretch()
    
    # Pulsanti personalizzati
    buttons_layout = QHBoxLayout()
    
    # Pulsante download FIT (se attività da Intervals)
    if activity.get("source") == "intervals":
        fit_btn = QPushButton("💾 Scarica FIT")
        fit_btn.clicked.connect(lambda: on_download_fit(
            activity_id=activity.get("id"),
            intervals_id=activity.get("id"),
            activity_title=activity.get("title"),
            athlete_name=activity.get("athlete_name"),
            details_dialog=details_dialog
        ))
        buttons_layout.addWidget(fit_btn)
    
    buttons_layout.addStretch()
    
    # Pulsante chiusura
    close_btn = QPushButton("Chiudi")
    close_btn.clicked.connect(details_dialog.accept)
    buttons_layout.addWidget(close_btn)
    
    layout.addLayout(buttons_layout)
    
    details_dialog.exec()


def delete_activity_with_confirmation(parent, storage, activity_id: int) -> bool:
    """Elimina un'attività dopo conferma"""
    confirm_dialog = QDialog(parent)
    confirm_dialog.setWindowTitle("Conferma eliminazione")
    confirm_dialog.setMinimumWidth(300)
    layout = QVBoxLayout(confirm_dialog)
    
    layout.addWidget(QLabel("Sei sicuro di voler eliminare questa attività?"))
    
    from PySide6.QtWidgets import QDialogButtonBox
    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.accepted.connect(confirm_dialog.accept)
    buttons.rejected.connect(confirm_dialog.reject)
    layout.addWidget(buttons)
    
    if confirm_dialog.exec():
        if storage.delete_activity(activity_id):
            print(f"[bTeam] Attività {activity_id} eliminata")
            return True
        else:
            error_dialog = QDialog(parent)
            error_dialog.setWindowTitle("Errore")
            error_layout = QVBoxLayout(error_dialog)
            error_layout.addWidget(QLabel("Errore durante l'eliminazione dell'attività"))
            from PySide6.QtWidgets import QDialogButtonBox
            error_buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            error_buttons.accepted.connect(error_dialog.accept)
            error_layout.addWidget(error_buttons)
            error_dialog.exec()
            return False
    
    return False


def format_num(value) -> str:
    """Formatta numero decimale"""
    return "" if value is None else f"{value:.1f}"


def download_fit_file(parent, storage, sync_service, activity_id: int, intervals_id: str, activity_title: str, athlete_name: str) -> None:
    """Scarica il file FIT da Intervals.icu e lo salva localmente"""
    try:
        if not sync_service.is_connected():
            QMessageBox.warning(parent, "Errore", "Non connesso a Intervals.icu")
            return
        
        # Crea cartella fit_library se non esiste
        fit_library = storage.storage_dir / "fit_library"
        fit_library.mkdir(parents=True, exist_ok=True)
        
        # Struttura cartella: fit_library/{athlete_name}/{YYYY}/{MM}/
        activity = storage.get_activity(activity_id)
        if not activity:
            QMessageBox.warning(parent, "Errore", "Attività non trovata nel database")
            return
        
        # Parse activity date
        activity_date_str = activity.get("activity_date", "")
        try:
            if "T" in activity_date_str:
                date_obj = datetime.fromisoformat(activity_date_str.replace("Z", "+00:00"))
            elif len(activity_date_str) == 10:
                date_obj = datetime.strptime(activity_date_str, "%Y-%m-%d")
            else:
                date_obj = datetime.now()
        except:
            date_obj = datetime.now()
        
        # Crea struttura cartella
        year_month_dir = fit_library / athlete_name / str(date_obj.year) / f"{date_obj.month:02d}"
        year_month_dir.mkdir(parents=True, exist_ok=True)
        
        # Nome file: {activity_id}_{title}.fit
        sanitized_title = activity_title.replace("/", "_").replace("\\", "_")[:50]
        fit_filename = f"{activity_id}_{sanitized_title}.fit"
        fit_path = year_month_dir / fit_filename
        
        # Mostra progress dialog
        progress = QDialog(parent)
        progress.setWindowTitle("Download FIT")
        progress.setMinimumWidth(300)
        progress_layout = QVBoxLayout(progress)
        progress_layout.addWidget(QLabel(f"Scaricamento: {activity_title}..."))
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(0)  # Indeterminate
        progress_layout.addWidget(progress_bar)
        progress.show()
        
        # Scarica file FIT
        print(f"[bTeam] Scaricamento FIT da Intervals per attività {intervals_id}...")
        fit_content = sync_service.api_client.download_activity_fit_file(
            activity_id=str(intervals_id),
            save_path=str(fit_path)
        )
        
        # Salva nel database
        from datetime import datetime as dt
        file_size_kb = len(fit_content) / 1024
        now = dt.utcnow().isoformat()
        storage.session.execute(
            f"""INSERT INTO fit_files (activity_id, file_path, file_size_kb, downloaded_at, intervals_id, created_at)
               VALUES ({activity_id}, '{fit_path.relative_to(storage.storage_dir)}', {file_size_kb}, '{now}', '{intervals_id}', '{now}')"""
        )
        storage.session.commit()
        
        progress.close()
        
        QMessageBox.information(
            parent, 
            "Download completato",
            f"FIT salvato in:\n{fit_path}"
        )
        
        print(f"[bTeam] FIT scaricato e salvato: {fit_path}")
        
    except Exception as e:
        print(f"[bTeam] Errore download FIT: {e}")
        QMessageBox.critical(parent, "Errore", f"Errore durante il download: {str(e)}")
