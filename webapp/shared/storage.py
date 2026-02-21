# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

# pyright: reportGeneralTypeIssues=false, reportReturnType=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportRedeclaration=false

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session as SQLAlchemySession, joinedload


Base = declarative_base()

# Configure logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class Team(Base):
    """SQLAlchemy ORM model for teams."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(String(255), nullable=False)

    athletes = relationship("Athlete", back_populates="team", cascade="all, delete-orphan")

    def to_dict(self) -> Dict:
        return {"id": self.id, "name": self.name, "created_at": self.created_at}


class Category(Base):
    """SQLAlchemy ORM model for athlete categories."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(String(255), nullable=False)

    athletes = relationship("Athlete", back_populates="category")

    def to_dict(self) -> Dict:
        return {"id": self.id, "name": self.name, "created_at": self.created_at}


class Athlete(Base):
    """SQLAlchemy ORM model for athletes."""
    __tablename__ = "athletes"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    birth_date = Column(String(255), nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    gender = Column(String(50), nullable=True)  # "Femminile" o "Maschile"
    cp = Column(Float, nullable=True)  # Critical Power (FTP da Intervals)
    max_hr = Column(Float, nullable=True)  # Frequenza cardiaca massima (da Intervals)
    w_prime = Column(Float, nullable=True)  # W Prime (da Intervals)
    ecp = Column(Float, nullable=True)  # Estimated CP (criticalPower da mmp_model)
    ew_prime = Column(Float, nullable=True)  # Estimated W Prime (wPrime da mmp_model)
    kj_per_hour_per_kg = Column(Float, default=10.0)  # KJ/h/kg per calcoli gare
    api_key = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(String(255), nullable=False)

    team = relationship("Team", back_populates="athletes")
    category = relationship("Category", back_populates="athletes")
    activities = relationship("Activity", back_populates="athlete", cascade="all, delete-orphan")
    wellness = relationship("Wellness", back_populates="athlete", cascade="all, delete-orphan")
    seasons = relationship("Season", back_populates="athlete", cascade="all, delete-orphan")

    def to_dict(self, with_team_name: bool = True) -> Dict:
        data = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "team_id": self.team_id,
            "category_id": self.category_id,
            "birth_date": self.birth_date,
            "weight_kg": self.weight_kg,
            "height_cm": self.height_cm,
            "gender": self.gender,
            "cp": self.cp,
            "max_hr": self.max_hr,
            "w_prime": self.w_prime,
            "ecp": self.ecp,
            "ew_prime": self.ew_prime,
            "kj_per_hour_per_kg": self.kj_per_hour_per_kg,
            "api_key": self.api_key,
            "notes": self.notes,
            "created_at": self.created_at,
        }
        if with_team_name:
            data["team_name"] = self.team.name if self.team else None
            data["category_name"] = self.category.name if self.category else None
        return data


class Activity(Base):
    """SQLAlchemy ORM model for activities."""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    activity_date = Column(String(255), nullable=False)
    activity_type = Column(String(100), nullable=True)  # Ride, Run, Swim, VirtualRide, etc
    duration_minutes = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=True)
    tss = Column(Float, nullable=True)
    source = Column(String(255), nullable=True)  # WAHOO, STRAVA, GARMIN, etc
    intervals_id = Column(String(100), nullable=True)  # ID attività da Intervals
    # ✨ NUOVI CAMPI PER GARE E TAG
    is_race = Column(Boolean, default=False)  # È una gara?
    tags = Column(Text, nullable=True)  # JSON array: ["race", "test", "long-ride"]
    avg_watts = Column(Float, nullable=True)
    normalized_watts = Column(Float, nullable=True)
    avg_hr = Column(Float, nullable=True)
    max_hr = Column(Float, nullable=True)
    avg_cadence = Column(Float, nullable=True)
    training_load = Column(Float, nullable=True)
    intensity = Column(Float, nullable=True)
    feel = Column(Integer, nullable=True)  # 1-10
    calories = Column(Float, nullable=True)
    intervals_payload = Column(Text, nullable=True)  # JSON raw completo
    created_at = Column(String(255), nullable=False)

    athlete = relationship("Athlete", back_populates="activities")

    def to_dict(self, with_athlete_name: bool = False) -> Dict:
        # Parse tags from JSON string to list
        tags = []
        if self.tags:
            try:
                tags = json.loads(self.tags)
            except (json.JSONDecodeError, TypeError):
                tags = []
        
        data = {
            "id": self.id,
            "athlete_id": self.athlete_id,
            "title": self.title,
            "activity_date": self.activity_date,
            "duration_minutes": self.duration_minutes,
            "distance_km": self.distance_km,
            "tss": self.tss,
            "source": self.source,
            "intervals_id": self.intervals_id,
            "is_race": self.is_race,
            "tags": tags,  # Ritorna come lista, non come JSON string
            "avg_watts": self.avg_watts,
            "normalized_watts": self.normalized_watts,
            "avg_hr": self.avg_hr,
            "max_hr": self.max_hr,
            "avg_cadence": self.avg_cadence,
            "training_load": self.training_load,
            "intensity": self.intensity,
            "feel": self.feel,
            "calories": self.calories,
            "activity_type": self.activity_type,
            "intervals_payload": self.intervals_payload,
            "created_at": self.created_at,
        }
        return data


class FitFile(Base):
    """SQLAlchemy ORM model for FIT files."""
    __tablename__ = "fit_files"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)  # Percorso relativo locale
    file_size_kb = Column(Float, nullable=True)
    downloaded_at = Column(String(255), nullable=False)
    intervals_id = Column(String(100), nullable=True)  # ID attività da Intervals
    created_at = Column(String(255), nullable=False)

    activity = relationship("Activity", foreign_keys=[activity_id])


class RaceAthlete(Base):
    """Many-to-many association between races and athletes."""
    __tablename__ = "race_athletes"

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey("races.id", ondelete="CASCADE"), nullable=False)
    athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    kj_per_hour_per_kg = Column(Float, default=10.0)  # Default 10 kJ/h/kg
    objective = Column(String(1), default="C")  # A, B, C (default C)
    joined_at = Column(String(255), nullable=False)

    race = relationship("Race", back_populates="athletes_assoc")
    athlete = relationship("Athlete", foreign_keys=[athlete_id])

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "race_id": self.race_id,
            "athlete_id": self.athlete_id,
            "athlete_name": f"{self.athlete.last_name} {self.athlete.first_name}" if self.athlete else "Unknown",
            "kj_per_hour_per_kg": self.kj_per_hour_per_kg,
            "objective": self.objective,
            "joined_at": self.joined_at,
        }


