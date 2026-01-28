# 🚀 bTeam - Standalone App

## Avvio diretto

### Metodo 1: File Batch (Windows)

```bash
# Doppio click
run.bat

# Con tema specifico
run.bat "Dark Blue"
```

### Metodo 2: PowerShell

```powershell
.\run.ps1
.\run.ps1 -Theme "Dark Blue"
```

### Metodo 3: Python diretto

```bash
python main.py
python main.py --theme "Dark Blue"
```

---

## 🎨 Temi disponibili

- Forest Green (default)
- Dark Blue
- Ocean
- Sunset
- Midnight

---

## 📦 Contenuto

| File | Descrizione |
|------|-------------|
| `main.py` | Entry point Python |
| `run.bat` | Launcher batch Windows |
| `run.ps1` | Launcher PowerShell |
| `gui_bteam.py` | GUI principale |
| `intervals_sync.py` | Sincronizzazione Intervals |
| `config_bteam.py` | Configurazione |
| `storage_bteam.py` | Database |
| `bteam_config.json` | Config file |

---

## 🚀 Copia-Incolla in altre posizioni

Tutta l'app bTeam è contenuta in questa cartella. Puoi:

1. Copiare l'intera cartella `bTeam` altrove
2. Eseguire `run.bat` da Windows
3. Eseguire `.\run.ps1` da PowerShell
4. Eseguire `python main.py` da terminale

Non è necessario il launcher principale o altri file del progetto.

---

## 💡 Sviluppo

```bash
# Avvia l'app
python main.py

# In un'altra finestra, test
python test_intervals_proto.py
```

---

## 📚 Documentazione

- **[INTERVALS_GUIDE.md](INTERVALS_GUIDE.md)** - Guida completa integrazione Intervals.icu
- **[API_GUIDE.md](API_GUIDE.md)** - Riferimento API completo

---

**Created**: 2026-01-28  
**Status**: ✅ Standalone Ready
