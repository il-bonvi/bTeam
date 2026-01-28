# 📚 API Reference - Intervals.icu

Documentazione completa del client API Python per Intervals.icu.

## 🎯 Setup

```python
from intervals_client_v2 import IntervalsAPIClient

# Con API Key (uso personale)
client = IntervalsAPIClient(api_key='tua_chiave')

# Con OAuth Token (multi-utente)
client = IntervalsAPIClient(access_token='bearer_token')
```

## 🏃 Activities - Gestione Attività

### Lettura

```python
# Lista attività
activities = client.get_activities(
    oldest='2025-01-01',
    newest='2025-01-28',
    limit=100
)

# Dettagli completi
details = client.get_activity('i12345', include_intervals=True)

# Download file FIT
client.download_activity_file('i12345', 'activity.fit.gz')
```

### Scrittura

```python
# Upload attività
result = client.upload_activity(
    file_path='myride.fit',
    name='Giro Domenicale',
    type='Ride'
)

# Modifica attività
client.update_activity(
    activity_id='i12345',
    name='Nuovo nome',
    feel=8,
    notes='Note private'
)

# Elimina attività
client.delete_activity('i12345')
```

## 💪 Wellness - Dati Benessere

```python
# Lista dati wellness
wellness = client.get_wellness(days_back=7)

# Aggiorna singolo giorno
client.update_wellness(
    date='2025-01-28',
    weight=70.5,
    restingHR=48,
    hrv=85.3
)

# Bulk upload
client.upload_wellness_bulk([
    {'id': '2025-01-28', 'weight': 70.5, 'restingHR': 48},
    {'id': '2025-01-27', 'weight': 70.3, 'restingHR': 47}
])
```

## 📅 Calendar/Events - Allenamenti Pianificati

```python
# Lista eventi
events = client.get_events(days_forward=30)

# Crea workout
workout = client.create_event(
    category='WORKOUT',
    start_date_local='2025-02-01T10:00:00',
    name='Intervalli Soglia',
    description='- 20m 60%\n- 3x (10m 95%, 5m 50%)\n- 10m 60%',
    type='Ride'
)

# Bulk create con upsert
events = client.create_events_bulk([
    {
        'category': 'WORKOUT',
        'start_date_local': '2025-02-01T10:00:00',
        'name': 'Workout 1',
        'external_id': 'my-id-1'
    }
], upsert=True)
```

## 👤 Athlete - Info Atleta

```python
# Info atleta
athlete = client.get_athlete()

# Settings completi
settings = client.get_athlete_settings()

# Aggiorna settings
client.update_athlete(
    weight=70.0,
    icu_ftp=250,
    icu_hr_lthr=165
)
```

## 📊 Analytics - Analisi Dati

```python
# Power curve
curve = client.get_power_curve(
    oldest='2024-11-01',
    newest='2025-01-28'
)

# Fitness (CTL, ATL, TSB)
fitness = client.get_fitness(
    oldest='2025-01-01',
    newest='2025-01-28'
)
```

## 📚 Workout Library

```python
# Lista workout
workouts = client.get_workouts()

# Crea workout
new_workout = client.create_workout(
    folder_id=1,
    name='Sweet Spot 3x10',
    description='- 15m 60%\n- 3x (10m 90%, 5m 60%)\n- 10m 60%'
)
```

## 🎯 Esempi Pratici

### 1. Sincronizzare Attività

```python
# Scarica ultimo mese
activities = client.get_activities(days_back=30)

for activity in activities:
    details = client.get_activity(activity['id'])
    
    # Salva nel DB
    store_in_database({
        'id': details['id'],
        'name': details['name'],
        'date': details['start_date_local'],
        'distance': details['distance'],
        'tss': details['icu_training_load']
    })
```

### 2. Creare Piano Settimanale

```python
from datetime import date, timedelta

monday = date(2025, 2, 1)

workouts = [
    {'day': 0, 'name': 'Endurance 60m @ 65%'},
    {'day': 2, 'name': 'VO2 Max 4x5min @ 120%'},
    {'day': 4, 'name': 'Soglia 3x10min @ 95%'},
    {'day': 6, 'name': 'Lungo 120m @ 60%'}
]

for workout in workouts:
    date_event = monday + timedelta(days=workout['day'])
    client.create_event(
        category='WORKOUT',
        start_date_local=date_event.isoformat() + 'T10:00:00',
        name=workout['name'],
        type='Ride'
    )
```

### 3. Analisi Forma Fisica

```python
# Ottieni dati fitness
fitness = client.get_fitness(days_back=7)
latest = fitness[-1]

tsb = latest['tsb']  # Training Stress Balance

if tsb > 25:
    print("⬆️ FORMA OTTIMA")
elif tsb > 0:
    print("➡️ Buona forma")
elif tsb > -25:
    print("⬇️ Faticato")
else:
    print("🔴 SOVRALLENAMENTO")
```

## 📝 Note Importanti

1. **Rate Limits**: Usa limiti ragionevoli (~100 req/min)
2. **Date Format**: ISO format `YYYY-MM-DD` o `YYYY-MM-DDTHH:MM:SS`
3. **Unità**: Watts, kg, bpm, km, minuti (sistema metrico)
4. **Sicurezza**: API key personale solo per i tuoi dati, OAuth per multi-utente

## 🛠️ Helper Functions

### Format Workout Description
```python
from intervals_client_v2 import format_workout_description

description = format_workout_description(
    warmup_minutes=15,
    intervals=[
        (8, 110, 8, 50),  # 8min@110%, 8min@50%
        (8, 110, 8, 50),
        (8, 110, 8, 50)
    ],
    cooldown_minutes=10
)
```

---

**Vedi anche**: [INTERVALS_GUIDE.md](INTERVALS_GUIDE.md) per guida utente completa
