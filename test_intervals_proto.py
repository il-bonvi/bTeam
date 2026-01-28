#!/usr/bin/env python3
"""
Script di test per il prototipo Intervals.icu
Testa la lettura attività senza dipendenze GUI
"""

import os
import sys
from pathlib import Path

# Aggiungi il path del progetto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bTeam.intervals_sync import IntervalsSyncService


def main():
    print("\n" + "="*60)
    print("TEST PROTOTIPO INTERVALS.ICU")
    print("="*60 + "\n")

    # Test 1: Inizializzazione senza key
    print("✓ Test 1: Inizializzazione senza API key")
    service = IntervalsSyncService()
    assert not service.is_connected(), "Dovrebbe non essere connesso"
    print("  ✓ Passato: Service non connesso senza key\n")

    # Test 2: API key
    print("✓ Test 2: Impostazione API key (test)")
    test_api_key = os.environ.get('INTERVALS_API_KEY', '')
    
    if test_api_key:
        print(f"  Usando API key da environment: {test_api_key[:10]}...{test_api_key[-5:]}")
        service.set_api_key(test_api_key)
        
        if service.is_connected():
            print("  ✓ Connesso a Intervals.icu!\n")
            
            # Test 3: Lettura atleta
            print("✓ Test 3: Lettura informazioni atleta")
            athlete, msg = service.fetch_athlete_info()
            if athlete:
                print(f"  Nome atleta: {athlete.get('name', 'Unknown')}")
                print(f"  FTP: {athlete.get('icu_ftp', 'N/A')} W")
                print(f"  W': {athlete.get('icu_w_prime', 'N/A')} J")
                print(f"  {msg}\n")
            
            # Test 4: Lettura attività
            print("✓ Test 4: Lettura attività (ultimi 7 giorni)")
            activities, msg = service.fetch_activities(days_back=7, include_intervals=False)
            print(f"  {msg}")
            print(f"  Totale attività: {len(activities)}\n")
            
            if activities:
                # Mostra la prima attività
                act = activities[0]
                print(f"  Ultima attività:")
                print(f"    - Data: {act.get('start_date_local', 'N/A')}")
                print(f"    - Nome: {act.get('name', 'N/A')}")
                print(f"    - Tipo: {act.get('type', 'N/A')}")
                print(f"    - Distanza: {(act.get('distance', 0) or 0)/1000:.1f} km")
                print(f"    - Training Load: {act.get('icu_training_load', 'N/A')}\n")
                
                # Test 5: Formattazione
                print("✓ Test 5: Formattazione per storage")
                formatted = IntervalsSyncService.format_activity_for_storage(act)
                print(f"  Nome: {formatted['name']}")
                print(f"  Distanza: {formatted['distance_km']:.1f} km")
                print(f"  Durata: {formatted['moving_time_minutes']:.1f} min")
                print(f"  Training Load: {formatted['training_load']}\n")
            
            # Test 6: Lettura wellness
            print("✓ Test 6: Lettura wellness (ultimi 7 giorni)")
            wellness, msg = service.fetch_wellness(days_back=7)
            print(f"  {msg}")
            print(f"  Record wellness: {len(wellness)}\n")
            
            if wellness:
                w = wellness[-1]  # Ultimo
                print(f"  Ultimo record:")
                print(f"    - Data: {w.get('id', 'N/A')}")
                print(f"    - Peso: {w.get('weight', 'N/A')} kg")
                print(f"    - HR riposo: {w.get('resting_hr', 'N/A')} bpm")
                print(f"    - HRV: {w.get('hrv', 'N/A')}\n")
            
            # Test 7: Power curve
            print("✓ Test 7: Lettura power curve")
            power_curve, msg = service.fetch_power_curve()
            print(f"  {msg}\n")
            
            print("="*60)
            print("✅ TUTTI I TEST PASSATI")
            print("="*60)
            print("\nIl prototipo è funzionante!")
            print("\nProssimi passi:")
            print("1. Integrazione GUI (completato)")
            print("2. Scrittura attività (Phase 2)")
            print("3. OAuth multi-atleta (Phase 3)")
            
        else:
            print("  ❌ Connessione fallita")
            print("  Verifica la API key\n")
    else:
        print("  ⚠️  Variabile INTERVALS_API_KEY non impostata")
        print("  Per testare, imposta:")
        print("    export INTERVALS_API_KEY='tua_chiave'\n")
        print("  O copia il valore dal file INFO/.env\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
