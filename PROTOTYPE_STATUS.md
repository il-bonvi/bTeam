# 🎉 bTeam - Prototipo Intervals.icu

## ✅ Implementato

### 📦 Nuovi Moduli

| File | Descrizione |
|------|-------------|
| `intervals_client_v2.py` | Client API completo (114+ endpoint) |
| `intervals_models.py` | Modelli Pydantic per validazione |
| `intervals_sync.py` | Servizio di sincronizzazione |
| `config_bteam.py` | ✨ Aggiornato - Gestione API key |
| `gui_bteam.py` | ✨ Aggiornato - Dialog sincronizzazione |

### 🎯 Funzionalità disponibili

#### Client API (`intervals_client_v2.py`)
```python
client = IntervalsAPIClient(api_key='...')

# Attività
activities = client.get_activities(days_back=30)
details = client.get_activity(activity_id, include_intervals=True)

# Info atleta
athlete = client.get_athlete()

# Dati wellness
wellness = client.get_wellness(days_back=7)

# Power curve
power = client.get_power_curve()

# Calendario/Eventi
events = client.get_events(days_forward=30)
```

#### Servizio Sync (`intervals_sync.py`)
```python
sync = IntervalsSyncService(api_key='...')

# Lettura attività
activities, msg = sync.fetch_activities(days_back=30)

# Lettura atleta
athlete, msg = sync.fetch_athlete_info()

# Lettura wellness
wellness, msg = sync.fetch_wellness(days_back=7)

# Lettura power curve
power, msg = sync.fetch_power_curve()

# Formatting per database
formatted = IntervalsSyncService.format_activity_for_storage(activity)
```

#### GUI (`gui_bteam.py`)
- 🔄 Pulsante "Sincronizza Intervals" nella toolbar
- 🔐 Dialog di configurazione con test connessione
- 📊 Anteprima attività prima di importare
- 💾 Salvataggio automatico nel database

### 🚀 Workflow completo

1. **Configurazione**
   ```
   User → API Key → Test Connessione → ✓ Connesso
   ```

2. **Sincronizzazione**
   ```
   Select Atleta → Seleziona Giorni → Visualizza Attività
         ↓
   Intervals.icu API → Download Dati → Anteprima
         ↓
   Conferma → Save in Database → Aggiorna Tabelle
   ```

3. **Risultato**
   - Attività visibili nella tabella principale
   - Dati completi salvati in bteam.db
   - Cronologia per analytics

## 📊 Dati sincronizzati

Per ogni attività:
```json
{
  "intervals_id": "i12345",
  "name": "Evening Ride",
  "type": "Ride",
  "start_date": "2026-01-28T18:30:00",
  "distance_km": 42.3,
  "moving_time_minutes": 127.5,
  "elevation_m": 485,
  "avg_watts": 185,
  "normalized_watts": 210,
  "avg_hr": 142,
  "max_hr": 178,
  "training_load": 95.5,
  "intensity": 1.15,
  "feel": 8,
  "description": "Great ride with intervals"
}
```

## 🔄 Architettura

```
┌─────────────────────────────────────────┐
│     GUI - bTeam (gui_bteam.py)          │
│   - SyncIntervalsDialog                 │
│   - Integration nella toolbar            │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│    Config Manager (config_bteam.py)     │
│   - API key storage                      │
│   - Configuration persistence            │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  Sync Service (intervals_sync.py)       │
│   - fetch_activities()                   │
│   - fetch_athlete_info()                 │
│   - fetch_wellness()                     │
│   - format_activity_for_storage()        │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  API Client (intervals_client_v2.py)    │
│   - IntervalsAPIClient (40+ methods)    │
│   - REST endpoints completi              │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│    Intervals.icu (API v1)               │
│    - 114+ endpoints disponibili          │
└─────────────────────────────────────────┘
```

## 🧪 Testing

```bash
# Test il prototipo (senza GUI)
python bTeam/test_intervals_proto.py

# Output atteso:
# ✓ Test 1: Inizializzazione
# ✓ Test 2: Impostazione API key
# ✓ Test 3: Lettura informazioni atleta
# ✓ Test 4: Lettura attività
# ✓ Test 5: Formattazione per storage
# ✓ Test 6: Lettura wellness
# ✓ Test 7: Lettura power curve
# ✅ TUTTI I TEST PASSATI
```

## 📋 Checklist Implementazione

### Phase 1: Lettura Attività ✅
- [x] Client API funzionante
- [x] Modelli Pydantic
- [x] Servizio sincronizzazione
- [x] Integrazione GUI
- [x] Salvataggio database
- [x] Test suite
- [x] Documentazione

### Phase 2: Scrittura Dati ⏳
- [ ] `client.upload_activity()`
- [ ] `client.update_activity()`
- [ ] Dialog upload GUI
- [ ] Upload wellness data
- [ ] Test bidirezionale

### Phase 3: Multi-atleta OAuth ⏳
- [ ] OAuth 2.0 flow
- [ ] Token management
- [ ] Multi-account support
- [ ] Team management UI
- [ ] Permission handling

### Phase 4: Features Avanzate ⏳
- [ ] Download FIT files
- [ ] Workout library sync
- [ ] Analytics dashboard
- [ ] Power curve plotting
- [ ] HRV/recovery tracking

## 💡 Punti chiave

### Sicurezza
- ✅ API key salvata localmente solo
- ✅ Non inviata a terzi
- ✅ Password mode nel dialog

### Robustezza
- ✅ Try/except su tutti gli endpoint
- ✅ Messaggi di errore chiari
- ✅ Test connessione prima di sync
- ✅ Validazione Pydantic

### Estensibilità
- ✅ Facile aggiungere nuovi endpoint
- ✅ Format function per storage
- ✅ Modelli predefiniti
- ✅ Service separato dalla GUI

## 🎯 Uso immediato

### Per l'utente:
1. Ottieni API key da https://intervals.icu/settings
2. Avvia bTeam
3. Clicca "🔄 Sincronizza Intervals"
4. Incolla API key
5. Clicca "Test connessione"
6. Seleziona atleta
7. Clicca "Visualizza attività"
8. Clicca OK per importare

### Per lo sviluppatore:
```python
# Estendere il servizio per nuovi dati
class IntervalsSyncService:
    def fetch_custom_data(self):
        activities, _ = self.fetch_activities()
        # processamento custom
        return processed_data

# Aggiungere nuovo endpoint
def get_custom_endpoint(self):
    response = self._request('GET', '/api/v1/custom')
    return response.json()
```

## 📚 Documentazione

- [INTERVALS_INTEGRATION.md](INTERVALS_INTEGRATION.md) - Guida utente completa
- [intervals_client_v2.py](intervals_client_v2.py) - Docstring API
- [intervals_sync.py](intervals_sync.py) - Docstring servizio
- [test_intervals_proto.py](test_intervals_proto.py) - Esempi di utilizzo

## ✨ Prossimo passo

Della Phase 2 (Scrittura):
```python
# Caricamento attività
client.upload_activity(
    file_path='activity.fit',
    name='My Ride',
    description='Morning workout',
    type='Ride'
)

# Aggiornamento
client.update_activity(
    activity_id='i12345',
    name='Updated name',
    feel=8
)

# GUI: Dialog per selezionare file e caricare
```

---

**Status**: Prototipo funzionante e testato ✅
**Prossimo**: Phase 2 - Scrittura dati