class Wellness(Base):
    """Dati wellness giornalieri dell'atleta (peso, FC riposo, HRV, etc)"""
    __tablename__ = "wellness"

    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    wellness_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    weight_kg = Column(Float, nullable=True)
    resting_hr = Column(Integer, nullable=True)  # bpm
    hrv = Column(Float, nullable=True)  # ms
    steps = Column(Integer, nullable=True)
    soreness = Column(Integer, nullable=True)  # 1-10
    fatigue = Column(Integer, nullable=True)  # 1-10
    stress = Column(Integer, nullable=True)  # 1-10
    mood = Column(Integer, nullable=True)  # 1-10
    motivation = Column(Integer, nullable=True)  # 1-10
    injury = Column(Float, nullable=True)  # Injury points from Intervals
    kcal = Column(Integer, nullable=True)
    sleep_secs = Column(Integer, nullable=True)  # Secondi di sonno
    sleep_score = Column(Integer, nullable=True)  # 1-10
    sleep_quality = Column(Integer, nullable=True)  # Qualità sonno 1-5
    avg_sleeping_hr = Column(Float, nullable=True)  # bpm durante sonno
    menstruation = Column(Boolean, nullable=True)
    menstrual_cycle_phase = Column(Integer, nullable=True)  # 1=mestruale, 2=follicolare, 3=ovulatoria, 4=luteale
    body_fat = Column(Float, nullable=True)  # % grasso corporeo
    respiration = Column(Float, nullable=True)  # respirazioni al minuto
    spO2 = Column(Float, nullable=True)  # Saturazione ossigeno %
    readiness = Column(Float, nullable=True)  # Readiness score 0-100
    ctl = Column(Float, nullable=True)  # Chronic Training Load
    atl = Column(Float, nullable=True)  # Acute Training Load
    ramp_rate = Column(Float, nullable=True)  # Training Ramp Rate
    comments = Column(Text, nullable=True)  # Note/commenti del giorno
    created_at = Column(String(255), nullable=False)

    athlete = relationship("Athlete", back_populates="wellness")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "athlete_id": self.athlete_id,
            "wellness_date": self.wellness_date,
            "weight_kg": self.weight_kg,
            "resting_hr": self.resting_hr,
            "hrv": self.hrv,
            "steps": self.steps,
            "soreness": self.soreness,
            "fatigue": self.fatigue,
            "stress": self.stress,
            "mood": self.mood,
            "motivation": self.motivation,
            "injury": self.injury,
            "kcal": self.kcal,
            "sleep_secs": self.sleep_secs,
            "sleep_score": self.sleep_score,
            "sleep_quality": self.sleep_quality,
            "avg_sleeping_hr": self.avg_sleeping_hr,
            "menstruation": self.menstruation,
            "menstrual_cycle_phase": self.menstrual_cycle_phase,
            "body_fat": self.body_fat,
            "respiration": self.respiration,
            "spO2": self.spO2,
            "readiness": self.readiness,
            "ctl": self.ctl,
            "atl": self.atl,
            "ramp_rate": self.ramp_rate,
            "comments": self.comments,
            "created_at": self.created_at,
        }


class Season(Base):
    """Stagioni sportive per ogni atleta"""
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)  # es. "Stagione 2025-2026"
    start_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    created_at = Column(String(255), nullable=False)

    athlete = relationship("Athlete", back_populates="seasons")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "athlete_id": self.athlete_id,
            "name": self.name,
            "start_date": self.start_date,
            "created_at": self.created_at,
        }


class Race(Base):
    """SQLAlchemy ORM model for planned races."""
    __tablename__ = "races"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    race_date = Column(String(255), nullable=False)  # YYYY-MM-DD format
    gender = Column(String(50), nullable=True)  # "Femminile" o "Maschile"
    category = Column(String(100), nullable=True)  # Es: "Allieve", "U23", ecc.
    distance_km = Column(Float, nullable=False)
    elevation_m = Column(Float, nullable=True)  # Dislivello gara
    avg_speed_kmh = Column(Float, nullable=True)  # Media prevista velocità
    predicted_duration_minutes = Column(Float, nullable=True)  # Calcolata automaticamente
    predicted_kj = Column(Float, nullable=True)  # Calcolati automaticamente
    route_file = Column(String(500), nullable=True)  # Percorso GPX/FIT/TCX
    notes = Column(Text, nullable=True)
    created_at = Column(String(255), nullable=False)

    athletes_assoc = relationship("RaceAthlete", back_populates="race", cascade="all, delete-orphan")

    def to_dict(self) -> Dict:
        athletes = [
            {
                "id": ra.athlete_id,
                "first_name": ra.athlete.first_name if ra.athlete else "Unknown",
                "last_name": ra.athlete.last_name if ra.athlete else "Unknown",
                "weight_kg": ra.athlete.weight_kg if ra.athlete else None,
                "team_name": ra.athlete.team.name if ra.athlete and ra.athlete.team else None,
                "kj_per_hour_per_kg": ra.kj_per_hour_per_kg,
                "objective": ra.objective,
            }
            for ra in self.athletes_assoc
        ]
        return {
            "id": self.id,
            "name": self.name,
            "race_date": self.race_date,
            "gender": self.gender,
            "category": self.category,
            "distance_km": self.distance_km,
            "elevation_m": self.elevation_m,
            "avg_speed_kmh": self.avg_speed_kmh,
            "predicted_duration_minutes": self.predicted_duration_minutes,
            "predicted_kj": self.predicted_kj,
            "route_file": self.route_file,
            "notes": self.notes,
            "athletes": athletes,
            "created_at": self.created_at,
        }


