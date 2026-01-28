# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session as SQLAlchemySession


Base = declarative_base()


class Team(Base):
    """SQLAlchemy ORM model for teams."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(String(255), nullable=False)

    athletes = relationship("Athlete", back_populates="team", cascade="all, delete-orphan")

    def to_dict(self) -> Dict:
        return {"id": self.id, "name": self.name, "created_at": self.created_at}


class Athlete(Base):
    """SQLAlchemy ORM model for athletes."""
    __tablename__ = "athletes"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    birth_date = Column(String(255), nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    cp = Column(Float, nullable=True)
    w_prime = Column(Float, nullable=True)
    kj_per_hour_per_kg = Column(Float, default=1.0)  # KJ/h/kg per calcoli gare
    api_key = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(String(255), nullable=False)

    team = relationship("Team", back_populates="athletes")
    activities = relationship("Activity", back_populates="athlete", cascade="all, delete-orphan")

    def to_dict(self, with_team_name: bool = True) -> Dict:
        data = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "team_id": self.team_id,
            "birth_date": self.birth_date,
            "weight_kg": self.weight_kg,
            "height_cm": self.height_cm,
            "cp": self.cp,
            "w_prime": self.w_prime,
            "kj_per_hour_per_kg": self.kj_per_hour_per_kg,
            "api_key": self.api_key,
            "notes": self.notes,
            "created_at": self.created_at,
        }
        if with_team_name:
            data["team_name"] = self.team.name if self.team else None
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

    def to_dict(self, with_athlete_name: bool = True) -> Dict:
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
        if with_athlete_name:
            athlete_name = f"{self.athlete.first_name} {self.athlete.last_name}" if self.athlete else "Unknown"
            data["athlete_name"] = athlete_name
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
    joined_at = Column(String(255), nullable=False)

    race = relationship("Race", back_populates="athletes_assoc")
    athlete = relationship("Athlete", foreign_keys=[athlete_id])

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "race_id": self.race_id,
            "athlete_id": self.athlete_id,
            "athlete_name": f"{self.athlete.first_name} {self.athlete.last_name}" if self.athlete else "Unknown",
            "joined_at": self.joined_at,
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
        athletes = [{"id": ra.athlete_id, "name": f"{ra.athlete.first_name} {ra.athlete.last_name}"} for ra in self.athletes_assoc]
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

        # Check for obsolete schema and delete if needed
        if self.db_path.exists():
            try:
                test_conn = sqlite3.connect(self.db_path)
                test_cur = test_conn.cursor()
                test_cur.execute("PRAGMA table_info(athletes)")
                cols_data = test_cur.fetchall()
                test_conn.close()

                cols = [row[1] for row in cols_data] if cols_data else []
                if cols and "name" in cols:
                    print("[bTeam] Schema obsoleto rilevato, eliminazione database...")
                    self.db_path.unlink()
            except (sqlite3.Error, OSError) as e:
                print(f"[bTeam] Errore check schema: {e}")
                try:
                    self.db_path.unlink()
                except (OSError, PermissionError):
                    pass

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
                    cursor.execute("ALTER TABLE athletes ADD COLUMN kj_per_hour_per_kg REAL DEFAULT 1.0")
                    print(f"[bTeam] Colonna 'kj_per_hour_per_kg' aggiunta alla tabella athletes")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"[bTeam] Errore aggiunta colonna 'kj_per_hour_per_kg': {e}")
            
            # Check if races table exists and if it has old athlete_id column
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
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[bTeam] Errore migrazione schema: {e}")

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

    def add_athlete(
        self,
        first_name: str,
        last_name: str,
        team_id: Optional[int] = None,
        birth_date: str = "",
        weight_kg: Optional[float] = None,
        height_cm: Optional[float] = None,
        cp: Optional[float] = None,
        w_prime: Optional[float] = None,
        notes: str = "",
    ) -> int:
        """Add a new athlete."""
        now = datetime.utcnow().isoformat()
        athlete = Athlete(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            team_id=team_id,
            birth_date=birth_date.strip() or None,
            weight_kg=weight_kg,
            height_cm=height_cm,
            cp=cp,
            w_prime=w_prime,
            notes=notes.strip() or None,
            created_at=now,
        )
        self.session.add(athlete)
        self.session.commit()
        return athlete.id

    def update_athlete(
        self,
        athlete_id: int,
        birth_date: str = "",
        weight_kg: Optional[float] = None,
        height_cm: Optional[float] = None,
        cp: Optional[float] = None,
        w_prime: Optional[float] = None,
        kj_per_hour_per_kg: Optional[float] = None,
        api_key: str = "",
        notes: str = "",
    ) -> None:
        """Update athlete details."""
        athlete = self.session.query(Athlete).filter_by(id=athlete_id).first()
        if athlete:
            athlete.birth_date = birth_date.strip() or None
            athlete.weight_kg = weight_kg
            athlete.height_cm = height_cm
            athlete.cp = cp
            athlete.w_prime = w_prime
            athlete.kj_per_hour_per_kg = kj_per_hour_per_kg or 1.0
            athlete.api_key = api_key.strip() or None
            athlete.notes = notes.strip() or None
            self.session.commit()

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
        """Add a new activity, avoiding duplicates for Intervals imports.
        
        Returns:
            Tuple (activity_id, is_new) - is_new True if activity was newly created
        """
        # Controlla se l'attività da Intervals esiste già
        if source == "intervals" and intervals_id:
            existing = self.session.query(Activity).filter(
                Activity.athlete_id == athlete_id,
                Activity.source == "intervals",
                Activity.title == title.strip(),
                Activity.activity_date == activity_date
            ).first()
            
            if existing:
                # Attività già esiste, non aggiungere duplicato
                return existing.id, False
        
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
            activity = self.session.query(Activity).filter(Activity.id == activity_id).first()
            if activity:
                return activity.to_dict(with_athlete_name=True)
            return None
        except Exception as e:
            print(f"[bTeam] Errore lettura attività: {e}")
            return None
        except Exception as e:
            print(f"[bTeam] Errore eliminazione attività: {e}")
            return False

    def list_activities(self) -> List[Dict[str, str]]:
        """List all activities with athlete names."""
        activities = (
            self.session.query(Activity)
            .order_by(Activity.activity_date.desc(), Activity.created_at.desc())
            .all()
        )
        return [activity.to_dict(with_athlete_name=True) for activity in activities]

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

    def add_athlete_to_race(self, race_id: int, athlete_id: int) -> bool:
        """Add an athlete to a race."""
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
        query = self.session.query(Race).order_by(Race.race_date.asc())
        races = query.all()
        return [race.to_dict() for race in races]

    def get_race(self, race_id: int) -> Optional[Dict]:
        """Get race details by ID."""
        try:
            race = self.session.query(Race).filter(Race.id == race_id).first()
            if race:
                return race.to_dict()
            return None
        except Exception as e:
            print(f"[bTeam] Errore lettura gara: {e}")
            return None

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
