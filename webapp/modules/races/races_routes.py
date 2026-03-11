"""Races API Routes"""

import re
import requests
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from typing import Optional, List

from shared.storage import get_storage
from shared.intervals.client import IntervalsAPIClient

router = APIRouter()


class BonviRaceLink(BaseModel):
    """Model for bonvi race database link"""
    link: str


class RaceCreate(BaseModel):
    name: str
    race_date_start: str
    race_date_end: str
    distance_km: Optional[float] = None
    num_stages: int = 1
    gender: Optional[str] = None
    category: Optional[str] = None
    elevation_m: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    predicted_duration_minutes: Optional[float] = None
    predicted_kj: Optional[float] = None
    route_file: Optional[str] = None
    route_link: Optional[str] = None
    notes: Optional[str] = None
    stage_links: Optional[List[str]] = None  # Auto-generated stage links from bonvi-race-database
    stages_data: Optional[List[dict]] = None  # Per-stage details: distance, elevation, date, route_link


class RaceAthleteAdd(BaseModel):
    athlete_id: int
    kj_per_hour_per_kg: float = 10.0
    objective: str = "C"


class StageUpdate(BaseModel):
    distance_km: Optional[float] = None
    elevation_m: Optional[float] = None
    route_file: Optional[str] = None
    route_link: Optional[str] = None
    notes: Optional[str] = None
    stage_date: Optional[str] = None
    avg_speed_kmh: Optional[float] = None


class StageCreate(BaseModel):
    distance_km: float
    elevation_m: Optional[float] = None
    route_file: Optional[str] = None
    route_link: Optional[str] = None
    notes: Optional[str] = None
    stage_date: Optional[str] = None
    avg_speed_kmh: Optional[float] = None


class LinkActivityRequest(BaseModel):
    athlete_id: int
    intervals_activity_id: str
    race_name: str  # The race name for matching/display


def _parse_bonvi_html(html: str, url_slug: str, month_map: dict) -> dict:
    """Shared HTML parsing helper for bonvi-race-database pages.

    Dates on the page appear WITHOUT a year (e.g. '14 ago'), so we extract
    the year from the URL slug (e.g. 'bizkaikoloreak-2025-DJ' → 2025).
    """
    race_name = None
    name_match = re.search(r'<span class="bar-title"[^>]*>([^<]+)</span>', html)
    if name_match:
        race_name = name_match.group(1).strip()

    # Priority 1: look for distance in <title> or <meta> (reliable, before any scripts/base64)
    distance: Optional[float] = None
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    title_text = title_match.group(1) if title_match else ''
    dist_in_title = re.search(r'(\d+(?:[.,]\d+)?)\s*km', title_text, re.IGNORECASE)
    if dist_in_title:
        distance = float(dist_in_title.group(1).replace(',', '.'))
    else:
        # Priority 2: look inside data-* attributes (e.g. bstat-v)
        bstat_dist = re.search(r'data-[^>]*>(\d+(?:[.,]\d+)?)\s*km<', html, re.IGNORECASE)
        if bstat_dist:
            distance = float(bstat_dist.group(1).replace(',', '.'))
        else:
            # Fallback: first plain match (may catch junk in base64, acceptable for stage pages)
            dist_fallback = re.search(r'>(\d+(?:[.,]\d+)?)\s*km<', html, re.IGNORECASE)
            if dist_fallback:
                distance = float(dist_fallback.group(1).replace(',', '.'))

    # Elevation: prefer structured tags, then bare +N m
    elevation: Optional[float] = None
    elev_in_tag = re.search(r'>\+(\d+(?:[.,]\d+)?)\s*m\s*<', html, re.IGNORECASE)
    if elev_in_tag:
        elevation = float(elev_in_tag.group(1).replace(',', '.'))
    else:
        elev_bare = re.search(r'\+(\d+(?:[.,]\d+)?)\s*m\b', html, re.IGNORECASE)
        if elev_bare:
            elevation = float(elev_bare.group(1).replace(',', '.'))

    # Year is in the slug (e.g. '-2025-'), NOT in the page body
    year_match = re.search(r'-(\d{4})-', url_slug)
    year = year_match.group(1) if year_match else str(datetime.now().year)

    months_pattern = '|'.join(month_map.keys())
    # Dates appear as "14 ago" without year
    date_matches = list(re.finditer(
        r'(\d{1,2})\s+(' + months_pattern + r')\b', html, re.IGNORECASE
    ))

    def _fmt_date(m):
        return f"{year}-{month_map[m.group(2).lower()]}-{m.group(1).zfill(2)}"

    # Deduplicate while preserving order
    seen = set()
    dates = []
    for m in date_matches:
        d = _fmt_date(m)
        if d not in seen:
            seen.add(d)
            dates.append(d)

    return {
        "name": race_name,
        "distance": distance,
        "elevation": elevation,
        "dates": dates,
    }


