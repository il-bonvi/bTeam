# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox
)


def show_add_team_dialog(parent, storage) -> bool:
    """Dialog per aggiungere una nuova squadra"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Nuova squadra")
    layout = QVBoxLayout(dialog)
    team_edit = QLineEdit()
    layout.addWidget(QLabel("Nome squadra"))
    layout.addWidget(team_edit)
    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    
    if dialog.exec():
        team_name = team_edit.text().strip()
        if team_name:
            storage.add_team(team_name)
            return True
    
    return False


def show_error_dialog(parent, title: str, message: str) -> None:
    """Mostra un dialog di errore"""
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel(message))
    buttons = QDialogButtonBox(QDialogButtonBox.Ok)
    buttons.accepted.connect(dialog.accept)
    layout.addWidget(buttons)
    dialog.exec()


def show_confirmation_dialog(parent, title: str, message: str) -> bool:
    """Mostra un dialog di conferma e ritorna True se accettato"""
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setMinimumWidth(300)
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel(message))
    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    
    return dialog.exec() == QDialog.Accepted
