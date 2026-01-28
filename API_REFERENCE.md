# 📚 API Reference Completa - Intervals.icu

## 🎯 Comandi Disponibili (114+ endpoints)

### 🏃 **ACTIVITIES** - Gestire attività/allenamenti

#### **LEGGERE (GET)**
```python
# Lista attività con filtri
activities = client.get_activities(
    oldest='2025-01-01',      # Data inizio
    newest='2025-01-28',      # Data fine
    limit=100,                 # Max risultati
    offset=0                   # Paginazione
)

# Dettagli completi di una attività
details = client.get_activity(
    activity_id='i12345',
    include_intervals=True    # Includi intervalli dettagliati
)

# Best efforts di una attività
efforts = client.get_activity_best_efforts(activity_id='i12345')

# Download file FIT originale
client.download_activity_file(
    activity_id='i12345',
    output_path='activity.fit.gz'
)

# Download file FIT modificato (Intervals.icu)
client.download_activity_fit_file(
    activity_id='i12345',
    output_path='edited.fit.gz'
)
```

#### **SCRIVERE (POST/PUT)**
```python
# Upload una attività da file FIT
result = client.upload_activity(
    file_path='myride.fit',
    name='Giro Domenicale',
    type='Ride',  # Ride, Run, Swim, ecc
    private=False,
    commute=False
)

# Modifica attività esistente
client.update_activity(
    activity_id='i12345',
    name='Nuovo nome',
    feel=8,                    # Feel 1-10
    notes='Note private',
    training_load=250,
    intensity=85,
    type='Ride'
)

# Elimina una attività
client.delete_activity(activity_id='i12345')
```

---

### 💪 **WELLNESS** - Dati benessere

#### **LEGGERE (GET)**
```python
# Lista dati wellness (ultimi N giorni)
wellness_data = client.get_wellness(days_back=7)

# Dati wellness di una data specifica
today = client.get_wellness_date('2025-01-28')
# Ritorna: weight, resting_hr, hrv, notes, ecc
```

#### **SCRIVERE (POST/PUT)**
```python
# Aggiorna dati wellness singolo giorno
client.update_wellness(
    date='2025-01-28',
    weight=70.5,              # kg
    restingHR=48,             # bpm
    hrv=85.3,                 # ms
    notes='Buone sensazioni'
)

# Bulk upload più giorni
client.upload_wellness_bulk([
    {'id': '2025-01-28', 'weight': 70.5, 'restingHR': 48, 'hrv': 85},
    {'id': '2025-01-27', 'weight': 70.3, 'restingHR': 47, 'hrv': 82},
    {'id': '2025-01-26', 'weight': 70.2, 'restingHR': 49, 'hrv': 80}
])
```

---

### 📅 **CALENDAR/EVENTS** - Allenamenti pianificati

#### **LEGGERE (GET)**
```python
# Lista eventi futuri
events = client.get_events(
    days_forward=30          # Prossimi 30 giorni
)

# Dettagli di un singolo evento
event = client.get_event(event_id=123)

# Scarica workout file
zwo = client.download_event_workout(
    event_id=123,
    format='zwo',            # zwo, mrc, erg
    save_path='workout.zwo'
)
```

#### **SCRIVERE (POST/PUT)**
```python
# Crea un workout pianificato
workout = client.create_event(
    category='WORKOUT',
    start_date_local='2025-02-01T10:00:00',
    name='Intervalli Soglia',
    description='- 20m 60%\n- 3x (10m 95%, 5m 50%)\n- 10m 60%',
    type='Ride',
    duration_minutes=90,
    notes='Lavora sulla soglia'
)

# Modifica evento
client.update_event(
    event_id=123,
    name='Nuovo nome',
    description='Descrizione aggiornata'
)

# Elimina evento
client.delete_event(event_id=123)

# Crea più eventi con upsert (aggiorna se esiste)
events = client.create_events_bulk([
    {
        'category': 'WORKOUT',
        'start_date_local': '2025-02-01T10:00:00',
        'name': 'Workout 1',
        'external_id': 'my-id-1',  # Per tracciamento
        'type': 'Ride'
    },
    {
        'category': 'WORKOUT',
        'start_date_local': '2025-02-02T10:00:00',
        'name': 'Workout 2',
        'external_id': 'my-id-2',
        'type': 'Ride'
    }
], upsert=True)

# Elimina più eventi
client.delete_events_bulk([
    {'id': 123},
    {'external_id': 'my-id-1'}
])
```

---

### 📚 **WORKOUT LIBRARY** - Libreria allenamenti

#### **LEGGERE (GET)**
```python
# Lista cartelle
folders = client.get_folders()

# Lista workout
workouts = client.get_workouts()

# Dettagli workout
workout = client.get_workout(workout_id=456)
```

#### **SCRIVERE (POST/PUT)**
```python
# Crea workout in libreria
new_workout = client.create_workout(
    folder_id=1,
    name='Sweet Spot 3x10',
    description='- 15m 60%\n- 3x (10m 90%, 5m 60%)\n- 10m 60%'
)

# Modifica workout
client.update_workout(
    workout_id=456,
    name='Nuovo nome',
    description='Descrizione aggiornata'
)

# Elimina workout
client.delete_workout(workout_id=456)
```

---

### 👤 **ATHLETE** - Info atleta

#### **LEGGERE (GET)**
```python
# Info atleta (chi sei)
athlete = client.get_athlete()
# Ritorna: id, firstname, lastname, email, ecc

# Settings completi
settings = client.get_athlete_settings()
# Ritorna: weight, icu_ftp, icu_hr_lthr, icu_vo2max, ecc

# Calendari disponibili
calendars = client.get_calendars()
```

