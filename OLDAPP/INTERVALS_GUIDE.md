# 🎉 bTeam - Integrazione Intervals.icu

## 🚀 Quick Start

### 1. Ottenere API Key
1. Vai su https://intervals.icu/settings
2. Copia la tua API Key personale
3. Non condividere questa chiave

### 2. Configurare bTeam
1. Avvia **bTeam**
2. Clicca su **"🔄 Sincronizza Intervals"**
3. Incolla la API key
4. Clicca **"Test connessione"** per verificare

### 3. Importare Attività
1. Seleziona l'**atleta di destinazione**
2. Imposta i **giorni indietro** (es. 30 giorni)
3. Clicca **"Visualizza attività disponibili"**
4. Verifica l'anteprima
5. Clicca **"OK"** per importare

✅ Le attività sono ora nel database bTeam!

## 📦 Componenti

| File | Descrizione |
|------|-------------|
| `intervals_client_v2.py` | Client API con 40+ metodi |
| `intervals_models.py` | Modelli Pydantic per validazione |
| `intervals_sync.py` | Servizio di sincronizzazione |
| `config_bteam.py` | Gestione API key |
| `gui_bteam.py` | Dialog sincronizzazione |

## 📊 Dati Sincronizzati

Per ogni attività:
- 📅 Data e ora
- 🏃 Nome, tipo, descrizione
- 📏 Distanza (km)
- ⏱️ Tempo movimento
- 💪 Potenza (media, normalizzata)
- ❤️ FC (media, max)
- 📈 Training Load, Intensità
- 😊 Feel rating (1-10)
- 🏔️ Dislivello

## 🔄 Architettura

```
GUI (gui_bteam.py)
    ↓
Config Manager (config_bteam.py)
    ↓
Sync Service (intervals_sync.py)
    ↓
API Client (intervals_client_v2.py)
    ↓
Intervals.icu API
```

## 🧪 Testing

```bash
cd bTeam
export INTERVALS_API_KEY='tua_chiave'
python test_intervals_proto.py
```

Output atteso:
```
✓ Test 1: Inizializzazione
✓ Test 2: Impostazione API key
✓ Test 3: Lettura informazioni atleta
✓ Test 4: Lettura attività
✓ Test 5: Formattazione per storage
✓ Test 6: Lettura wellness
✓ Test 7: Lettura power curve
✅ TUTTI I TEST PASSATI
```

## 💡 Esempi di Utilizzo

### Leggere Attività
```python
from intervals_sync import IntervalsSyncService

sync = IntervalsSyncService(api_key='tua_chiave')
activities, msg = sync.fetch_activities(days_back=30)

for act in activities:
    print(f"{act['start_date_local']}: {act['name']} - {act['distance']/1000:.1f}km")
```

### Salvare nel Database
```python
formatted = IntervalsSyncService.format_activity_for_storage(activity)
storage.add_activity(
    athlete_id=1,
    title=formatted['name'],
    activity_date=formatted['start_date'],
    duration_minutes=formatted['moving_time_minutes'],
    distance_km=formatted['distance_km']
)
```

## 🔒 Sicurezza

- ✅ API key salvata **solo localmente** in `bteam_config.json`
- ✅ Non inviata a server terzi
- ✅ Password fields nei dialog
- ✅ HTTPS per API calls

## 🛣️ Roadmap

### Phase 1: Lettura Attività ✅ COMPLETATO
- [x] Client API
- [x] Modelli Pydantic
- [x] Servizio Sync
- [x] GUI Dialog
- [x] Database Integration

### Phase 2: Scrittura Dati ⏳ PROSSIMA
- [ ] Upload attività
- [ ] Update feel/notes
- [ ] Wellness sync
- [ ] Sync bidirezionale
- [x] **Push race** ← IMPLEMENTATO!
- [ ] Analisi MMP
- [ ] Analisi test
- [ ] Load analisi del sangue
- [ ] Designer settimanale (per ultimo)

### Phase 3: Multi-Atleta OAuth ⏳ FUTURA
- [ ] OAuth 2.0 flow
- [ ] Token management
- [ ] Multi-account support

## 🏁 Push Race (NUOVO!)

### Come pushare una gara su Intervals.icu

1. **Accedi a "Gestione Gare"** dal menu principale
2. **Doppio clic sulla gara** per aprire i dettagli
3. **Controlla i parametri**:
   - Nome gara
   - Data della gara
   - Distanza (km)
   - Velocità media (km/h)
   - Categoria (A/B/C Race)
4. **Clicca il bottone "🔄 Sync Race"**
5. **Conferma il push**

La gara sarà creata su Intervals.icu come:
- **Evento pianificato** (RACE)
- **Tipo di attività**: Ride
- **Data**: giorno della gara alle 10:00
- **Durata**: calcolata da distanza e velocità
- **Categoria**: A/B/C Race (salvata nelle note)

### Mapping Categorie
- A Race → Categoria A su Intervals
- B Race → Categoria B su Intervals
- C Race → Categoria C su Intervals

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

## ❓ FAQ

**D: La API key è al sicuro?**  
R: Sì, salvata solo localmente. Non viene inviata a server terzi.

**D: Posso sincronizzare più volte?**  
R: Sì, ma attento ai duplicati nel database.

**D: Come aggiungo nuovi endpoint?**  
R: Aggiungi metodo in `IntervalsAPIClient`, estendi `IntervalsSyncService`.

---

**Status**: ✅ Production Ready (Read Phase)  
**Vedi anche**: [API_GUIDE.md](API_GUIDE.md) per riferimento completo API
