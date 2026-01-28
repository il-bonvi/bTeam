# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from .dialog_athletes import SimpleAthleteDialog, AthleteDetailsDialog
from .dialog_activities import SimpleActivityDialog, ActivityDetailsDialog
from .dialog_teams import ManageTeamsDialog
from .dialog_sync import IntervalsDialog, SyncIntervalsDialog
from .dialog_wellness import WellnessDialog
from .dialog_planning import PlanWeekDialog, ExportImportDialog
from .dialog_races import RacesDialog

__all__ = [
    'SimpleAthleteDialog',
    'AthleteDetailsDialog',
    'SimpleActivityDialog',
    'ActivityDetailsDialog',
    'ManageTeamsDialog',
    'IntervalsDialog',
    'SyncIntervalsDialog',
    'WellnessDialog',
    'PlanWeekDialog',
    'ExportImportDialog',
    'RacesDialog',
]
