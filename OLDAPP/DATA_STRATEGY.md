# Strategia di Sincronizzazione Dati Intervals.icu - bTeam

## 📊 Dati Attualmente Raccolti da Intervals

### Attività (Activities)
Stai già prendendo dalla API:
- ✅ ID attività
- ✅ Nome/Titolo
- ✅ Tipo (Ride, Run, Swim, ecc)
- ✅ Data/Ora inizio
- ✅ Distanza (km)
- ✅ Durata movimento (minuti)
- ✅ Durata totale (minuti)
- ✅ Elevazione (m)
- ✅ Potenza media
- ✅ Potenza normalizzata
- ✅ FC media
- ✅ FC massima
- ✅ Cadenza media
- ✅ Training Load (ICU)
- ✅ Intensità (ICU)
- ✅ Feel (sensazione)
- ✅ Descrizione
- ✅ Intervalli rilevati (se richiesti)
- ✅ JSON raw completo

### Wellness (opzionale)
- ✅ Data
- ✅ Peso
- ✅ FC riposo
- ✅ HRV
- ✅ Sleep (ore e qualità)
- ✅ Note

### Events (Gare e Test)
- ✅ Data evento
- ✅ Nome
- ✅ Tipo (Race, Workout, Ftp Test, ecc)
- ✅ Descrizione

### Power Curve
- ✅ Curve di potenza (5s, 1min, 5min, 20min, 1h)

## 🎯 Cosa Aggiungere

### 1. **File FIT/TCX Completi**
```
Metodo disponibile: download_activity_fit_file(activity_id)
Vantaggi:
- Dati grezzi al 1 Hz (o più)
- Analizzabile con altre app (Golden Cheetah, etc)
- Posizionamento GPS completo
- Cadenza istantanea
- Temperature
- Campionamento completo del segnale HR/Potenza
```

### 2. **Identificazione Gare e Test**
```
Da fare:
- Filtrare eventi con type='Race' o type='FTP Test'
- Memorizzare separatamente per analisi specifiche
- Associare file FIT ai risultati
```

### 3. **Dati Metabolici Completi**
```
Disponibili ma non ancora salvati:
- Vo2max
- FTP (da test)
- Lactate Threshold Power
- Peak watts (per durata)
- Energy systems breakdown
```

### 4. **Componenti Allenamento**
```
Disponibili:
- Intervalli rilevati (già presi)
- Zone intensity
- Specifico per tipo di sport
```

## 🗄️ Struttura Database Proposta

### Tabella `activities` (espansa)
```sql
ALTER TABLE activities ADD COLUMNS (
    intervals_id STRING,           -- ID unico da Intervals
    activity_type STRING,          -- Ride, Run, Swim, etc
    avg_watts FLOAT,               -- Potenza media
    normalized_watts FLOAT,        -- Potenza normalizzata
    avg_hr FLOAT,                  -- FC media
    max_hr FLOAT,                  -- FC massima
    avg_cadence FLOAT,             -- Cadenza media
    training_load FLOAT,           -- ICU Training Load
    intensity_factor FLOAT,        -- ICU Intensity
    feel INT,                      -- Sensazione (1-10)
    elevation_gain_m FLOAT,        -- Elevazione
    is_race BOOLEAN,               -- È una gara?
    is_test BOOLEAN,               -- È un test (FTP)?
    fit_file_downloaded BOOLEAN,   -- FIT scaricato?
    fit_file_path STRING,          -- Path al file FIT
    tcx_file_path STRING,          -- Path al file TCX
    intervals_payload JSON         -- Raw JSON da Intervals (già presente)
);
```

