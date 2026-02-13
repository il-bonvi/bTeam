# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QDialogButtonBox,
    QGroupBox,
)


class ManageTeamsDialog(QDialog):
    """Dialog per gestire le squadre"""
    
    def __init__(self, parent=None, storage=None):
        super().__init__(parent)
        self.setWindowTitle("Gestisci squadre")
        self.setMinimumSize(500, 400)
        self.storage = storage

        layout = QVBoxLayout(self)

        self.teams_list = QTableWidget(0, 2)
        self.teams_list.setHorizontalHeaderLabels(["ID", "Nome squadra"])
        self.teams_list.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.teams_list)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Aggiungi squadra")
        btn_add.clicked.connect(self._add_team)
        btn_edit = QPushButton("Modifica squadra")
        btn_edit.clicked.connect(self._edit_team)
        btn_delete = QPushButton("Elimina squadra")
        btn_delete.clicked.connect(self._delete_team)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        layout.addLayout(btn_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)

        self._refresh()

    def _refresh(self):
        teams = self.storage.list_teams()
        self.teams_list.setRowCount(len(teams))
        for row_idx, team in enumerate(teams):
            self.teams_list.setItem(row_idx, 0, QTableWidgetItem(str(team["id"])))
            self.teams_list.setItem(row_idx, 1, QTableWidgetItem(team["name"]))

    def _add_team(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Aggiungi squadra")
        layout = QVBoxLayout(dialog)
        name_edit = QLineEdit()
        layout.addWidget(QLabel("Nome squadra"))
        layout.addWidget(name_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip():
                self.storage.add_team(name_edit.text())
                self._refresh()

    def _edit_team(self):
        row = self.teams_list.currentRow()
        if row < 0:
            return
        team_id = int(self.teams_list.item(row, 0).text())
        old_name = self.teams_list.item(row, 1).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Modifica squadra")
        layout = QVBoxLayout(dialog)
        name_edit = QLineEdit()
        name_edit.setText(old_name)
        layout.addWidget(QLabel("Nome squadra"))
        layout.addWidget(name_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip():
                self.storage.update_team(team_id, name_edit.text())
                self._refresh()

    def _delete_team(self):
        row = self.teams_list.currentRow()
        if row < 0:
            return
        team_id = int(self.teams_list.item(row, 0).text())
        team_name = self.teams_list.item(row, 1).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Conferma eliminazione")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Eliminare la squadra '{team_name}'?\nGli atleti verranno mantenuti senza squadra."))
        buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            self.storage.delete_team(team_id)
            self._refresh()