#### **SCRIVERE (POST/PUT)**
```python
# Aggiorna info atleta
client.update_athlete(
    weight=70.0,              # kg
    icu_ftp=250,              # Watts
    icu_hr_lthr=165,          # bpm - Soglia cardiaca
    icu_vo2max=60,            # ml/kg/min
    icu_cp=400,               # W - Critical Power
    ecp_w_prime=25000         # Joules - W'
)
```

---

### 📊 **ANALYTICS** - Analisi dati

#### **LEGGERE (GET)**
```python
# Power Curve (max watts per durata)
curve = client.get_power_curve(
    oldest='2024-11-01',
    newest='2025-01-28'
)
# Ritorna: 1s, 5s, 10s, 1min, 5min, 10min, 20min, 60min, ecc max watts

# Fitness (CTL, ATL, TSB)
fitness = client.get_fitness(
    oldest='2025-01-01',
    newest='2025-01-28'
)
# Ritorna: data, ctl (fitness), atl (fatica), tsb (forma), ecc
```

---

## 🛠️ **Helper Functions**

### Format Workout Description
```python
from intervals_client import format_workout_description

description = format_workout_description(
    warmup_minutes=15,
    intervals=[
        (8, 110, 8, 50),   # 8min@110%, 8min@50%
        (8, 110, 8, 50),
        (8, 110, 8, 50),
        (8, 110, 8, 50)
    ],
    cooldown_minutes=10
)

# Risultato:
# - 15m 60%
# - 4x (
#   - 8m 110%
#   - 8m 50%
# )
# - 10m 60%
```

---

## 🎯 **Casi d'Uso Pratici**

### 1️⃣ **Sincronizzare tutte le attività di un atleta**
```python
# Scarica ultimo mese
activities = client.get_activities(days_back=30)

for activity in activities:
    details = client.get_activity(activity['id'], include_intervals=True)
    
    # Salva nel DB
    store_in_database({
        'id': details['id'],
        'name': details['name'],
        'date': details['start_date_local'],
        'type': details['type'],
        'duration': details['moving_time'],
        'distance': details['distance'],
        'tss': details['icu_training_load'],
        'intensity': details['icu_intensity'],
        'power_avg': details['average_watts'],
        'hr_avg': details['average_heartrate'],
        'intervals': details.get('icu_intervals', [])
    })
```

### 2️⃣ **Creare una settimana di allenamenti**
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

### 3️⃣ **Tracciare dati benessere quotidiani**
```python
from datetime import date, timedelta

# Ultimi 7 giorni
for i in range(7):
    d = date.today() - timedelta(days=i)
    client.update_wellness(
        date=d.isoformat(),
        weight=70.5 + (0.1 * i),
        restingHR=48 - i,
        hrv=85 + (2 * i)
    )
```

### 4️⃣ **Analizzare forma fisica (CTL/ATL/TSB)**
```python
from datetime import date, timedelta

# Ultimi 30 giorni di fitness
fitness = client.get_fitness(
    oldest=(date.today() - timedelta(days=30)).isoformat(),
    newest=date.today().isoformat()
)

for day in fitness:
    ctl = day['ctl']      # Fitness (long-term training load)
    atl = day['atl']      # Fatica (short-term fatigue)
    tsb = day['tsb']      # Forma (Training Stress Balance)
    
    if tsb > 25:
        print(f"{day['date']}: ⬆️ FORMA OTTIMA (TSB={tsb:.0f})")
    elif tsb > 0:
        print(f"{day['date']}: ➡️ Buona forma (TSB={tsb:.0f})")
    elif tsb > -25:
        print(f"{day['date']}: ⬇️ Faticato (TSB={tsb:.0f})")
    else:
        print(f"{day['date']}: 🔴 SOVRALLENAMENTO (TSB={tsb:.0f})")
```

### 5️⃣ **Ottenere dati per dashboard atleta**
```python
athlete = client.get_athlete()
settings = client.get_athlete_settings()

# Ultimi 7 giorni
activities_week = client.get_activities(days_back=7)
total_load = sum(a.get('icu_training_load', 0) for a in activities_week)

# Ultimi 7 giorni benessere
wellness = client.get_wellness(days_back=7)
avg_weight = sum(w.get('weight', 0) for w in wellness) / len(wellness) if wellness else 0

# Forma attuale
fitness = client.get_fitness(days_back=7)
current_tsb = fitness[-1]['tsb'] if fitness else 0

dashboard = {
    'atleta': athlete['firstname'],
    'ftp': settings.get('icu_ftp', 'N/A'),
    'peso': avg_weight,
    'training_load_7d': total_load,
    'forma': 'OTTIMA' if current_tsb > 25 else 'BUONA' if current_tsb > 0 else 'FATICATO'
}
```

---

## 🔐 **Autenticazione**

### Con API Key (personale)
```python
from intervals_client import IntervalsAPIClient

client = IntervalsAPIClient(api_key='tua_api_key_qui')
```

### Con OAuth Bearer Token (multi-user)
```python
client = IntervalsAPIClient(access_token='bearer_token_from_oauth')
```

---

## 📝 **Note Importanti**

1. **API Key Personale**: Usa solo per leggere/scrivere i TUI dati
2. **OAuth**: Necessario per app che gestiscono più atleti
3. **Rate Limits**: Non specificati, ma usa limiti ragionevoli (~100 req/min)
4. **Date Format**: ISO format `YYYY-MM-DD` o `YYYY-MM-DDTHH:MM:SS`
5. **Unità**: Watts, kg, bpm, km, minuti (sistema metrico/watt)