@router.post("/load-from-bonvi")
async def load_from_bonvi(data: BonviRaceLink):
    """Load race data from bonvi-race-database.
    
    Auto-detects link type and returns:
    - link_type: "single_day" | "stage_race" | "single_stage"
    - For single_day: name, distance_km, elevation_m, race_date_start, route_link
    - For stage_race: name, race_date_start, race_date_end, num_stages, route_link
    - For single_stage: name, stage_number, stage_date, distance_km, elevation_m, route_link
    """
    try:
        link = data.link.strip()
        if not link.endswith('/'):
            link += '/'

        if "il-bonvi.github.io/bonvi-race-database/gare/" not in link:
            raise ValueError("Link non valido. Deve essere una gara da bonvi-race-database")

        url_slug = link.rstrip('/').split('/')[-1]

        response = await run_in_threadpool(requests.get, link, timeout=10)
        response.raise_for_status()
        html = response.text

        month_map = {
            'gen': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'mag': '05', 'giu': '06', 'lug': '07', 'ago': '08',
            'set': '09', 'ott': '10', 'nov': '11', 'dic': '12'
        }

        parsed = _parse_bonvi_html(html, url_slug, month_map)
        dates = parsed["dates"]

        # --- Detect link type ---
        stage_num_match = re.search(r'-S(\d+)-', url_slug, re.IGNORECASE)

        if stage_num_match:
            # ── Single stage link (e.g. bizkaikoloreak-S1-2025-DJ) ──
            stage_number = int(stage_num_match.group(1))
            stage_date = min(dates) if dates else None
            return {
                "link_type": "single_stage",
                "stage_number": stage_number,
                "name": parsed["name"],
                "stage_date": stage_date,
                "distance_km": parsed["distance"],
                "elevation_m": parsed["elevation"],
                "route_link": link,
            }
        else:
            # Detect stage race by looking for links to individual stages on the page
            stage_link_nums = set(
                int(m) for m in re.findall(r'-S(\d+)-', html, re.IGNORECASE)
            )
            is_stage_race = len(stage_link_nums) > 0

            if is_stage_race:
                # ── Complete stage race link ──
                num_stages = len(stage_link_nums)
                if num_stages == 0:
                    stages_text = re.search(r'(\d+)\s+tappe?', html, re.IGNORECASE)
                    num_stages = int(stages_text.group(1)) if stages_text else 1

                race_date_start = min(dates) if dates else None
                race_date_end = max(dates) if dates else None

                # Extract actual stage hrefs from the page HTML (reliable - avoids slug-order bugs)
                gh_base = "https://il-bonvi.github.io"
                found_hrefs = re.findall(r'href="(/bonvi-race-database/gare/[^"]+)"', html)
                stage_links_set: dict[int, str] = {}
                for h in found_hrefs:
                    sn = re.search(r'-S(\d+)-', h, re.IGNORECASE)
                    if sn:
                        n = int(sn.group(1))
                        full = gh_base + h if not h.startswith('http') else h
                        if not full.endswith('/'):
                            full += '/'
                        stage_links_set[n] = full

                stage_links = [stage_links_set[n] for n in sorted(stage_links_set.keys())]
                if not stage_links:
                    # Fallback: none found in HTML – use slug-based generation
                    base_slug = url_slug
                    parts = base_slug.rsplit('-', 1)
                    base_url2 = link.rsplit('/', 2)[0]
                    if len(parts) == 2:
                        for i in range(1, int(num_stages) + 1):
                            stage_links.append(f"{base_url2}/{parts[0]}-S{i}-{parts[1]}/")

                # Fetch each stage page and collect per-stage data
                stages_data = []
                for i, stage_link in enumerate(stage_links, 1):
                    try:
                        stage_resp = await run_in_threadpool(requests.get, stage_link, timeout=10)
                        stage_resp.raise_for_status()
                        stage_slug_i = stage_link.rstrip('/').split('/')[-1]
                        sp = _parse_bonvi_html(stage_resp.text, stage_slug_i, month_map)
                        stage_date = min(sp["dates"]) if sp["dates"] else None
                        stages_data.append({
                            "stage_number": i,
                            "distance_km": sp["distance"],
                            "elevation_m": sp["elevation"],
                            "stage_date": stage_date,
                            "route_link": stage_link,
                            "fetch_error": None,
                        })
                    except Exception as e:
                        stages_data.append({
                            "stage_number": i,
                            "distance_km": None,
                            "elevation_m": None,
                            "stage_date": None,
                            "route_link": stage_link,
                            "fetch_error": str(e),
                        })

                # Totals: always sum from stages (main page may not have them or may be unreliable)
                distances = [s["distance_km"] for s in stages_data if s["distance_km"]]
                elevations = [s["elevation_m"] for s in stages_data if s["elevation_m"]]
                total_distance = round(sum(distances), 2) if distances else parsed["distance"]
                total_elevation = round(sum(elevations), 2) if elevations else parsed["elevation"]

                return {
                    "link_type": "stage_race",
                    "name": parsed["name"],
                    "race_date_start": race_date_start,
                    "race_date_end": race_date_end,
                    "num_stages": len(stage_links) or num_stages,
                    "distance_km": total_distance,
                    "elevation_m": total_elevation,
                    "route_link": link,
                    "stage_links": stage_links,
                    "stages_data": stages_data,
                }
            else:
                # ── Single day race ──
                race_date = min(dates) if dates else None
                return {
                    "link_type": "single_day",
                    "name": parsed["name"],
                    "distance_km": parsed["distance"],
                    "elevation_m": parsed["elevation"],
                    "race_date_start": race_date,
                    "avg_speed_kmh": None,
                    "route_link": link,
                    "note": "Velocità media non estratta automaticamente. Consulta il visualizzatore su bonvi-race-database"
                }

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Errore nel caricamento della pagina: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel parsing dei dati: {str(e)}")


