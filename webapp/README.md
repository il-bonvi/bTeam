# 🚴 bTeam WebApp

Applicazione web moderna per la gestione di team e atleti di ciclismo con integrazione Intervals.icu.

## 📋 Caratteristiche

- **Gestione Squadre**: Crea e gestisci multiple squadre
- **Gestione Atleti**: Anagrafica completa degli atleti con dati fisici e prestazionali
- **Attività**: Tracciamento di tutte le attività di allenamento e gare
- **Gare**: Pianificazione e gestione gare con atleti partecipanti
- **Wellness**: Monitoraggio dati wellness quotidiani (peso, FC, HRV, sonno, etc.)
- **Sincronizzazione Intervals.icu**: Importa attività e wellness da Intervals.icu
- **API RESTful**: Backend FastAPI con documentazione automatica
- **Interfaccia Moderna**: Design responsivo e intuitivo

## 🏗️ Struttura Progetto

```
webapp/
├── backend/                    # Backend FastAPI
│   ├── app.py                 # Applicazione principale
│   └── __init__.py
├── modules/                    # Moduli funzionali
│   ├── teams/                 # Gestione squadre
│   │   ├── backend/
│   │   │   └── teams_routes.py
│   │   └── frontend/
│   │       ├── html/
│   │       ├── js/
│   │       └── css/
│   ├── athletes/              # Gestione atleti
│   │   ├── backend/
│   │   │   └── athletes_routes.py
│   │   └── frontend/
│   ├── activities/            # Gestione attività
│   │   ├── backend/
│   │   │   └── activities_routes.py
│   │   └── frontend/
│   ├── races/                 # Gestione gare
│   │   ├── backend/
│   │   │   └── races_routes.py
│   │   └── frontend/
│   ├── wellness/              # Dati wellness
│   │   ├── backend/
│   │   │   └── wellness_routes.py
│   │   └── frontend/
│   └── sync/                  # Sincronizzazione Intervals.icu
│       ├── backend/
│       │   └── sync_routes.py
│       └── frontend/
├── static/                     # File statici
│   ├── css/
│   │   └── main.css           # Stili principali
│   ├── js/
│   │   ├── api.js             # Client API
│   │   ├── utils.js           # Utility functions
│   │   └── app.js             # Applicazione principale
│   └── images/
├── templates/                  # Template HTML
│   └── index.html             # Pagina principale
├── api_docs/                   # Documentazione API
├── config/                     # Configurazioni
└── data/                       # Database SQLite
```

## 🚀 Installazione

### Prerequisiti

- Python 3.8+
- pip

### Passi di Installazione

1. **Installa le dipendenze**

```bash
cd webapp
pip install -r requirements.txt
```

2. **Avvia il server**

```bash
python backend/app.py
```

Oppure con uvicorn:

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

3. **Apri il browser**

Naviga a: `http://localhost:8000`

## 📚 Documentazione API

Una volta avviato il server, la documentazione interattiva delle API è disponibile a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 Configurazione

### Intervals.icu API Key

Per utilizzare la sincronizzazione con Intervals.icu:

1. Ottieni la tua API key da https://intervals.icu/settings
2. Vai alla sezione "Sincronizzazione" nell'app
3. Incolla la tua API key e testa la connessione
4. Importa le attività selezionando l'atleta e il periodo desiderato

## 📖 Utilizzo

### Gestione Squadre

1. Clicca su "Squadre" nella barra laterale
2. Clicca "Nuova Squadra" per aggiungere una squadra
3. Compila il nome e salva

### Gestione Atleti

1. Clicca su "Atleti" nella barra laterale
2. Clicca "Nuovo Atleta" per aggiungere un atleta
3. Compila i dati anagrafici e fisici
4. Seleziona la squadra di appartenenza
5. Opzionalmente aggiungi l'API key di Intervals.icu per la sincronizzazione

### Sincronizzazione Attività

1. Vai alla sezione "Sincronizzazione"
2. Inserisci l'API key di Intervals.icu
3. Seleziona l'atleta di destinazione
4. Imposta il periodo (giorni indietro)
5. Clicca "Sincronizza Attività"

### Gestione Gare

1. Vai alla sezione "Gare"
2. Crea una nuova gara con nome, data, distanza
3. Aggiungi atleti partecipanti
4. Opzionalmente puoi pushare la gara su Intervals.icu

## 🎨 Personalizzazione

### Temi e Stili

I colori e stili sono definiti in `static/css/main.css` usando variabili CSS:

```css
:root {
    --primary-color: #2c7a7b;
    --secondary-color: #ed8936;
    /* ... altre variabili */
}
```

### Aggiungere Nuovi Moduli

1. Crea una nuova cartella in `modules/`
2. Aggiungi `backend/` con i route handlers
3. Aggiungi `frontend/` con HTML, JS, CSS
4. Registra il router in `backend/app.py`
5. Aggiungi il link nella sidebar di `templates/index.html`

## 🔒 Sicurezza

- Le API key vengono salvate solo nel database locale
- Nessun dato viene inviato a server terzi (eccetto Intervals.icu quando richiesto)
- Tutte le comunicazioni con Intervals.icu avvengono tramite HTTPS
- In produzione, configura CORS appropriatamente in `backend/app.py`

## 🐛 Troubleshooting

### Il server non parte

- Verifica che tutte le dipendenze siano installate: `pip install -r requirements.txt`
- Controlla che la porta 8000 non sia già in uso

### Errore di connessione con Intervals.icu

- Verifica che l'API key sia corretta
- Controlla la connessione internet
- Assicurati che l'account Intervals.icu sia attivo

### Database non trovato

- Il database viene creato automaticamente in `webapp/data/bteam.db`
- Se ci sono errori, elimina il file e riavvia l'app

## 📦 Dipendenze Principali

- **FastAPI**: Framework web moderno e veloce
- **Uvicorn**: Server ASGI per FastAPI
- **SQLAlchemy**: ORM per database
- **Pydantic**: Validazione dati
- **requests**: Client HTTP per Intervals.icu

## 🤝 Contributi

Questo è un progetto proprietario. Per informazioni sui contributi, contatta il maintainer.

## 📄 Licenza

```
Copyright (c) 2026 Andrea Bonvicin - bFactor Project
PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
Sharing, distribution or reproduction is strictly prohibited.
La condivisione, distribuzione o riproduzione è severamente vietata.
```

## 📞 Supporto

Per supporto e domande, consulta la documentazione completa in `api_docs/`.

---

**Versione**: 1.0.0  
**Data**: 2026-02-13  
**Status**: ✅ Production Ready
