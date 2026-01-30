#!/usr/bin/env python3
"""
🔧 FIX: Sincronizzazione Attività da Atleta - BUG RISOLTO

PROBLEMA:
  AttributeError: 'list' object has no attribute 'get'
  
  fetch_activities() restituisce una TUPLA (lista, messaggio)
  Non una semplice lista

SOLUZIONE IMPLEMENTATA:
  • Corretto unpacking della tupla
  • Aggiunto loop corretto su activities
  • Gestione errori per singole attività
  • Messaggi di feedback migliorati
"""

print("""
✅ FIX: Metodo _sync_intervals() Corretto
═════════════════════════════════════════════════════════════════

ERRORE ORIGINALE:
─────────────────────────────────────────────────────────────

  Traceback:
  File "...dialog_athletes.py", line 272, in _sync_intervals
    formatted = IntervalsSyncService.format_activity_for_storage(activity)
    ^^^^^^^^^^^^
  AttributeError: 'list' object has no attribute 'get'

CAUSA:
─────────────────────────────────────────────────────────────

  sync_service.fetch_activities() RESTITUISCE:
  
    (lista_attività, messaggio_stato)
  
  Invece di:
  
    lista_attività


SOLUZIONE:
─────────────────────────────────────────────────────────────

1. Unpacking corretto della tupla:
   
   # PRIMA (SBAGLIATO):
   activities = sync_service.fetch_activities(days_back=30)
   
   # DOPO (CORRETTO):
   activities, status_msg = sync_service.fetch_activities(days_back=30)

2. Ciclo corretto su attività:
   
   for activity in activities:  # Ora 'activity' è un dict
       formatted = IntervalsSyncService.format_activity_for_storage(activity)
       # ... salva nel database

3. Gestione errori per singola attività:
   
   imported_count = 0
   for activity in activities:
       try:
           # ... processa
           imported_count += 1
       except Exception as e:
           print(f"Errore: {e}")
           continue

4. Messaggi di feedback migliorati:
   
   QMessageBox.information(
       self,
       "✓ Sincronizzazione completata",
       f"Importate {imported_count} attività da Intervals.icu"
   )


MODIFICHE AL FILE:
─────────────────────────────────────────────────────────────

✏️ dialogs/dialog_athletes.py

   Modified _sync_intervals():
   • Unpacking corretto della tupla da fetch_activities()
   • Loop con try-except per gestire errori singole attività
   • Contatore delle attività importate
   • Messaggi di feedback migliorati
   • Ordine logico: connessione → fetch → save


TESTING:
─────────────────────────────────────────────────────────────

1. Apri Dettagli di un atleta
2. Aggiungi API key
3. Clicca "🔄 Sincronizza Intervals"
4. Risultato atteso:
   ├─ ✓ Connessione OK
   ├─ Scaricamento attività...
   ├─ Importazione nel database
   └─ "✓ Sincronizzazione completata - Importate N attività"


STRUTTURA TUPLA:
─────────────────────────────────────────────────────────────

fetch_activities() restituisce:

  (
    [
      {
        'id': '123',
        'name': 'Morning Ride',
        'distance': 45000,  # in metri
        'moving_time': 7200,  # in secondi
        'start_date_local': '2026-01-30T08:00:00',
        ...
      },
      {
        'id': '124',
        'name': 'Evening Run',
        ...
      }
    ],
    '✅ Sincronizzate 2 attività da Intervals.icu'
  )


═════════════════════════════════════════════════════════════════
✅ BUG RISOLTO - PRONTO PER USO
═════════════════════════════════════════════════════════════════
""")
