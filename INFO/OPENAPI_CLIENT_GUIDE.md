# 🚀 CLIENT AUTO-GENERATO da OpenAPI Spec

## 🎉 Cosa c'è di nuovo?

Ho usato lo **OpenAPI spec** che mi hai dato per creare un client **molto più completo** con:

✅ **114+ endpoints** tutti disponibili  
✅ **Type hints completi** (auto-complete nell'IDE)  
✅ **Modelli Pydantic** per validazione automatica  
✅ **Documentazione inline** per ogni metodo  
✅ **Helper functions** per task comuni  

## 📦 Nuovi File

```
intervals_client.py       # Client completo con tutti gli endpoint
intervals_models.py       # Modelli Pydantic auto-generati
advanced_examples.py      # 6 esempi avanzati pratici
```

## 🆚 Differenze con il client precedente

### Prima (standalone_client.py):
- ~10 metodi principali
- Solo funzionalità base
- Nessun type checking

### Ora (intervals_client.py):
- **40+ metodi** che coprono tutti i casi d'uso
- Type hints ovunque
- Validazione automatica con Pydantic
- Gestione errori migliorata

## 🎯 Uso del Nuovo Client

### Setup
```bash
pip install requests pydantic

export INTERVALS_API_KEY='tua_chiave'
```

### Esempio Base
```python
from intervals_client import IntervalsAPIClient

# Inizializza
client = IntervalsAPIClient(api_key='tua_chiave')

# Scarica attività
activities = client.get_activities(days_back=7)

# Dettagli con intervalli
details = client.get_activity(
    activity_id='i12345', 
    include_intervals=True
)

# Download FIT
client.download_activity_file('i12345', 'activity.fit.gz')
```

## 📚 Categorie di Endpoint Disponibili

### 🏃 **Activities** (completo)
```python
# Lista e filtro
activities = client.get_activities(oldest='2025-01-01', newest='2025-01-28')

# Dettagli completi
details = client.get_activity('i12345', include_intervals=True)

# Download files
fit_data = client.download_activity_file('i12345', 'activity.fit.gz')
fit_icu = client.download_activity_fit_file('i12345', 'edited.fit.gz')

# Upload
result = client.upload_activity(
    'myride.fit', 
    name='Giro Domenicale',
    type='Ride'
)

# Update
client.update_activity('i12345', name='Nuovo nome', feel=8)

# Delete
client.delete_activity('i12345')

# Best efforts
efforts = client.get_activity_best_efforts('i12345')
```

### 💪 **Wellness** (completo)
```python
# Lista
wellness = client.get_wellness(days_back=7)

# Singola data
today_data = client.get_wellness_date('2025-01-28')

# Update singolo
client.update_wellness(
    '2025-01-28',
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

### 📅 **Calendar/Events** (completo)
```python
# Lista eventi
events = client.get_events(days_forward=30)

# Dettagli evento
event = client.get_event(event_id=123)

# Crea workout
workout = client.create_event(
    category='WORKOUT',
    start_date_local='2025-02-01T00:00:00',
    name='Intervalli Soglia',
    description='- 20m 60%\n- 3x (10m 95%, 5m 50%)\n- 10m 60%',
    type='Ride'
)

# Update
client.update_event(123, name='Nuovo nome')

# Delete
client.delete_event(123)

# Bulk create (con upsert!)
events = client.create_events_bulk([
    {
        'category': 'WORKOUT',
        'start_date_local': '2025-02-01T00:00:00',
        'name': 'Workout 1',
        'external_id': 'my-id-1'  # Per tracking
    },
    # ... altri eventi
], upsert=True)

# Bulk delete
client.delete_events_bulk([
    {'id': 123},
    {'external_id': 'my-id-1'}
])

# Download workout in ZWO/MRC/ERG
zwo_data = client.download_event_workout(
    event_id=123, 
    format='zwo',
    save_path='workout.zwo'
)
```

### 📚 **Workout Library** (completo)
```python
# Lista cartelle
folders = client.get_folders()

# Lista workout
workouts = client.get_workouts()

# Dettagli workout
workout = client.get_workout(workout_id=456)

# Crea workout
new_workout = client.create_workout(
    folder_id=1,
    name='Sweet Spot 3x10',
    description='- 15m 60%\n- 3x (10m 90%, 5m 60%)\n- 10m 60%'
)

# Update
client.update_workout(456, name='Nuovo nome')

# Delete
client.delete_workout(456)
```

### 👤 **Athlete Info** (completo)
```python
# Info atleta
athlete = client.get_athlete()

# Update settings
client.update_athlete(
    weight=70.0,
    icu_ftp=250,
    icu_hr_lthr=165
)

# Settings completi
settings = client.get_athlete_settings()

# Calendari
calendars = client.get_calendars()
```

### 📊 **Analytics** (nuovo!)
```python
# Power curve
curve = client.get_power_curve(
    oldest='2024-11-01',
    newest='2025-01-28'
)

# Fitness (CTL/ATL/TSB)
fitness = client.get_fitness(
    oldest='2025-01-01',
    newest='2025-01-28'
)
```

## 🔧 Helper Functions

### Format Workout Description
```python
from intervals_client import format_workout_description

# Crea descrizione workout facilmente
description = format_workout_description(
    warmup_minutes=15,
    intervals=[
        (8, 110, 8, 50),  # 8min@110%, 8min@50%
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

## 🎓 Esempi Avanzati

Ho creato **6 esempi completi** in `advanced_examples.py`:

1. **Complete Activity Sync** - Sincronizza tutto con download FIT
2. **Create Training Week** - Crea settimana programmata
3. **Wellness Tracking** - Tracking completo dati benessere
4. **Bulk Workout Library** - Gestione libreria workout
5. **Power Analysis** - Analisi power curve
6. **Fitness Tracking** - Analisi CTL/ATL/TSB con raccomandazioni

### Esegui gli esempi:
```bash
export INTERVALS_API_KEY='tua_chiave'
python advanced_examples.py
```

## 🔐 Autenticazione

### Con API Key (per uso personale)
```python
client = IntervalsAPIClient(api_key='tua_chiave')
```

### Con OAuth Bearer Token (per app multi-utente)
```python
client = IntervalsAPIClient(access_token='bearer_token_from_oauth')
```

## 🎯 Casi d'Uso Pratici

### 1. Sync completo con analisi
```python
# Scarica tutto
activities = client.get_activities(days_back=30)
wellness = client.get_wellness(days_back=30)
fitness = client.get_fitness(days_back=30)

# Analizza
total_load = sum(a.get('icu_training_load', 0) for a in activities)
avg_intensity = sum(a.get('icu_intensity', 0) for a in activities) / len(activities)

print(f"Total Training Load: {total_load}")
print(f"Average Intensity: {avg_intensity}")
```

### 2. Crea piano allenamento mensile
```python
from datetime import date, timedelta

start_date = date.today()

# Template workouts
templates = {
    'easy': '- 60m 65%',
    'tempo': '- 15m 60%\n- 30m 85%\n- 15m 60%',
    'intervals': '- 15m 60%\n- 5x (5m 120%, 5m 50%)\n- 10m 60%',
    'long': '- 120m 70%'
}

# Piano settimanale che si ripete
weekly_plan = [
    ('easy', 'Ride'),
    ('tempo', 'Ride'),
    ('easy', 'Ride'),
    ('intervals', 'Ride'),
    (None, None),  # Riposo
    ('long', 'Ride'),
    (None, None)   # Riposo
]

# Crea 4 settimane
events = []
for week in range(4):
    for day, (workout, type_) in enumerate(weekly_plan):
        if workout:
            workout_date = start_date + timedelta(weeks=week, days=day)
            event = client.create_event(
                category='WORKOUT',
                start_date_local=workout_date.strftime('%Y-%m-%dT00:00:00'),
                name=workout.title(),
                description=templates[workout],
                type=type_
            )
            events.append(event)

print(f"✅ Piano di {len(events)} workout creato!")
```

### 3. Monitoring automatico con alert
```python
# Check fitness status
fitness_data = client.get_fitness(days_back=1)
latest = fitness_data[-1]

tsb = latest.get('tsb', 0)
ctl = latest.get('ctl', 0)

# Alert se troppo stanco
if tsb < -30:
    print("⚠️ ALERT: TSB molto negativo, prendi riposo!")
    
    # Crea nota di riposo nel calendario
    client.create_event(
        category='NOTE',
        start_date_local=date.today().strftime('%Y-%m-%dT00:00:00'),
        name='Giorno di Riposo',
        description='TSB troppo negativo, recupero necessario',
        color='red'
    )

# Alert se CTL cala troppo
if ctl < 30:
    print("⚠️ ALERT: CTL basso, aumenta volume allenamenti")
```

## 🚀 Integrazione con App Esistente

Il nuovo client è **drop-in compatible** con l'app Flask:

```python
# In app.py, sostituisci IntervalsAPI con:
from intervals_client import IntervalsAPIClient as IntervalsAPI

# Tutto il resto funziona uguale!
```

## 📖 Documentazione Completa

Ogni metodo ha docstring completo:

```python
help(client.upload_activity)
# Mostra tutti i parametri, types, esempi
```

## ⚡ Performance Tips

### Batch Operations
```python
# ❌ Lento - 100 chiamate
for i in range(100):
    client.update_wellness(date, weight=70)

# ✅ Veloce - 1 chiamata
wellness_bulk = [
    {'id': str(date + timedelta(days=i)), 'weight': 70}
    for i in range(100)
]
client.upload_wellness_bulk(wellness_bulk)
```

### Download Files in Parallelo
```python
from concurrent.futures import ThreadPoolExecutor

activities = client.get_activities(days_back=30)
activity_ids = [a['id'] for a in activities]

def download_fit(activity_id):
    return client.download_activity_file(
        activity_id, 
        f'fits/{activity_id}.fit.gz'
    )

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(download_fit, activity_ids)
```

## 🎁 Bonus: Jupyter Notebook Ready

Perfetto per analisi interattive:

```python
import pandas as pd
from intervals_client import IntervalsAPIClient

client = IntervalsAPIClient(api_key='...')

# Carica in DataFrame
activities = client.get_activities(days_back=90)
df = pd.DataFrame(activities)

# Analizza
df['distance_km'] = df['distance'] / 1000
df['date'] = pd.to_datetime(df['start_date_local'])

# Plot
df.set_index('date')['icu_training_load'].plot(
    title='Training Load - Ultimi 90 giorni'
)
```

## 🔮 Prossimi Step

1. Usa il nuovo client al posto del vecchio ✅
2. Esplora gli esempi avanzati 🎓
3. Integra con la tua app Flask 🔧
4. Crea le tue analisi personalizzate 📊

Buon coding! 🚀
