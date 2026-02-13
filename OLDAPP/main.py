#!/usr/bin/env python3
# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

"""
MAIN.PY - Launcher standalone per bTeam

Consente di avviare bTeam direttamente come applicazione indipendente.
Perfetto per copia-incolla in altre posizioni.

Uso:
    python main.py [--theme "Forest Green"]
"""

import sys
from pathlib import Path

# Aggiungi il path del progetto (directory corrente)
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication

# Import della GUI - fatto dopo che il path è stato configurato
from gui_bteam import BTeamApp


def main():
    """Avvia bTeam come applicazione standalone"""
    
    # Parse arguments
    theme = "Forest Green"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--theme" and len(sys.argv) > 2:
            theme = sys.argv[2]
    
    # Crea app Qt
    app = QApplication([])
    
    # Crea e mostra bTeam
    bteam = BTeamApp(theme=theme)
    bteam.showMaximized()
    
    print(f"\n[*] bTeam avviato (standalone)")
    print(f"    Tema: {theme}")
    print(f"    Finestra massimizzata\n")
    
    # Run
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
