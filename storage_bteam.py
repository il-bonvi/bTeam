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
from typing import Dict, Iterable, List, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float, create_engine
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
    duration_minutes = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=True)
    tss = Column(Float, nullable=True)
    source = Column(String(255), nullable=True)
    intervals_payload = Column(Text, nullable=True)
    created_at = Column(String(255), nullable=False)

    athlete = relationship("Athlete", back_populates="activities")

    def to_dict(self, with_athlete_name: bool = True) -> Dict:
        data = {
            "id": self.id,
            "athlete_id": self.athlete_id,
            "title": self.title,
            "activity_date": self.activity_date,
            "duration_minutes": self.duration_minutes,
            "distance_km": self.distance_km,
            "tss": self.tss,
            "source": self.source,
            "intervals_payload": self.intervals_payload,
            "created_at": self.created_at,
        }
        if with_athlete_name:
            athlete_name = f"{self.athlete.first_name} {self.athlete.last_name}" if self.athlete else "Unknown"
            data["athlete_name"] = athlete_name
        return data


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
            except Exception as e:
                print(f"[bTeam] Errore check schema: {e}")
                try:
                    self.db_path.unlink()
                except (OSError, PermissionError):
                    pass

        # Initialize SQLAlchemy engine and session
        db_url = f"sqlite:///{self.db_path.as_posix()}"
        self.engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        
        SessionLocal = sessionmaker(bind=self.engine)
        self.session: SQLAlchemySession = SessionLocal()

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
    ) -> int:
        """Add a new activity."""
        now = datetime.utcnow().isoformat()
        payload = json.dumps(list(intervals_payload), ensure_ascii=False) if intervals_payload else None
        activity = Activity(
            athlete_id=athlete_id,
            title=title.strip(),
            activity_date=activity_date,
            duration_minutes=duration_minutes,
            distance_km=distance_km,
            tss=tss,
            source=source,
            intervals_payload=payload,
            created_at=now,
        )
        self.session.add(activity)
        self.session.commit()
        return activity.id

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

    def close(self) -> None:
        """Close the database session."""
        self.session.close()
