# bTeam - Integrazione Intervals.icu

## 🎯 Cosa è stato implementato

Prototipo funzionante con lettura attività da Intervals.icu tramite API.

### Componenti creati:

1. **intervals_client_v2.py** - Client API completo con 40+ metodi
2. **intervals_models.py** - Modelli Pydantic per validazione dati
3. **intervals_sync.py** - Servizio di sincronizzazione
4. **gui_bteam.py (aggiornata)** - UI per configurare e sincronizzare
5. **config_bteam.py (aggiornata)** - Gestione API key

## 🚀 Come usare

### 1. Ottenere API Key da Intervals.icu

1. Vai su https://intervals.icu/settings
2. Copia la tua **API Key personale**
3. Non condividere questa chiave

### 2. Configurare l'app

1. Avvia **bTeam**
2. Clicca su **"🔄 Sincronizza Intervals"**
3. Incolla la API key nel campo
4. Clicca **"Test connessione"** per verificare

### 3. Importare attività

1. Seleziona l'**atleta di destinazione**
2. Imposta i **giorni indietro** (es. 30 giorni)
3. Clicca **"Visualizza attività disponibili"**
4. Verifica l'anteprima
5. Clicca **"OK"** per importare

Le attività verranno scaricate e salvate nel database bTeam.

## 📊 Dati sincronizzati

Per ogni attività importa:

- 📅 Data e ora
- 🏃 Nome e tipo (Ride, Run, Swim, etc.)
- 📏 Distanza (km)
- ⏱️ Durata movimento
- 💪 Potenza media/normalizzata
- ❤️ Frequenza cardiaca (media/max)
- 📈 Training Load
- 😊 Feel rating

## 🔄 Flusso di sincronizzazione

```
Intervals.icu API
        ↓
    client_v2.py (114+ endpoint)
        ↓
    intervals_sync.py (format e save)
        ↓
    bTeam Database
        ↓
    GUI mostra le attività
```

## 🎯 Prossimi passaggi (roadmap)

### Phase 2: Scrittura dati
- Caricamento attività nuove a Intervals.icu
- Aggiornamento feel/notes
- Sincronizzazione bidirezionale

### Phase 3: Multi-atleta con OAuth
- Login atleta (OAuth 2.0)
- Accesso agli account multipli
- Gestione squadra completa

### Phase 4: Features avanzate
- Download file FIT
- Sincronizzazione wellness
- Power curve e analytics
- Workout library

## 🔐 Sicurezza

- La API key è salvata localmente in `bteam_config.json`
- Non viene mai inviata a terzi
- Cancella la key se non la usi più

## 🐛 Troubleshooting

**"Connessione fallita"**
- Verifica che la API key sia corretta
- Controlla la connessione internet
- Accedi a https://intervals.icu per verificare l'account

**"Nessuna attività trovata"**
- Aumenta i giorni indietro
- Verifica che l'account abbia attività

**Errore durante l'import**
- Riprova con meno giorni
- Controlla i log della console

## 📝 Note tecniche

### File importanti

- `intervals_client_v2.py` - Client OAuth-ready, pronto per fase 3
- `intervals_sync.py` - Logica di sincronizzazione (facilmente estendibile)
- `config_bteam.py` - Gestione configurazione centralizz ata
- `bteam_config.json` - Salva API key (Git-ignored)

### Endpoints disponibili

Il client supporta:
- ✅ Lettura attività (`get_activities`, `get_activity`)
- ✅ Lettura dati atleta (`get_athlete`)
- ✅ Lettura wellness
- ✅ Lettura calendario/eventi
- ✅ Power curve
- ⏳ Scrittura attività (Phase 2)
- ⏳ OAuth flow (Phase 3)

## 💡 Suggerimenti per estensioni

```python
# Esempio: estendere sync_service per wellness
wellness, msg = sync_service.fetch_wellness(days_back=7)

# Esempio: estendere per athlete info
athlete, msg = sync_service.fetch_athlete_info()

# Esempio: power curve
power_curve, msg = sync_service.fetch_power_curve()
```
