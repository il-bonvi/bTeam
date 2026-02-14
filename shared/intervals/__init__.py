# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

"""Intervals.icu Integration Module"""

from .client import IntervalsAPIClient, format_workout_description
from .models import (
    Activity, Wellness, CalendarEvent, Athlete, 
    Interval, WorkoutStep, Folder, WorkoutLibrary,
    ActivityType, EventCategory
)
from .sync import IntervalsSyncService

__all__ = [
    'IntervalsAPIClient',
    'format_workout_description',
    'Activity',
    'Wellness',
    'CalendarEvent',
    'Athlete',
    'Interval',
    'WorkoutStep',
    'Folder',
    'WorkoutLibrary',
    'ActivityType',
    'EventCategory',
    'IntervalsSyncService',
]
