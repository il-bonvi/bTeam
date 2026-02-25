# 📚 API Documentation - bTeam WebApp

## Panoramica

bTeam WebApp fornisce una API RESTful completa per la gestione di team, atleti, attività, gare e wellness data. L'API è costruita con FastAPI e include documentazione interattiva.

## Base URL

```
http://localhost:8000/api
```

## Autenticazione

Attualmente l'API non richiede autenticazione. In produzione, implementare un sistema di autenticazione appropriato.

---

## 📋 Teams API

### GET /api/teams/

Ottieni tutte le squadre.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Team Pro",
    "created_at": "2026-02-13T10:00:00"
  }
]
```

### GET /api/teams/{team_id}

Ottieni una squadra specifica.

**Parameters:**
- `team_id` (integer): ID della squadra

**Response:**
```json
{
  "id": 1,
  "name": "Team Pro",
  "created_at": "2026-02-13T10:00:00"
}
```

### POST /api/teams/

Crea una nuova squadra.

**Body:**
```json
{
  "name": "Team Pro"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Team Pro",
  "created_at": "2026-02-13T10:00:00"
}
```

### PUT /api/teams/{team_id}

Aggiorna una squadra.

**Parameters:**
- `team_id` (integer): ID della squadra

**Body:**
```json
{
  "name": "Team Pro Updated"
}
```

### DELETE /api/teams/{team_id}

Elimina una squadra.

**Parameters:**
- `team_id` (integer): ID della squadra

---

## 👥 Athletes API

### GET /api/athletes/

Ottieni tutti gli atleti, opzionalmente filtrati per squadra.

**Query Parameters:**
- `team_id` (optional): ID della squadra

**Response:**
```json
[
  {
    "id": 1,
    "first_name": "Mario",
    "last_name": "Rossi",
    "team_id": 1,
    "team_name": "Team Pro",
    "birth_date": "1995-05-15",
    "weight_kg": 70.5,
    "height_cm": 180.0,
    "gender": "Maschile",
    "cp": 280.0,
    "w_prime": 18000.0,
    "api_key": "****",
    "created_at": "2026-02-13T10:00:00"
  }
]
```

### GET /api/athletes/{athlete_id}

Ottieni un atleta specifico.

**Parameters:**
- `athlete_id` (integer): ID dell'atleta

### POST /api/athletes/

Crea un nuovo atleta.

**Body:**
```json
{
  "first_name": "Mario",
  "last_name": "Rossi",
  "team_id": 1,
  "birth_date": "1995-05-15",
  "weight_kg": 70.5,
  "height_cm": 180.0,
  "gender": "Maschile",
  "api_key": "your_intervals_api_key",
  "notes": "Note sull'atleta"
}
```

### PUT /api/athletes/{athlete_id}

Aggiorna un atleta.

**Parameters:**
- `athlete_id` (integer): ID dell'atleta

**Body:** (tutti i campi sono opzionali)
```json
{
  "first_name": "Mario",
  "weight_kg": 71.0,
  "cp": 285.0
}
```

### DELETE /api/athletes/{athlete_id}

Elimina un atleta.

---

## 🏃 Activities API

### GET /api/activities/

Ottieni tutte le attività con filtri opzionali.

**Query Parameters:**
- `athlete_id` (optional): Filtra per atleta
- `limit` (optional, default=100): Numero massimo di risultati
- `is_race` (optional): Filtra per gare (true/false)

**Response:**
```json
[
  {
    "id": 1,
    "athlete_id": 1,
    "athlete_name": "Mario Rossi",
    "title": "Allenamento Base",
    "activity_date": "2026-02-13",
    "activity_type": "Ride",
    "duration_minutes": 120.5,
    "distance_km": 45.3,
    "tss": 85.2,
    "source": "INTERVALS",
    "is_race": false,
    "avg_watts": 220.0,
    "normalized_watts": 235.0,
    "avg_hr": 145,
    "max_hr": 178,
    "training_load": 85.2,
    "intensity": 0.75,
    "feel": 7,
    "created_at": "2026-02-13T10:00:00"
  }
]
```

### GET /api/activities/{activity_id}

Ottieni un'attività specifica.

### POST /api/activities/

Crea una nuova attività.

**Body:**
```json
{
  "athlete_id": 1,
  "title": "Allenamento Base",
  "activity_date": "2026-02-13",
  "activity_type": "Ride",
  "duration_minutes": 120.5,
  "distance_km": 45.3,
  "tss": 85.2,
  "source": "MANUAL",
  "is_race": false,
  "avg_watts": 220.0,
  "avg_hr": 145,
  "feel": 7
}
```

### DELETE /api/activities/{activity_id}

Elimina un'attività.

### GET /api/activities/athlete/{athlete_id}/stats

Ottieni statistiche per un atleta.

**Response:**
```json
{
  "total_activities": 45,
  "total_distance_km": 2150.5,
  "total_duration_hours": 87.5,
  "avg_tss": 78.3
}
```

---

## 🏁 Races API

### GET /api/races/

Ottieni tutte le gare.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Gran Fondo delle Dolomiti",
    "race_date": "2026-06-15",
    "distance_km": 120.0,
    "gender": "Maschile",
    "category": "Elite",
    "elevation_m": 2500.0,
    "avg_speed_kmh": 35.0,
    "predicted_duration_minutes": 205.7,
    "notes": "Gara importante",
    "athletes": [
      {
        "id": 1,
        "name": "Rossi Mario"
      }
    ],
    "created_at": "2026-02-13T10:00:00"
  }
]
```