@router.get("/")
async def get_races():
    """Get all races"""
    return get_storage().list_races()


@router.get("/{race_id}")
async def get_race(race_id: int):
    """Get a specific race by ID"""
    race = get_storage().get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race


@router.post("/")
async def create_race(race: RaceCreate):
    """Create a new race"""
    try:
        storage = get_storage()
        race_id = storage.add_race(
            name=race.name,
            race_date_start=race.race_date_start,
            race_date_end=race.race_date_end,
            distance_km=race.distance_km,
            num_stages=race.num_stages,
            gender=race.gender,
            category=race.category,
            elevation_m=race.elevation_m,
            avg_speed_kmh=race.avg_speed_kmh,
            predicted_duration_minutes=race.predicted_duration_minutes,
            predicted_kj=race.predicted_kj,
            route_file=race.route_file,
            route_link=race.route_link,
            notes=race.notes
        )
        
        # Auto-assign per-stage data if stages_data is provided (from bonvi fetch)
        update_data = race.stages_data or []
        if not update_data and race.stage_links:
            # Fallback: only route_link available
            update_data = [{"stage_number": i + 1, "route_link": link} for i, link in enumerate(race.stage_links)]

        if update_data:
            created_race = storage.get_race(race_id)
            stages = created_race.get('stages', []) if isinstance(created_race, dict) else []
            stages_by_num = {s['stage_number']: s for s in stages}

            for sd in update_data:
                stage_num = sd.get('stage_number')
                matched = stages_by_num.get(stage_num)
                if matched:
                    storage.update_stage(
                        stage_id=matched['id'],
                        distance_km=sd.get('distance_km'),
                        elevation_m=sd.get('elevation_m'),
                        stage_date=sd.get('stage_date'),
                        route_link=sd.get('route_link'),
                        avg_speed_kmh=sd.get('avg_speed_kmh'),
                    )

        return storage.get_race(race_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{race_id}")
async def update_race(race_id: int, race: RaceCreate):
    """Update an existing race"""
    storage = get_storage()
    if not storage.get_race(race_id):
        raise HTTPException(status_code=404, detail="Race not found")

    try:
        storage.update_race(
            race_id=race_id,
            name=race.name,
            race_date_start=race.race_date_start,
            race_date_end=race.race_date_end,
            distance_km=race.distance_km,
            num_stages=race.num_stages,
            gender=race.gender,
            category=race.category,
            elevation_m=race.elevation_m,
            avg_speed_kmh=race.avg_speed_kmh,
            predicted_duration_minutes=race.predicted_duration_minutes,
            predicted_kj=race.predicted_kj,
            route_file=race.route_file,
            route_link=race.route_link,
            notes=race.notes
        )
        return storage.get_race(race_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{race_id}")
async def delete_race(race_id: int):
    """Delete a race"""
    storage = get_storage()
    if not storage.get_race(race_id):
        raise HTTPException(status_code=404, detail="Race not found")

    try:
        storage.delete_race(race_id)
        return {"message": "Race deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{race_id}/athletes")
async def add_athlete_to_race(race_id: int, athlete_data: RaceAthleteAdd):
    """Add an athlete to a race"""
    storage = get_storage()
    if not storage.get_race(race_id):
        raise HTTPException(status_code=404, detail="Race not found")
    if not storage.get_athlete(athlete_data.athlete_id):
        raise HTTPException(status_code=404, detail="Athlete not found")

    try:
        storage.add_athlete_to_race(
            race_id=race_id,
            athlete_id=athlete_data.athlete_id,
            kj_per_hour_per_kg=athlete_data.kj_per_hour_per_kg,
            objective=athlete_data.objective
        )
        return {"message": "Athlete added to race successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{race_id}/athletes/{athlete_id}")
async def update_athlete_in_race(race_id: int, athlete_id: int, athlete_data: RaceAthleteAdd):
    """Update athlete's objective and kJ value in a race"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        # Update the athlete's objective and kJ value using the proper storage method
        success = storage.update_race_athlete(
            race_id=race_id,
            athlete_id=athlete_id,
            objective=athlete_data.objective,
            kj_per_hour_per_kg=athlete_data.kj_per_hour_per_kg
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Athlete not found in this race")
        
        return {"message": "Athlete updated in race successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{race_id}/athletes/{athlete_id}")
async def remove_athlete_from_race(race_id: int, athlete_id: int):
    """Remove an athlete from a race"""
    try:
        get_storage().remove_athlete_from_race(race_id, athlete_id)
        return {"message": "Athlete removed from race successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{race_id}/athletes")
async def get_race_athletes(race_id: int):
    """Get all athletes for a race"""
    race = get_storage().get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race.get('athletes', [])


# ============ STAGE MANAGEMENT ENDPOINTS ============

@router.get("/{race_id}/stages")
async def get_race_stages(race_id: int):
    """Get all stages for a race"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        stages = storage.get_stages(race_id)
        response = []
        for stage in stages:
            response.append(stage.to_dict() if hasattr(stage, 'to_dict') else stage)  # type: ignore[union-attr]
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{race_id}/stages/{stage_id}")
async def get_stage(race_id: int, stage_id: int):
    """Get a specific stage by ID"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        stage = storage.get_stage(stage_id)
        if not stage:
            raise HTTPException(status_code=404, detail="Stage not found")
        return stage.to_dict() if hasattr(stage, 'to_dict') else stage  # type: ignore[union-attr]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{race_id}/stages")
async def create_stage(race_id: int, stage: StageCreate):
    """Create a new stage for a race"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        # Get current number of stages to determine next stage number
        current_stages = storage.get_stages(race_id)
        stage_number = len(current_stages) + 1
        
        # Add the new stage
        stage_id = storage.add_stage(
            race_id=race_id,
            stage_number=stage_number,
            distance_km=stage.distance_km,
            elevation_m=stage.elevation_m,
            route_file=stage.route_file,
            route_link=stage.route_link,
            notes=stage.notes
        )
        
        if stage_id is None:
            raise HTTPException(status_code=500, detail="Failed to create stage")
        new_stage = storage.get_stage(stage_id)
        return new_stage.to_dict() if hasattr(new_stage, 'to_dict') else new_stage  # type: ignore[union-attr]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{race_id}/stages/{stage_id}")
async def update_stage(race_id: int, stage_id: int, stage: StageUpdate):
    """Update a specific stage"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        existing_stage = storage.get_stage(stage_id)
        if not existing_stage:
            raise HTTPException(status_code=404, detail="Stage not found")
        
        # Update the stage with provided data
        storage.update_stage(
            stage_id=stage_id,
            distance_km=stage.distance_km,
            elevation_m=stage.elevation_m,
            route_file=stage.route_file,
            route_link=stage.route_link,
            notes=stage.notes,
            stage_date=stage.stage_date,
            avg_speed_kmh=stage.avg_speed_kmh
        )
        
        updated_stage = storage.get_stage(stage_id)
        return updated_stage.to_dict() if hasattr(updated_stage, 'to_dict') else updated_stage  # type: ignore[union-attr]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{race_id}/stages/{stage_id}")
async def delete_stage(race_id: int, stage_id: int):
    """Delete a specific stage"""
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        stage = storage.get_stage(stage_id)
        if not stage:
            raise HTTPException(status_code=404, detail="Stage not found")
        
        storage.delete_stage(stage_id)
        return {"message": "Stage deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ RACE ACTIVITY MATCHING ENDPOINTS ============

@router.post("/{race_id}/candidate-activities")
async def get_candidate_activities(race_id: int):
    """
    Fetch activities from Intervals for race day(s) for all race athletes.
    
    Returns candidate activities for each athlete with smart name matching:
    - Auto-matched: activity name ≈ race name (99.9% match)
    - Candidates: all activities from that day for manual selection
    """
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        race_date_start = race.get('race_date_start')
        race_name = race.get('name', '')
        
        if not race_date_start:
            raise HTTPException(status_code=400, detail="Race date not set")
        
        # Get all athletes in this race
        race_athletes = race.get('athletes', [])
        if not race_athletes:
            return {"message": "No athletes enrolled in this race", "candidates": {}}
        
        results = {}
        
        for ra in race_athletes:
            athlete_id = ra.get('id')
            athlete = storage.get_athlete(athlete_id)
            
            if not athlete or not athlete.get('api_key'):
                results[athlete_id] = {
                    "athlete_name": ra.get('last_name', '') + ' ' + ra.get('first_name', ''),
                    "error": "No Intervals API key configured"
                }
                continue
            
            try:
                # Fetch activities from Intervals for race day
                client = IntervalsAPIClient(api_key=athlete['api_key'])
                
                # Get activities for the race day (allow range for multi-day races)
                oldest = race_date_start  # YYYY-MM-DD
                newest = race.get('race_date_end', race_date_start)
                
                activities = client.get_activities(
                    athlete_id='0',  # Current user (authenticated by API key)
                    oldest=oldest,
                    newest=newest
                )
                
                if not activities:
                    results[athlete_id] = {
                        "athlete_name": ra.get('last_name', '') + ' ' + ra.get('first_name', ''),
                        "candidates": [],
                        "auto_matched": None
                    }
                    continue
                
                # Smart matching: find activity with name closest to race name
                def name_similarity(name1: str, name2: str) -> float:
                    """Simple similarity metric: count matching words"""
                    words1 = set(name1.lower().split())
                    words2 = set(name2.lower().split())
                    if not words1 or not words2:
                        return 0.0
                    matches = len(words1 & words2)
                    return matches / max(len(words1), len(words2))
                
                best_match = None
                best_similarity = 0.0
                
                for activity in activities:
                    activity_name = activity.get('name', '')
                    similarity = name_similarity(activity_name, race_name)
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = activity if similarity > 0.3 else None  # Threshold 30%
                
                # Format results
                candidates = [
                    {
                        "id": act.get('id'),
                        "name": act.get('name', 'Untitled'),
                        "date": str(act.get('start_date_local', ''))[:10],
                        "distance_km": act.get('distance'),
                        "avg_watts": round(act.get('average_watts', 0), 1) if act.get('average_watts') else None,
                        "avg_hr": round(act.get('average_heartrate', 0), 1) if act.get('average_heartrate') else None,
                        "moving_time_min": round((act.get('moving_time', 0) or 0) / 60, 1),
                    }
                    for act in activities
                ]
                
                auto_matched = None
                if best_match and best_similarity > 0.3:
                    auto_matched = {
                        "id": best_match.get('id'),
                        "name": best_match.get('name', 'Untitled'),
                        "similarity": round(best_similarity * 100, 1),
                    }
                
                results[athlete_id] = {
                    "athlete_name": ra.get('last_name', '') + ' ' + ra.get('first_name', ''),
                    "candidates": candidates,
                    "auto_matched": auto_matched
                }
                
            except Exception as e:
                results[athlete_id] = {
                    "athlete_name": ra.get('last_name', '') +  ' ' + ra.get('first_name', ''),
                    "error": f"Failed to fetch activities: {str(e)}"
                }
        
        return {"race_name": race_name, "race_date": race_date_start, "results": results}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching activities: {str(e)}")


@router.post("/{race_id}/link-activity")
async def link_activity(race_id: int, request: LinkActivityRequest):
    """
    Link an Intervals activity to a race athlete.
    
    Stores the mapping: race_id + athlete_id → intervals_activity_id
    The activity is fetched from Intervals on-demand when needed.
    """
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    athlete = storage.get_athlete(request.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    try:
        # Insert or update the race_activity link
        storage.link_race_activity(
            race_id=race_id,
            athlete_id=request.athlete_id,
            intervals_activity_id=request.intervals_activity_id,
            race_name=request.race_name
        )
        
        return {
            "message": "Activity linked successfully",
            "race_id": race_id,
            "athlete_id": request.athlete_id,
            "intervals_activity_id": request.intervals_activity_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error linking activity: {str(e)}")


@router.get("/{race_id}/athlete/{athlete_id}/linked-activity")
async def get_linked_activity(race_id: int, athlete_id: int):
    """
    Get the linked activity for a race athlete (if any).
    
    Returns the stored link info (race_name, intervals_activity_id).
    """
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    athlete = storage.get_athlete(athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    try:
        link = storage.get_race_activity(race_id, athlete_id)
        if not link:
            return {"linked": False, "message": "No activity linked for this athlete"}
        
        return {
            "linked": True,
            "race_id": race_id,
            "athlete_id": athlete_id,
            "intervals_activity_id": link.get('intervals_activity_id'),
            "race_name": link.get('race_name'),
            "linked_at": link.get('linked_at')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving linked activity: {str(e)}")


@router.delete("/{race_id}/athlete/{athlete_id}/linked-activity")
async def unlink_activity(race_id: int, athlete_id: int):
    """
    Remove the linked activity for a race athlete.
    """
    storage = get_storage()
    race = storage.get_race(race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    try:
        storage.unlink_race_activity(race_id, athlete_id)
        return {"message": "Activity unlinked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error unlinking activity: {str(e)}")
