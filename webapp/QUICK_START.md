# 🚀 Quick Start Guide - bTeam WebApp

## Avvio Rapido in 3 Passi

### 1️⃣ Installa Dipendenze

```bash
cd webapp
pip install -r requirements.txt
```

### 2️⃣ Avvia il Server

```bash
python backend/app.py
```

Oppure con uvicorn:

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### 3️⃣ Apri il Browser

Naviga a: **http://localhost:8000**

---

## 🎯 Primi Passi

### Crea la Prima Squadra

1. Clicca su **"Squadre"** nella barra laterale
2. Clicca **"Nuova Squadra"**
3. Inserisci il nome (es. "Team Pro")
4. Salva

### Aggiungi il Primo Atleta

1. Clicca su **"Atleti"** nella barra laterale
2. Clicca **"Nuovo Atleta"**
3. Compila i dati:
   - Nome e cognome
   - Squadra
   - Data di nascita
   - Peso e altezza
   - Genere
4. Salva

### Sincronizza da Intervals.icu

1. Vai su **"Sincronizzazione"**
2. Inserisci la tua **API Key** di Intervals.icu
   - Ottienila da: https://intervals.icu/settings
3. Clicca **"Testa Connessione"**
4. Seleziona l'**atleta** di destinazione
5. Imposta **giorni indietro** (es. 30)
6. Clicca **"Sincronizza Attività"**

### Crea una Gara

1. Vai su **"Gare"**
2. Clicca **"Nuova Gara"**
3. Compila i dati:
   - Nome gara
   - Data
   - Distanza (km)
   - Categoria
   - Dislivello (opzionale)
4. Aggiungi atleti partecipanti
5. Salva

---

## 📚 Documentazione Completa

Una volta avviato il server, puoi accedere alla documentazione interattiva:

- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

---

## ⚙️ Configurazione Avanzata

### Cambiare Porta

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 3000
```

### Modalità Produzione

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Database Personalizzato

Il database SQLite viene creato automaticamente in:
```
webapp/data/bteam.db
```

Per cambiare il percorso, modifica `backend/app.py`:

```python
storage_dir = Path("/tuo/percorso/personalizzato")
```

---

## 🐛 Problemi Comuni

### "Port already in use"

**Soluzione**: Cambia porta o termina il processo che la sta usando

```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "Module not found"

**Soluzione**: Assicurati di aver installato tutte le dipendenze

```bash
pip install -r requirements.txt
```

### "Cannot connect to Intervals.icu"

**Soluzione**:
1. Verifica la tua API key
2. Controlla la connessione internet
3. Assicurati che l'account Intervals.icu sia attivo

---

## 🎨 Personalizzazione

### Cambiare Colori

Modifica le variabili CSS in `static/css/main.css`:

```css
:root {
    --primary-color: #2c7a7b;  /* Colore principale */
    --secondary-color: #ed8936; /* Colore secondario */
}
```

### Aggiungere Logo

Inserisci il tuo logo in `static/images/logo.png` e modifica `templates/index.html`:

```html
<div class="sidebar-header">
    <img src="/static/images/logo.png" alt="Logo" width="40">
    <h1>bTeam</h1>
</div>
```

---

## 📞 Supporto

Per domande e supporto:

1. Consulta la [documentazione completa](README.md)
2. Leggi l'[API Reference](api_docs/API_REFERENCE.md)
3. Vedi la [guida Intervals.icu](api_docs/INTERVALS_INTEGRATION.md)

---

## ✅ Checklist Setup

- [ ] Python 3.8+ installato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)
- [ ] Server avviato senza errori
- [ ] Browser aperto su http://localhost:8000
- [ ] Prima squadra creata
- [ ] Primo atleta aggiunto
- [ ] (Opzionale) API Key Intervals.icu configurata
- [ ] (Opzionale) Attività sincronizzate

---

**Buon allenamento con bTeam! 🚴‍♂️**