### GET /api/races/{race_id}

Ottieni una gara specifica.

### POST /api/races/

Crea una nuova gara.

**Body:**
```json
{
  "name": "Gran Fondo delle Dolomiti",
  "race_date": "2026-06-15",
  "distance_km": 120.0,
  "gender": "Maschile",
  "category": "Elite",
  "elevation_m": 2500.0,
  "avg_speed_kmh": 35.0,
  "notes": "Gara importante"
}
```

### DELETE /api/races/{race_id}

Elimina una gara.

### POST /api/races/{race_id}/athletes

Aggiungi un atleta a una gara.

**Body:**
```json
{
  "athlete_id": 1,
  "kj_per_hour_per_kg": 10.0,
  "objective": "A"
}
```

### DELETE /api/races/{race_id}/athletes/{athlete_id}

Rimuovi un atleta da una gara.

### GET /api/races/{race_id}/athletes

Ottieni tutti gli atleti di una gara.

---

## ❤️ Wellness API

### GET /api/wellness/

Ottieni dati wellness con filtri opzionali.

**Query Parameters:**
- `athlete_id` (optional): Filtra per atleta
- `days_back` (optional, default=30): Giorni indietro

**Response:**
```json
[
  {
    "id": 1,
    "athlete_id": 1,
    "wellness_date": "2026-02-13",
    "weight_kg": 70.5,
    "resting_hr": 48,
    "hrv": 85.3,
    "steps": 8500,
    "soreness": 3,
    "fatigue": 4,
    "stress": 2,
    "mood": 8,
    "motivation": 7,
    "sleep_secs": 28800,
    "sleep_score": 8,
    "comments": "Buona giornata",
    "created_at": "2026-02-13T10:00:00"
  }
]
```

### GET /api/wellness/{wellness_id}

Ottieni un entry wellness specifico.

### POST /api/wellness/

Crea un nuovo entry wellness.

**Body:**
```json
{
  "athlete_id": 1,
  "wellness_date": "2026-02-13",
  "weight_kg": 70.5,
  "resting_hr": 48,
  "hrv": 85.3,
  "steps": 8500,
  "soreness": 3,
  "fatigue": 4,
  "stress": 2,
  "mood": 8,
  "motivation": 7,
  "sleep_secs": 28800,
  "sleep_score": 8,
  "comments": "Buona giornata"
}
```

### PUT /api/wellness/{wellness_id}

Aggiorna un entry wellness.

### DELETE /api/wellness/{wellness_id}

Elimina un entry wellness.

### GET /api/wellness/athlete/{athlete_id}/latest

Ottieni l'ultimo entry wellness per un atleta.

---

## 🔄 Sync API (Intervals.icu)

### POST /api/sync/test-connection

Testa la connessione a Intervals.icu.

**Body:**
```json
{
  "api_key": "your_intervals_api_key"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "athlete_name": "Mario Rossi"
}
```

### POST /api/sync/activities

Sincronizza attività da Intervals.icu.

**Body:**
```json
{
  "athlete_id": 1,
  "api_key": "your_intervals_api_key",
  "days_back": 30,
  "include_intervals": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Imported 15 activities",
  "imported": 15,
  "total": 15
}
```

### POST /api/sync/wellness

Sincronizza dati wellness da Intervals.icu.

**Body:**
```json
{
  "athlete_id": 1,
  "api_key": "your_intervals_api_key",
  "days_back": 7
}
```

**Response:**
```json
{
  "success": true,
  "message": "Imported 7 wellness entries",
  "imported": 7
}
```

### POST /api/sync/push-race

Pusha una gara su Intervals.icu come evento pianificato per **tutti gli atleti iscritti** nella gara. 
Usa automaticamente la API key di ogni atleta dal database.
Se la gara è già presente nel calendario di un atleta, non viene creato un duplicato.

**Body:**
```json
{
  "race_id": 1
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Race pushed to 3 athletes",
  "athletes_processed": 3,
  "total_athletes": 3,
  "failed_athletes": null
}
```

**Response (Error - No API Keys):**
```json
{
  "success": false,
  "detail": "No athletes in this race have an API key configured"
}
```

**Response (Partial Failure):**
```json
{
  "success": true,
  "message": "Race pushed to 2 athletes",
  "athletes_processed": 2,
  "total_athletes": 3,
  "failed_athletes": ["Athlete 5: Connection error"]
}
```

### GET /api/sync/power-curve/{athlete_id}

Ottieni la power curve da Intervals.icu.

**Query Parameters:**
- `api_key`: API key di Intervals.icu
- `days_back` (optional, default=90): Giorni indietro

**Response:**
```json
{
  "success": true,
  "data": {
    "secs": [1, 5, 10, 30, 60, 120, 300, 600, 1200, 3600],
    "watts": [850, 680, 550, 420, 380, 350, 310, 285, 265, 240]
  }
}
```

---

## 🔗 Documentazione Interattiva

Quando il server è in esecuzione, visita:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Questi endpoint forniscono documentazione interattiva dove puoi testare tutte le API direttamente dal browser.

---

## 📝 Note

- Tutti gli endpoint restituiscono JSON
- Gli errori sono restituiti con codici di stato HTTP appropriati (400, 404, 500, etc.)
- Le date sono in formato ISO 8601 (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
- I campi opzionali possono essere omessi nelle richieste POST/PUT

---

**Versione API**: 1.0.0  
**Ultima Aggiornamento**: 2026-02-13