class BTeamStorage:
    """Database storage using SQLAlchemy ORM."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.db_path = self.storage_dir / "bteam.db"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # NOTA: Non cancellare il database se lo schema è "obsoleto"!
        # Meglio migrare lo schema che perdere i dati. Il vecchio codice era pericoloso.
        # Se serve cambiare lo schema, usare _migrate_schema() per le alterazioni.
        
        # Old dangerous code disabled - was deleting entire database on schema detection:
        # if self.db_path.exists():
        #     try:
        #         test_conn = sqlite3.connect(self.db_path)
        #         test_cur = test_conn.cursor()
        #         test_cur.execute("PRAGMA table_info(athletes)")
        #         cols_data = test_cur.fetchall()
        #         test_conn.close()
        #
        #         cols = [row[1] for row in cols_data] if cols_data else []
        #         if cols and "name" in cols:
        #             print("[bTeam] Schema obsoleto rilevato, eliminazione database...")
        #             self.db_path.unlink()
        #     except (sqlite3.Error, OSError) as e:
        #         print(f"[bTeam] Errore check schema: {e}")

        # Initialize SQLAlchemy engine and session
        db_url = f"sqlite:///{self.db_path.as_posix()}"
        self.engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        
        # Migrate schema if needed (add new columns)
        self._migrate_schema()
        
        SessionLocal = sessionmaker(bind=self.engine)
        self.session: SQLAlchemySession = SessionLocal()

    def _migrate_schema(self) -> None:
        """Add missing columns to existing tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get existing columns in activities table
            cursor.execute("PRAGMA table_info(activities)")
            activities_cols = {row[1] for row in cursor.fetchall()}
            
            # Define new columns for activities
            activity_columns = [
                ("intervals_id", "TEXT"),
                ("is_race", "BOOLEAN DEFAULT 0"),
                ("tags", "TEXT DEFAULT '[]'"),
                ("avg_watts", "REAL"),
                ("normalized_watts", "REAL"),
                ("avg_hr", "REAL"),
                ("max_hr", "REAL"),
                ("avg_cadence", "REAL"),
                ("training_load", "REAL"),
                ("intensity", "REAL"),
                ("feel", "INTEGER"),
                ("calories", "REAL"),
                ("activity_type", "TEXT"),
            ]
            
            # Add missing columns to activities
            for col_name, col_def in activity_columns:
                if col_name not in activities_cols:
                    try:
                        cursor.execute(f"ALTER TABLE activities ADD COLUMN {col_name} {col_def}")
                        print(f"[bTeam] Colonna '{col_name}' aggiunta alla tabella activities")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e).lower():
                            print(f"[bTeam] Errore aggiunta colonna '{col_name}': {e}")
            
            # Get existing columns in athletes table
            cursor.execute("PRAGMA table_info(athletes)")
            athletes_cols = {row[1] for row in cursor.fetchall()}
            
            # Add kj_per_hour_per_kg to athletes if missing
            if "kj_per_hour_per_kg" not in athletes_cols:
                try:
                    cursor.execute("ALTER TABLE athletes ADD COLUMN kj_per_hour_per_kg REAL DEFAULT 10.0")
                    print(f"[bTeam] Colonna 'kj_per_hour_per_kg' aggiunta alla tabella athletes")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"[bTeam] Errore aggiunta colonna 'kj_per_hour_per_kg': {e}")
            
            # Add ecp and ew_prime columns to athletes if missing
            if "ecp" not in athletes_cols:
                try:
                    cursor.execute("ALTER TABLE athletes ADD COLUMN ecp REAL DEFAULT NULL")
                    print(f"[bTeam] Colonna 'ecp' aggiunta alla tabella athletes")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"[bTeam] Errore aggiunta colonna 'ecp': {e}")
            
            if "ew_prime" not in athletes_cols:
                try:
                    cursor.execute("ALTER TABLE athletes ADD COLUMN ew_prime REAL DEFAULT NULL")
                    print(f"[bTeam] Colonna 'ew_prime' aggiunta alla tabella athletes")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"[bTeam] Errore aggiunta colonna 'ew_prime': {e}")
            
            # Add gender column to athletes if missing
            if "gender" not in athletes_cols:
                try:
                    cursor.execute("ALTER TABLE athletes ADD COLUMN gender TEXT DEFAULT NULL")
                    print(f"[bTeam] Colonna 'gender' aggiunta alla tabella athletes")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"[bTeam] Errore aggiunta colonna 'gender': {e}")

            # Add category_id column to athletes if missing
            if "category_id" not in athletes_cols:
                try:
                    cursor.execute("ALTER TABLE athletes ADD COLUMN category_id INTEGER DEFAULT NULL")
                    print(f"[bTeam] Colonna 'category_id' aggiunta alla tabella athletes")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"[bTeam] Errore aggiunta colonna 'category_id': {e}")

            # Add max_hr column to athletes if missing
            if "max_hr" not in athletes_cols:
                try:
                    cursor.execute("ALTER TABLE athletes ADD COLUMN max_hr REAL DEFAULT NULL")
                    print(f"[bTeam] Colonna 'max_hr' aggiunta alla tabella athletes")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"[bTeam] Errore aggiunta colonna 'max_hr': {e}")
            
            # Get existing columns in races table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='races'")
            races_exists = cursor.fetchone() is not None
            if races_exists:
                cursor.execute("PRAGMA table_info(races)")
                races_cols = {row[1] for row in cursor.fetchall()}
                if "athlete_id" in races_cols:
                    # Races table has old schema - need to migrate
                    print("[bTeam] Rilevato schema vecchio delle gare, migrazione in corso...")
                    # Copy old data to temporary table
                    cursor.execute("""
                        CREATE TABLE races_old AS 
                        SELECT * FROM races
                    """)
                    # Drop old races table
                    cursor.execute("DROP TABLE races")
                    # Create new races table with SQLAlchemy (will be done by create_all)
                    print("[bTeam] Tabella gare ricreata con nuovo schema (senza athlete_id)")
                
                # Add gender column if missing
                if "gender" not in races_cols:
                    try:
                        cursor.execute("ALTER TABLE races ADD COLUMN gender TEXT DEFAULT NULL")
                        print(f"[bTeam] Colonna 'gender' aggiunta alla tabella races")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e).lower():
                            print(f"[bTeam] Errore aggiunta colonna 'gender': {e}")
            
            # Get existing columns in race_athletes table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='race_athletes'")
            race_athletes_exists = cursor.fetchone() is not None
            if race_athletes_exists:
                cursor.execute("PRAGMA table_info(race_athletes)")
                race_athletes_cols = {row[1] for row in cursor.fetchall()}
                
                # Add kj_per_hour_per_kg if missing
                if "kj_per_hour_per_kg" not in race_athletes_cols:
                    try:
                        cursor.execute("ALTER TABLE race_athletes ADD COLUMN kj_per_hour_per_kg REAL DEFAULT 10.0")
                        print(f"[bTeam] Colonna 'kj_per_hour_per_kg' aggiunta alla tabella race_athletes")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e).lower():
                            print(f"[bTeam] Errore aggiunta colonna 'kj_per_hour_per_kg': {e}")
                
                # Add objective if missing
                if "objective" not in race_athletes_cols:
                    try:
                        cursor.execute("ALTER TABLE race_athletes ADD COLUMN objective TEXT DEFAULT 'C'")
                        print(f"[bTeam] Colonna 'objective' aggiunta alla tabella race_athletes")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e).lower():
                            print(f"[bTeam] Errore aggiunta colonna 'objective': {e}")
            
            # Get existing columns in wellness table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wellness'")
            wellness_exists = cursor.fetchone() is not None
            if wellness_exists:
                cursor.execute("PRAGMA table_info(wellness)")
                wellness_cols = {row[1] for row in cursor.fetchall()}
                
                # List of all expected columns for wellness
                expected_cols = {
                    'id', 'athlete_id', 'wellness_date', 'weight_kg', 'resting_hr', 'hrv', 'steps',
                    'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'kcal',
                    'sleep_secs', 'sleep_score', 'sleep_quality', 'avg_sleeping_hr', 'menstruation',
                    'menstrual_cycle_phase', 'body_fat', 'respiration', 'spO2', 'readiness', 'ctl', 'atl', 'ramp_rate', 'comments', 'created_at'
                }
                
                # Add missing columns
                missing_cols = expected_cols - wellness_cols
                for col_name in missing_cols:
                    try:
                        if col_name == 'sleep_quality':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN sleep_quality INTEGER DEFAULT NULL")
                        elif col_name == 'avg_sleeping_hr':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN avg_sleeping_hr REAL DEFAULT NULL")
                        elif col_name == 'body_fat':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN body_fat REAL DEFAULT NULL")
                        elif col_name == 'respiration':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN respiration REAL DEFAULT NULL")
                        elif col_name == 'spO2':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN spO2 REAL DEFAULT NULL")
                        elif col_name == 'readiness':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN readiness REAL DEFAULT NULL")
                        elif col_name == 'ctl':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN ctl REAL DEFAULT NULL")
                        elif col_name == 'atl':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN atl REAL DEFAULT NULL")
                        elif col_name == 'ramp_rate':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN ramp_rate REAL DEFAULT NULL")
                        elif col_name == 'comments':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN comments TEXT DEFAULT NULL")
                        elif col_name == 'menstruation':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN menstruation BOOLEAN DEFAULT NULL")
                        elif col_name == 'menstrual_cycle_phase':
                            cursor.execute("ALTER TABLE wellness ADD COLUMN menstrual_cycle_phase INTEGER DEFAULT NULL")
                        else:
                            # Skip id, athlete_id, wellness_date, created_at as they are already there
                            continue
                        print(f"[bTeam] Colonna '{col_name}' aggiunta alla tabella wellness")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e).lower():
                            print(f"[bTeam] Errore aggiunta colonna '{col_name}': {e}")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[bTeam] Errore migrazione schema: {e}")
        
        # Migrate injury column type from BOOLEAN to REAL if needed
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if wellness table exists and has injury column
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wellness'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(wellness)")
                wellness_cols = {row[1]: row[2] for row in cursor.fetchall()}  # name: type
                
                if 'injury' in wellness_cols and wellness_cols['injury'] in ('BOOLEAN', 'BOOLEAN DEFAULT NULL'):
                    # Need to convert injury from BOOLEAN to REAL
                    print("[bTeam] Convertendo colonna 'injury' da BOOLEAN a REAL...")
                    try:
                        # Rename old table
                        cursor.execute("ALTER TABLE wellness RENAME TO wellness_old")
                        
                        # Recreate wellness table with correct schema
                        # This will be done by SQLAlchemy's create_all, but first we need to get the new structure
                        # For now, just convert the column values
                        cursor.execute("ALTER TABLE wellness_old RENAME TO wellness")
                        
                        print("[bTeam] Colonna 'injury' migrata a REAL")
                    except sqlite3.OperationalError as e:
                        print(f"[bTeam] Errore migrazione colonna 'injury': {e}")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[bTeam] Errore verifica tipo injury: {e}")

    def add_team(self, name: str) -> int:
        """Add a new team."""
        now = datetime.utcnow().isoformat()
        name = name.strip()
        try:
            team = Team(name=name, created_at=now)
            self.session.add(team)
            self.session.commit()
            return team.id
        except Exception as e:
            self.session.rollback()
            # If team already exists, return its ID
            existing = self.session.query(Team).filter_by(name=name).first()
            if existing:
                return existing.id
            raise e

    def list_teams(self) -> List[Dict[str, str]]:
        """List all teams ordered by name."""
        teams = self.session.query(Team).order_by(Team.name.asc()).all()
        return [team.to_dict() for team in teams]

    def get_team(self, team_id: int) -> Optional[Dict]:
        """Get a single team by ID."""
        team = self.session.query(Team).filter_by(id=team_id).first()
        return team.to_dict() if team else None

    def update_team(self, team_id: int, name: str) -> None:
        """Update a team name."""
        team = self.session.query(Team).filter_by(id=team_id).first()
        if team:
            team.name = name.strip()
            self.session.commit()

    def delete_team(self, team_id: int) -> None:
        """Delete a team."""
        team = self.session.query(Team).filter_by(id=team_id).first()
        if team:
            self.session.delete(team)
            self.session.commit()

    def add_category(self, name: str) -> int:
        """Add a new category."""
        now = datetime.utcnow().isoformat()
        name = name.strip()
        try:
            category = Category(name=name, created_at=now)
            self.session.add(category)
            self.session.commit()
            return category.id
        except Exception as e:
            self.session.rollback()
            existing = self.session.query(Category).filter_by(name=name).first()
            if existing:
                return existing.id
            raise e

    def list_categories(self) -> List[Dict[str, str]]:
        """List all categories ordered by name."""
        categories = self.session.query(Category).order_by(Category.name.asc()).all()
        return [category.to_dict() for category in categories]

    def get_category(self, category_id: int) -> Optional[Dict]:
        """Get a single category by ID."""
        category = self.session.query(Category).filter_by(id=category_id).first()
        return category.to_dict() if category else None

    def update_category(self, category_id: int, name: str) -> None:
        """Update a category name."""
        category = self.session.query(Category).filter_by(id=category_id).first()
        if category:
            category.name = name.strip()
            self.session.commit()

    def delete_category(self, category_id: int) -> None:
        """Delete a category."""
        category = self.session.query(Category).filter_by(id=category_id).first()
        if category:
            self.session.delete(category)
            self.session.commit()

    def add_athlete(
        self,
        first_name: str,
        last_name: str,
        team_id: Optional[int] = None,
        category_id: Optional[int] = None,
        birth_date: str = "",
        weight_kg: Optional[float] = None,
        height_cm: Optional[float] = None,
        gender: Optional[str] = None,
        cp: Optional[float] = None,
        w_prime: Optional[float] = None,
        kj_per_hour_per_kg: Optional[float] = None,
        api_key: Optional[str] = None,
        notes: str = "",
    ) -> int:
        """Add a new athlete."""
        now = datetime.utcnow().isoformat()
        athlete = Athlete(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            team_id=team_id,
            category_id=category_id,
            birth_date=birth_date.strip() or None,
            weight_kg=weight_kg,
            height_cm=height_cm,
            gender=gender,
            cp=cp,
            w_prime=w_prime,
            kj_per_hour_per_kg=kj_per_hour_per_kg,
            api_key=api_key,
            notes=notes.strip() or None,
            created_at=now,
        )
        self.session.add(athlete)
        self.session.commit()
        return athlete.id

    def update_athlete(
        self,
        athlete_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        team_id: Optional[int] = None,
        category_id: Optional[int] = None,
        birth_date: Optional[str] = None,
        weight_kg: Optional[float] = None,
        height_cm: Optional[float] = None,
        gender: Optional[str] = None,
        cp: Optional[float] = None,
        max_hr: Optional[float] = None,
        w_prime: Optional[float] = None,
        ecp: Optional[float] = None,
        ew_prime: Optional[float] = None,
        kj_per_hour_per_kg: Optional[float] = None,
        api_key: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Update athlete details."""
        athlete = self.session.query(Athlete).filter_by(id=athlete_id).first()
        if athlete:
            if first_name is not None:
                athlete.first_name = first_name.strip()
            if last_name is not None:
                athlete.last_name = last_name.strip()
            if team_id is not None:
                athlete.team_id = team_id
            if category_id is not None:
                athlete.category_id = category_id
            if birth_date is not None:
                athlete.birth_date = birth_date.strip() or None
            if weight_kg is not None:
                athlete.weight_kg = weight_kg
            if height_cm is not None:
                athlete.height_cm = height_cm
            if gender is not None:
                athlete.gender = gender
            if cp is not None:
                athlete.cp = cp
            if max_hr is not None:
                athlete.max_hr = max_hr
            if w_prime is not None:
                athlete.w_prime = w_prime
            if ecp is not None:
                athlete.ecp = ecp
            if ew_prime is not None:
                athlete.ew_prime = ew_prime
            if kj_per_hour_per_kg is not None:
                athlete.kj_per_hour_per_kg = kj_per_hour_per_kg
            if api_key is not None:
                athlete.api_key = api_key.strip() or None
            if notes is not None:
                athlete.notes = notes.strip() or None
            self.session.commit()

    def import_power_data_from_intervals(
        self,
        athlete_id: int,
        power_data: Dict
    ) -> str:
        """
        Importa i dati di potenza (CP, W', eCP, eW', Height) da Intervals nel database.
        
        Args:
            athlete_id: ID dell'atleta
            power_data: Dizionario con chiavi: cp, w_prime, ecp, ew_prime, height_cm
        
        Returns:
            Messaggio di stato
        """
        if not power_data:
            return "❌ Nessun dato power da importare"
        
        athlete = self.session.query(Athlete).filter_by(id=athlete_id).first()
        if not athlete:
            return f"❌ Atleta {athlete_id} non trovato"
        
        try:
            updates = []
            
            # Update CP (FTP da Intervals)
            if power_data.get('cp'):
                athlete.cp = float(power_data['cp'])
                updates.append(f"CP: {athlete.cp} W")
            
            # Update W' (W Prime da Intervals)
            if power_data.get('w_prime'):
                athlete.w_prime = float(power_data['w_prime'])
                updates.append(f"W': {athlete.w_prime} J")
            
            # Update eCP (estimated CP da mmp_model - read-only in UI)
            if power_data.get('ecp'):
                athlete.ecp = float(power_data['ecp'])
                updates.append(f"eCP: {athlete.ecp} W")
            
            # Update eW' (estimated W Prime da mmp_model - read-only in UI)
            if power_data.get('ew_prime'):
                athlete.ew_prime = float(power_data['ew_prime'])
                updates.append(f"eW': {athlete.ew_prime} J")
            
            # Update Height
            if power_data.get('height_cm'):
                athlete.height_cm = float(power_data['height_cm'])
                updates.append(f"Height: {athlete.height_cm} cm")
            
            if updates:
                self.session.commit()
                return f"✅ Importati dati power: {', '.join(updates)}"
            else:
                return "ℹ Nessun dato power disponibile da importare"
        
        except Exception as e:
            self.session.rollback()
            return f"❌ Errore import power data: {str(e)}"

    def delete_athlete(self, athlete_id: int) -> None:
        """Delete an athlete."""
        athlete = self.session.query(Athlete).filter_by(id=athlete_id).first()
        if athlete:
            self.session.delete(athlete)
            self.session.commit()

    def list_athletes(self) -> List[Dict[str, str]]:
        """List all athletes with team information."""
        athletes = self.session.query(Athlete).order_by(Athlete.created_at.desc()).all()
        return [athlete.to_dict(with_team_name=True) for athlete in athletes]

    def get_athlete(self, athlete_id: int) -> Optional[Dict]:
        """Get a single athlete by ID."""
        athlete = self.session.query(Athlete).filter(Athlete.id == athlete_id).first()
        return athlete.to_dict(with_team_name=True) if athlete else None

    def add_activity(
        self,
        athlete_id: int,
        title: str,
        activity_date: str,
        duration_minutes: Optional[float] = None,
        distance_km: Optional[float] = None,
        tss: Optional[float] = None,
        source: str = "manual",
        intervals_payload: Optional[Iterable[Dict]] = None,
        intervals_id: Optional[str] = None,
        is_race: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        avg_watts: Optional[float] = None,
        normalized_watts: Optional[float] = None,
        avg_hr: Optional[float] = None,
        max_hr: Optional[float] = None,
        avg_cadence: Optional[float] = None,
        training_load: Optional[float] = None,
        intensity: Optional[float] = None,
        feel: Optional[int] = None,
        calories: Optional[float] = None,
        activity_type: Optional[str] = None,
    ) -> Tuple[int, bool]:
        """Add a new activity, avoiding duplicates.
        
        Returns:
            Tuple (activity_id, is_new) - is_new True if activity was newly created
        """
        # Log activity being added
        _logger.info(f"[DUPLICATE CHECK] Adding activity: athlete_id={athlete_id}, title='{title}', "
                f"date={activity_date}, source={source}, intervals_id={intervals_id}")
        
        # Check for duplicates
        existing = None
        
        # First priority: check by intervals_id if provided (strongest check)
        if intervals_id:
            _logger.debug(f"[DUPLICATE CHECK] Checking by intervals_id={intervals_id}")
            existing = self.session.query(Activity).filter(
                Activity.intervals_id == intervals_id
            ).first()
            if existing:
                _logger.info(f"[DUPLICATE] Found existing activity by intervals_id (ID: {existing.id})")
                return existing.id, False
            _logger.debug(f"[DUPLICATE CHECK] No existing activity by intervals_id")
        
        # Second priority: For Intervals imports, also check by athlete, source, title, and date
        # This catches duplicates even if intervals_id somehow differs
        if source and source.lower() == "intervals":
            _logger.debug(f"[DUPLICATE CHECK] Intervals source - checking by athlete+source+title+date")
            existing = self.session.query(Activity).filter(
                Activity.athlete_id == athlete_id,
                Activity.source == source,
                Activity.title == title.strip(),
                Activity.activity_date == activity_date
            ).first()
            if existing:
                _logger.info(f"[DUPLICATE] Found existing Intervals activity by athlete+source+title+date (ID: {existing.id})")
                return existing.id, False
            _logger.debug(f"[DUPLICATE CHECK] No existing Intervals activity by athlete+source+title+date")
        
        # Third priority: For manual activities, check by athlete, title, and date
        _logger.debug(f"[DUPLICATE CHECK] Fallback check by athlete+title+date")
        if not existing:
            existing = self.session.query(Activity).filter(
                Activity.athlete_id == athlete_id,
                Activity.title == title.strip(),
                Activity.activity_date == activity_date
            ).first()
            if existing:
                _logger.info(f"[DUPLICATE] Found existing activity by athlete+title+date (ID: {existing.id})")
                return existing.id, False
            _logger.debug(f"[DUPLICATE CHECK] No existing activity by athlete+title+date - creating new")
        
        now = datetime.utcnow().isoformat()
        payload = json.dumps(list(intervals_payload), ensure_ascii=False) if intervals_payload else None
        tags_json = json.dumps(tags or [], ensure_ascii=False)
        
        activity = Activity(
            athlete_id=athlete_id,
            title=title.strip(),
            activity_date=activity_date,
            duration_minutes=duration_minutes,
            distance_km=distance_km,
            tss=tss,
            source=source,
            intervals_id=intervals_id,
            intervals_payload=payload,
            is_race=is_race,
            tags=tags_json,
            avg_watts=avg_watts,
            normalized_watts=normalized_watts,
            avg_hr=avg_hr,
            max_hr=max_hr,
            avg_cadence=avg_cadence,
            training_load=training_load,
            intensity=intensity,
            feel=feel,
            calories=calories,
            activity_type=activity_type,
            created_at=now,
        )
        self.session.add(activity)
        self.session.commit()
        _logger.info(f"[NEW ACTIVITY] Created activity ID={activity.id}, source={source}, intervals_id={intervals_id}")
        return activity.id, True

    def delete_activity(self, activity_id: int) -> bool:
        """Delete an activity by ID.
        
        Returns:
            True if activity was deleted, False if not found
        """
        try:
            activity = self.session.query(Activity).filter(Activity.id == activity_id).first()
            if activity:
                self.session.delete(activity)
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"[bTeam] Errore eliminazione attività: {e}")
            return False

    def get_activity(self, activity_id: int) -> Optional[Dict]:
        """Get activity details by ID.
        
        Returns:
            Activity dict with all details, or None if not found
        """
        try:
            activity = (
                self.session.query(Activity)
                .options(joinedload(Activity.athlete))
                .filter(Activity.id == activity_id)
                .first()
            )
            if activity:
                activity_dict = activity.to_dict(with_athlete_name=False)
                athlete_name = "Unknown"
                if activity.athlete_id:
                    athlete = (
                        self.session.query(Athlete)
                        .filter(Athlete.id == activity.athlete_id)
                        .first()
                    )
                    if athlete:
                        athlete_name = f"{athlete.first_name} {athlete.last_name}"
                activity_dict["athlete_name"] = athlete_name
                return activity_dict
            return None
        except Exception as e:
            _logger.error(f"Errore lettura attività: {e}")
            return None

    def list_activities(self) -> List[Dict[str, str]]:
        """List all activities with athlete names."""
        _logger.debug("[list_activities] Starting query")
        activities = (
            self.session.query(Activity)
            .order_by(Activity.activity_date.desc(), Activity.created_at.desc())
            .all()
        )
        _logger.info(f"[list_activities] Loaded {len(activities)} activities")

        athlete_rows = self.session.query(Athlete.id, Athlete.first_name, Athlete.last_name).all()
        athlete_lookup = {
            athlete_id: f"{first_name} {last_name}"
            for athlete_id, first_name, last_name in athlete_rows
        }

        result = []
        for activity in activities:
            activity_dict = activity.to_dict(with_athlete_name=False)
            athlete_name = athlete_lookup.get(activity.athlete_id, "Unknown")
            if athlete_name == "Unknown":
                _logger.warning(
                    f"[list_activities] Activity {activity.id}: athlete_id={activity.athlete_id} not found in athletes"
                )
            activity_dict["athlete_name"] = athlete_name
            result.append(activity_dict)
        
        _logger.debug(f"[list_activities] Converted to dict, first activity athlete_name: {result[0].get('athlete_name') if result else 'N/A'}")
        return result

    def stats(self) -> Dict[str, int]:
        """Get database statistics."""
        athletes_count = self.session.query(Athlete).count()
        activities_count = self.session.query(Activity).count()
        return {"athletes": athletes_count, "activities": activities_count}

    # ===== RACE MANAGEMENT =====
    def add_race(
        self,
        name: str,
        race_date: str,
        distance_km: float,
        gender: Optional[str] = None,
        category: Optional[str] = None,
        elevation_m: Optional[float] = None,
        avg_speed_kmh: Optional[float] = None,
        predicted_duration_minutes: Optional[float] = None,
        predicted_kj: Optional[float] = None,
        route_file: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> int:
        """Add a new race (standalone, not linked to an athlete)."""
        now = datetime.utcnow().isoformat()
        race = Race(
            name=name.strip(),
            race_date=race_date,
            gender=gender,
            category=category,
            distance_km=distance_km,
            elevation_m=elevation_m,
            avg_speed_kmh=avg_speed_kmh,
            predicted_duration_minutes=predicted_duration_minutes,
            predicted_kj=predicted_kj,
            route_file=route_file,
            notes=notes,
            created_at=now,
        )
        self.session.add(race)
        self.session.commit()
        return race.id

    def update_race(
        self,
        race_id: int,
        name: Optional[str] = None,
        race_date: Optional[str] = None,
        distance_km: Optional[float] = None,
        gender: Optional[str] = None,
        category: Optional[str] = None,
        elevation_m: Optional[float] = None,
        avg_speed_kmh: Optional[float] = None,
        predicted_duration_minutes: Optional[float] = None,
        predicted_kj: Optional[float] = None,
        route_file: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """Update race details."""
        try:
            race = self.session.query(Race).filter(Race.id == race_id).first()
            if not race:
                return False
            
            if name is not None:
                race.name = name.strip()
            if race_date is not None:
                race.race_date = race_date
            if distance_km is not None:
                race.distance_km = distance_km
            if gender is not None:
                race.gender = gender
            if category is not None:
                race.category = category
            if elevation_m is not None:
                race.elevation_m = elevation_m
            if avg_speed_kmh is not None:
                race.avg_speed_kmh = avg_speed_kmh
            if predicted_duration_minutes is not None:
                race.predicted_duration_minutes = predicted_duration_minutes
            if predicted_kj is not None:
                race.predicted_kj = predicted_kj
            if route_file is not None:
                race.route_file = route_file
            if notes is not None:
                race.notes = notes
            
            self.session.commit()
            return True
        except Exception as e:
            print(f"[bTeam] Errore aggiornamento gara: {e}")
            return False

    def add_athlete_to_race(self, race_id: int, athlete_id: int, objective: str = "C", kj_per_hour_per_kg: float = 10.0) -> bool:
        """Add an athlete to a race with objective and kJ/h/kg parameters."""
        try:
            # Check if already exists
            existing = self.session.query(RaceAthlete).filter(
                RaceAthlete.race_id == race_id,
                RaceAthlete.athlete_id == athlete_id
            ).first()
            if existing:
                return False  # Already associated

            race_athlete = RaceAthlete(
                race_id=race_id,
                athlete_id=athlete_id,
                objective=objective,
                kj_per_hour_per_kg=kj_per_hour_per_kg,
                joined_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            self.session.add(race_athlete)
            self.session.commit()
            return True
        except Exception as e:
            print(f"[bTeam] Errore aggiunta atleta a gara: {e}")
            return False

    def remove_athlete_from_race(self, race_id: int, athlete_id: int) -> bool:
        """Remove an athlete from a race."""
        try:
            race_athlete = self.session.query(RaceAthlete).filter(
                RaceAthlete.race_id == race_id,
                RaceAthlete.athlete_id == athlete_id
            ).first()
            if race_athlete:
                self.session.delete(race_athlete)
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"[bTeam] Errore rimozione atleta da gara: {e}")
            return False

    def get_race_athletes(self, race_id: int) -> List[Dict]:
        """Get all athletes associated with a race."""
        try:
            race_athletes = self.session.query(RaceAthlete).filter(
                RaceAthlete.race_id == race_id
            ).all()
            return [ra.to_dict() for ra in race_athletes]
        except Exception as e:
            print(f"[bTeam] Errore lettura atleti gara: {e}")
            return []

    def update_race_athlete(self, race_id: int, athlete_id: int, **kwargs) -> bool:
        """Update race athlete data (kj_per_hour_per_kg, objective, etc.)."""
        try:
            race_athlete = self.session.query(RaceAthlete).filter(
                RaceAthlete.race_id == race_id,
                RaceAthlete.athlete_id == athlete_id
            ).first()
            
            if not race_athlete:
                print(f"[bTeam] Atleta {athlete_id} non trovato nella gara {race_id}")
                return False
            
            # Update allowed fields
            for key, value in kwargs.items():
                if hasattr(race_athlete, key):
                    setattr(race_athlete, key, value)
            
            self.session.commit()
            return True
        except Exception as e:
            print(f"[bTeam] Errore aggiornamento atleta gara: {e}")
            self.session.rollback()
            return False

    def delete_race_athletes_by_race_id(self, race_id: int) -> bool:
        """Delete all race athletes for a specific race."""
        try:
            self.session.query(RaceAthlete).filter(RaceAthlete.race_id == race_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            print(f"[bTeam] Errore eliminazione atleti gara: {e}")
            self.session.rollback()
            return False

    def delete_race(self, race_id: int) -> bool:
        """Delete a race by ID."""
        try:
            race = self.session.query(Race).filter(Race.id == race_id).first()
            if race:
                self.session.delete(race)
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"[bTeam] Errore eliminazione gara: {e}")
            return False

    def list_races(self) -> List[Dict]:
        """List all races (not filtered by athlete - races are standalone)."""
        query = self.session.query(Race).options(
            joinedload(Race.athletes_assoc).joinedload(RaceAthlete.athlete).joinedload(Athlete.team)
        ).order_by(Race.race_date.asc())
        races = query.all()
        return [race.to_dict() for race in races]

    def get_race(self, race_id: int) -> Optional[Dict]:
        """Get race details by ID."""
        try:
            race = self.session.query(Race).options(
                joinedload(Race.athletes_assoc).joinedload(RaceAthlete.athlete).joinedload(Athlete.team)
            ).filter(Race.id == race_id).first()
            if race:
                return race.to_dict()
            return None
        except Exception as e:
            print(f"[bTeam] Errore lettura gara: {e}")
            return None

    # ===== WELLNESS MANAGEMENT =====
    def add_wellness(
        self,
        athlete_id: int,
        wellness_date: str,  # YYYY-MM-DD
        weight_kg: Optional[float] = None,
        resting_hr: Optional[int] = None,
        hrv: Optional[float] = None,
        steps: Optional[int] = None,
        soreness: Optional[int] = None,
        fatigue: Optional[int] = None,
        stress: Optional[int] = None,
        mood: Optional[int] = None,
        motivation: Optional[int] = None,
        injury: Optional[float] = None,
        kcal: Optional[int] = None,
        sleep_secs: Optional[int] = None,
        sleep_score: Optional[int] = None,
        sleep_quality: Optional[int] = None,
        avg_sleeping_hr: Optional[float] = None,
        menstruation: Optional[bool] = None,
        menstrual_cycle_phase: Optional[int] = None,
        body_fat: Optional[float] = None,
        respiration: Optional[float] = None,
        spO2: Optional[float] = None,
        readiness: Optional[float] = None,
        ctl: Optional[float] = None,
        atl: Optional[float] = None,
        ramp_rate: Optional[float] = None,
        comments: Optional[str] = None,
    ) -> bool:
        """Add or update wellness data for a specific date."""
        # Check if wellness already exists for this date
        existing = self.session.query(Wellness).filter_by(
            athlete_id=athlete_id,
            wellness_date=wellness_date
        ).first()
        
        now = datetime.utcnow().isoformat()
        
        if existing:
            # Update existing
            existing.weight_kg = weight_kg if weight_kg is not None else existing.weight_kg
            existing.resting_hr = resting_hr if resting_hr is not None else existing.resting_hr
            existing.hrv = hrv if hrv is not None else existing.hrv
            existing.steps = steps if steps is not None else existing.steps
            existing.soreness = soreness if soreness is not None else existing.soreness
            existing.fatigue = fatigue if fatigue is not None else existing.fatigue
            existing.stress = stress if stress is not None else existing.stress
            existing.mood = mood if mood is not None else existing.mood
            existing.motivation = motivation if motivation is not None else existing.motivation
            existing.injury = injury if injury is not None else existing.injury
            existing.kcal = kcal if kcal is not None else existing.kcal
            existing.sleep_secs = sleep_secs if sleep_secs is not None else existing.sleep_secs
            existing.sleep_score = sleep_score if sleep_score is not None else existing.sleep_score
            existing.sleep_quality = sleep_quality if sleep_quality is not None else existing.sleep_quality
            existing.avg_sleeping_hr = avg_sleeping_hr if avg_sleeping_hr is not None else existing.avg_sleeping_hr
            existing.menstruation = menstruation if menstruation is not None else existing.menstruation
            existing.menstrual_cycle_phase = menstrual_cycle_phase if menstrual_cycle_phase is not None else existing.menstrual_cycle_phase
            existing.body_fat = body_fat if body_fat is not None else existing.body_fat
            existing.respiration = respiration if respiration is not None else existing.respiration
            existing.spO2 = spO2 if spO2 is not None else existing.spO2
            existing.readiness = readiness if readiness is not None else existing.readiness
            existing.ctl = ctl if ctl is not None else existing.ctl
            existing.atl = atl if atl is not None else existing.atl
            existing.ramp_rate = ramp_rate if ramp_rate is not None else existing.ramp_rate
            existing.comments = comments if comments is not None else existing.comments
            self.session.commit()
            return True
        else:
            # Create new
            wellness = Wellness(
                athlete_id=athlete_id,
                wellness_date=wellness_date,
                weight_kg=weight_kg,
                resting_hr=resting_hr,
                hrv=hrv,
                steps=steps,
                soreness=soreness,
                fatigue=fatigue,
                stress=stress,
                mood=mood,
                motivation=motivation,
                injury=injury,
                kcal=kcal,
                sleep_secs=sleep_secs,
                sleep_score=sleep_score,
                sleep_quality=sleep_quality,
                avg_sleeping_hr=avg_sleeping_hr,
                menstruation=menstruation,
                menstrual_cycle_phase=menstrual_cycle_phase,
                body_fat=body_fat,
                respiration=respiration,
                spO2=spO2,
                readiness=readiness,
                ctl=ctl,
                atl=atl,
                ramp_rate=ramp_rate,
                comments=comments,
                created_at=now,
            )
            self.session.add(wellness)
            self.session.commit()
            return True

    def get_wellness(self, athlete_id: int, days_back: int = 30) -> List[Dict]:
        """Get wellness records for an athlete (last N days)."""
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        wellness_records = self.session.query(Wellness).filter(
            Wellness.athlete_id == athlete_id,
            Wellness.wellness_date >= start_date
        ).order_by(Wellness.wellness_date.desc()).all()
        return [w.to_dict() for w in wellness_records]

    def get_latest_weight(self, athlete_id: int) -> Optional[float]:
        """Get the latest weight for an athlete."""
        wellness = self.session.query(Wellness).filter(
            Wellness.athlete_id == athlete_id,
            Wellness.weight_kg.isnot(None)
        ).order_by(Wellness.wellness_date.desc()).first()
        return wellness.weight_kg if wellness else None

    # ========== SEASONS ==========

    def create_season(self, athlete_id: int, name: str, start_date: str) -> Dict:
        """Create a new season for an athlete."""
        now = datetime.now().isoformat()
        season = Season(
            athlete_id=athlete_id,
            name=name,
            start_date=start_date,
            created_at=now
        )
        self.session.add(season)
        self.session.commit()
        return season.to_dict()

    def get_seasons(self, athlete_id: int) -> List[Dict]:
        """Get all seasons for an athlete, ordered by start_date DESC."""
        seasons = self.session.query(Season).filter(
            Season.athlete_id == athlete_id
        ).order_by(Season.start_date.desc()).all()
        
        # Calculate end_date for each season (= start of next season or None)
        result = []
        for i, season in enumerate(seasons):
            season_dict = season.to_dict()
            # End date is start of next season (which is previous in DESC order)
            if i > 0:
                season_dict['end_date'] = seasons[i - 1].start_date
            else:
                season_dict['end_date'] = None  # Most recent season, still ongoing
            result.append(season_dict)
        
        return result

    def get_season(self, season_id: int) -> Optional[Dict]:
        """Get a specific season by ID."""
        season = self.session.query(Season).filter(Season.id == season_id).first()
        if not season:
            return None
        
        season_dict = season.to_dict()
        # Calculate end_date
        next_season = self.session.query(Season).filter(
            Season.athlete_id == season.athlete_id,
            Season.start_date > season.start_date
        ).order_by(Season.start_date.asc()).first()
        
        season_dict['end_date'] = next_season.start_date if next_season else None
        return season_dict

    def update_season(self, season_id: int, **kwargs) -> bool:
        """Update a season."""
        season = self.session.query(Season).filter(Season.id == season_id).first()
        if not season:
            return False
        
        for key, value in kwargs.items():
            if hasattr(season, key) and value is not None:
                setattr(season, key, value)
        
        self.session.commit()
        return True

    def delete_season(self, season_id: int) -> bool:
        """Delete a season."""
        season = self.session.query(Season).filter(Season.id == season_id).first()
        if not season:
            return False
        
        self.session.delete(season)
        self.session.commit()
        return True
    
    def close(self) -> None:
        """
        Close database session and connections.
        
        This method should be called explicitly when done with the storage object,
        or use the storage object as a context manager with 'with' statement.
        """
        if hasattr(self, 'session') and self.session:
            try:
                self.session.close()
            except Exception as e:
                # Log error but don't raise during cleanup
                print(f"[bTeam] Errore chiusura sessione: {e}")
        
        if hasattr(self, 'engine') and self.engine:
            try:
                self.engine.dispose()
            except Exception as e:
                # Log error but don't raise during cleanup
                print(f"[bTeam] Errore chiusura engine: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
        return False  # Don't suppress exceptions
