# 🔄 Guida Integrazione Intervals.icu - WebApp

## Panoramica

bTeam WebApp si integra completamente con Intervals.icu per sincronizzare attività, dati wellness e pushare gare pianificate.

## 🔑 Ottenere l'API Key

1. Accedi a [Intervals.icu](https://intervals.icu)
2. Vai in **Settings** (Impostazioni)
3. Scorri fino alla sezione **Developer**
4. Copia la tua **API Key** personale
5. **IMPORTANTE**: Non condividere mai questa chiave

## 🚀 Utilizzo nell'App

### 1. Test Connessione

Nella sezione "Sincronizzazione" dell'app:

1. Incolla la tua API Key nel campo
2. Clicca "Testa Connessione"
3. Se la connessione è corretta, vedrai il tuo nome atleta

**API Endpoint:**
```
POST /api/sync/test-connection
Body: { "api_key": "your_key" }
```

### 2. Sincronizzazione Attività

Importa attività da Intervals.icu nel database bTeam:

1. Seleziona l'**atleta** di destinazione nel database
2. Inserisci la **API Key**
3. Imposta **giorni indietro** (es. 30 per ultimo mese)
4. Clicca "Sincronizza Attività"

**Dati Importati per Attività:**
- Nome e descrizione
- Data e ora
- Tipo (Ride, Run, VirtualRide, etc.)
- Distanza (km)
- Durata (minuti)
- Potenza media e normalizzata
- Frequenza cardiaca media e max
- Training Load (TSS)
- Intensità
- Feel rating (1-10)
- Cadenza media
- Calorie

**API Endpoint:**
```
POST /api/sync/activities
Body: {
  "athlete_id": 1,
  "api_key": "your_key",
  "days_back": 30,
  "include_intervals": true
}
```

### 3. Sincronizzazione Wellness

Importa dati wellness quotidiani:

1. Seleziona l'**atleta** di destinazione
2. Inserisci la **API Key**
3. Imposta **giorni indietro** (es. 7 per ultima settimana)
4. Clicca "Sincronizza Wellness"

**Dati Importati per Wellness:**
- Peso corporeo
- Frequenza cardiaca a riposo
- HRV (Heart Rate Variability)
- Passi giornalieri
- Dolori muscolari (soreness)
- Fatica
- Stress mentale
- Umore
- Motivazione
- Durata e qualità del sonno
- Score sonno
- Commenti

**API Endpoint:**
```
POST /api/sync/wellness
Body: {
  "athlete_id": 1,
  "api_key": "your_key",
  "days_back": 7
}
```

### 4. Push Gare

Pusha gare pianificate su Intervals.icu come eventi:

1. Vai nella sezione "Gare"
2. Seleziona una gara
3. Clicca "Push su Intervals.icu"
4. Inserisci la **API Key**
5. Conferma

La gara verrà creata su Intervals.icu come:
- **Tipo**: RACE event
- **Data**: Data della gara alle 10:00
- **Nome**: Nome della gara
- **Descrizione**: Distanza e categoria
- **Sport**: Ride

**API Endpoint:**
```
POST /api/sync/push-race
Body: {
  "race_id": 1,
  "api_key": "your_key"
}
```

### 5. Power Curve

Visualizza la power curve dell'atleta:

1. Seleziona un atleta
2. Inserisci la **API Key**
3. Imposta il periodo (es. 90 giorni)
4. Clicca "Carica Power Curve"

**API Endpoint:**
```
GET /api/sync/power-curve/{athlete_id}?api_key=your_key&days_back=90
```

## 🔒 Sicurezza

### Gestione API Key

- **Non salvare** l'API key nel codice frontend
- L'API key viene inviata solo quando necessario per operazioni specifiche
- Le API key degli atleti possono essere salvate nel database (campo criptato consigliato)
- In produzione, considera OAuth2 per multi-utente

### Best Practices

1. **Non condividere** la tua API key
2. **Non committare** API key nel version control
3. **Usa HTTPS** in produzione
4. **Rate limiting**: Intervals.icu ha limiti (circa 100 req/min)
5. **Rigenera** l'API key periodicamente

## 📊 Mapping Dati

### Activity Types

| Intervals.icu | bTeam |
|--------------|-------|
| Ride | Ride |
| Run | Run |
| VirtualRide | VirtualRide |
| Swim | Swim |
| WeightTraining | WeightTraining |
| Yoga | Yoga |

### Feel Rating

Scale 1-10:
- 1-3: Molto male
- 4-5: Male
- 6-7: Ok
- 8-9: Bene
- 10: Ottimo

### Training Load

Training Load (TSS) da Intervals.icu corrisponde a:
- TSS per attività ciclismo
- TRIMP per attività running
- Equivalente per altri sport

## 🐛 Troubleshooting

### Errore "Connection Failed"

**Causa**: API key non valida o connessione internet assente

**Soluzione**:
1. Verifica che l'API key sia corretta
2. Controlla la connessione internet
3. Assicurati che l'account Intervals.icu sia attivo

### Errore "No activities found"

**Causa**: Nessuna attività nel periodo selezionato

**Soluzione**:
1. Aumenta i "giorni indietro"
2. Verifica che ci siano attività su Intervals.icu

### Errore durante l'import

**Causa**: Dati mancanti o formato non valido

**Soluzione**:
1. Verifica i log del server
2. Controlla che l'atleta esista nel database
3. Riprova con meno giorni indietro

### Rate Limit Exceeded

**Causa**: Troppe richieste in breve tempo

**Soluzione**:
1. Attendi qualche minuto
2. Importa periodi più brevi
3. Non fare richieste contemporanee

## 🔗 Risorse

- [Intervals.icu API Docs](https://intervals.icu/api)
- [Intervals.icu Settings](https://intervals.icu/settings)
- [Intervals.icu Support](https://intervals.icu/support)

## 📝 Note Tecniche

### Formato Date

Intervals.icu usa ISO 8601:
- Date: `YYYY-MM-DD`
- DateTime: `YYYY-MM-DDTHH:MM:SS`

### Timezone

Le date sono in **local time** dell'atleta.

### Unità di Misura

- Distanza: metri (convertiti in km nell'app)
- Durata: secondi (convertiti in minuti)
- Potenza: watts
- FC: bpm
- Peso: kg
- Altezza: cm

---

**Ultimo Aggiornamento**: 2026-02-13  
**Compatibilità**: Intervals.icu API v1
