# PATCH — shared/ dentro webapp/

## Obiettivo
Spostare `bTeam/shared/` dentro `bTeam/webapp/shared/` in modo che
webapp sia completamente autonoma e non dipenda da nulla all'esterno.

---

## Struttura PRIMA
```
bTeam/
├── shared/           ← codice vero qui
│   ├── __init__.py
│   ├── config.py
│   ├── storage.py
│   ├── styles.py
│   └── intervals/
│       ├── __init__.py
│       ├── client.py
│       ├── models.py
│       └── sync.py
└── webapp/
    ├── shared/       ← VUOTA
    └── backend/app.py
```

## Struttura DOPO
```
bTeam/
└── webapp/
    ├── shared/       ← codice qui dentro
    │   ├── __init__.py
    │   ├── config.py
    │   ├── storage.py
    │   ├── styles.py
    │   └── intervals/
    └── backend/app.py
```

---

## Passi da eseguire

### 1. Copia shared/ dentro webapp/
```bash
# Dalla root del progetto (bTeam/)
cp -r shared/. webapp/shared/
```

### 2. Sostituisci 3 file con quelli della patch

| File patch                              | Destinazione nel progetto                        |
|-----------------------------------------|--------------------------------------------------|
| `patch/shared/config.py`                | `webapp/shared/config.py`                        |
| `patch/webapp/backend/app.py`           | `webapp/backend/app.py`                          |
| `patch/webapp/modules/sync/sync_routes.py` | `webapp/modules/sync/sync_routes.py`          |

```bash
cp patch/shared/config.py                   webapp/shared/config.py
cp patch/webapp/backend/app.py              webapp/backend/app.py
cp patch/webapp/modules/sync/sync_routes.py webapp/modules/sync/sync_routes.py
```

### 3. Elimina la vecchia shared/ dalla root
```bash
rm -rf shared/
```

### 4. Test
```bash
cd webapp
python backend/app.py
# oppure
uvicorn backend.app:app --reload
```
Verifica: http://localhost:8000/health → `{"status": "ok"}`

---

## Cosa è cambiato nei 3 file

### `shared/config.py`
- **Nessun cambio logico**
- Il `CONFIG_FILE` path era già `parent.parent / "bteam_config.json"`
- Con shared dentro webapp, `parent.parent` ora punta a `webapp/` ✅
- Il file `bteam_config.json` verrà salvato in `webapp/bteam_config.json`
  (se ne hai già uno nella root, spostalo in `webapp/`)

### `webapp/backend/app.py`
- Rimosso `root_dir` e `sys.path.insert(0, root_dir)` → non più necessario
- Rimasto solo `webapp_dir` in sys.path (sufficiente: shared è lì dentro)

### `webapp/modules/sync/sync_routes.py`
- Rimosso `import sys` e `sys.path.insert(0, ...)` manuale → non più necessario
- Gli import `from shared.xxx` funzionano grazie al sys.path settato in app.py

---

## Se hai un bteam_config.json esistente
```bash
# Spostalo dentro webapp/
mv bteam_config.json webapp/bteam_config.json
```