### Nuova tabella `race_results`
```sql
CREATE TABLE race_results (
    id INT PRIMARY KEY,
    activity_id INT FOREIGN KEY,
    race_name STRING,
    race_date DATE,
    distance_km FLOAT,
    duration_minutes INT,
    avg_watts FLOAT,
    normalized_watts FLOAT,
    avg_hr FLOAT,
    max_hr FLOAT,
    placement INT,                 -- Posizione se disponibile
    category STRING,               -- Categoria gara
    notes TEXT,
    intervals_raw JSON,
    created_at TIMESTAMP
);
```

### Nuova tabella `fitness_tests`
```sql
CREATE TABLE fitness_tests (
    id INT PRIMARY KEY,
    activity_id INT FOREIGN KEY,
    test_type STRING,              -- FTP, Vo2max, Lactate, etc
    test_date DATE,
    result_value FLOAT,            -- Valore misurato (W, ml/kg/min, etc)
    result_unit STRING,            -- W, ml/kg/min, etc
    previous_value FLOAT,          -- Valore precedente
    improvement_pct FLOAT,         -- % miglioramento
    methodology STRING,            -- Come è stato misurato
    intervals_raw JSON,
    created_at TIMESTAMP
);
```

### Nuova tabella `fit_files`
```sql
CREATE TABLE fit_files (
    id INT PRIMARY KEY,
    activity_id INT FOREIGN KEY,
    file_type STRING,              -- FIT, TCX, GPX
    file_path STRING,              -- Path locale
    file_size_kb INT,
    downloaded_at TIMESTAMP,
    parsed BOOLEAN,                -- Già parsato?
    intervals_id STRING,           -- ID da Intervals
    created_at TIMESTAMP
);
```

## 🔄 Piano di Implementazione

### Fase 1: Espandere Storage
1. Aggiungere colonne a `activities`
2. Creare `race_results` e `fitness_tests`
3. Creare `fit_files`

### Fase 2: Espandere Sincronizzazione
1. Aggiungere download automatico FIT per ogni attività
2. Identificare gare e test
3. Salvare in tabelle dedicate

### Fase 3: Gestione File
1. Struttura cartelle: `data/fit_files/{athlete_id}/{YYYY}/{MM}/`
2. Naming: `{activity_id}_{activity_name}.fit`
3. Backup su cloud (opzionale)

### Fase 4: Visualizzazione
1. Tab "Gare" con analisi specifica
2. Tab "Test" con trend fitness
3. Export FIT/TCX per Golden Cheetah
4. Grafici Performance

## 💾 API Intervals Disponibili

```python
# Attività
get_activities(days_back=30)
get_activity(activity_id, include_intervals=True)
download_activity_fit_file(activity_id)      # ← IMPORTANTE
upload_activity(file_path, activity_date)
update_activity(activity_id, data)

# Gare/Test
get_events(event_type='Race')                # ← Filtrare per tipo
get_events(event_type='FTP Test')            

# Wellness
get_wellness(days_back=7)
get_wellness_date(date_str)

# Atleta
get_athlete()                                # Vo2max, FTP, ecc

# Power curve
get_power_curve()                            # 5s, 1min, 5min, 20min, 1h
```

## 🎯 Prossimi Passi Consigliati

1. **Priorità Alta**: 
   - [ ] Download file FIT per tutte le attività
   - [ ] Identificare gare vs allenamenti
   - [ ] Salvare dati FTP/test in tabella dedicata

2. **Priorità Media**:
   - [ ] Creare UI per visualizzare gare
   - [ ] UI per analizzare test
   - [ ] Export FIT per Golden Cheetah

3. **Priorità Bassa**:
   - [ ] Parsing file FIT (lettura dati grezzi)
   - [ ] Grafici prestazioni
   - [ ] Analisi trend

## 📝 Note Importanti

- Intervals.icu ha file FIT per TUTTE le attività (non solo caricate)
- Il download è automatico se sincronizzi via Garmin Connect
- I file FIT sono il "source of truth" - contengono tutto
- Golden Cheetah può leggere FIT e fare analisi avanzate
- WKO5 e TrainingPeaks integrano con Intervals

