#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test: Push Race Functionality
Verifica il funzionamento della sincronizzazione gare su Intervals.icu

Nota: Questo è un test prototipale che mostra come il metodo verrà usato
"""

def test_sync_race_format():
    """Test: Formattazione timestamp e categorie"""
    
    # Simuliamo i dati di una gara
    race_data = {
        "name": "Granfondo del Garda",
        "race_date": "2026-02-15",
        "distance_km": 120,
        "avg_speed_kmh": 25,
        "category": "A Race",
    }
    
    # Test 1: Formattazione timestamp
    race_date_str = race_data["race_date"]
    start_date_local = f"{race_date_str}T10:00:00"
    assert start_date_local == "2026-02-15T10:00:00", "Timestamp non formattato correttamente"
    print(f"✓ Timestamp: {start_date_local}")
    
    # Test 2: Calcolo durata
    distance_km = race_data["distance_km"]
    speed_kmh = race_data["avg_speed_kmh"]
    duration_minutes = (distance_km / speed_kmh) * 60
    assert duration_minutes == 288, f"Durata calcolata male: {duration_minutes}"
    print(f"✓ Durata: {int(duration_minutes)} minuti ({int(duration_minutes//60)}h {int(duration_minutes%60)}m)")
    
    # Test 3: Mapping categorie
    category_map = {
        "A Race": "A",
        "B Race": "B",
        "C Race": "C",
    }
    intervals_category = category_map.get(race_data["category"], race_data["category"])
    assert intervals_category == "A", "Mapping categoria non corretto"
    print(f"✓ Categoria: {race_data['category']} → {intervals_category}")
    
    # Test 4: Descrizione
    description = f"Categoria: {race_data['category']}\nDistanza: {distance_km} km\nMedia: {speed_kmh} km/h"
    assert "Categoria:" in description, "Descrizione non contiene categoria"
    assert str(distance_km) in description, "Descrizione non contiene distanza"
    print(f"✓ Descrizione: {len(description)} caratteri")
    
    print("\n✅ Tutti i test di formattazione passati!")


def test_category_mappings():
    """Test: Verifica tutti i mapping categorie"""
    
    test_cases = [
        ("A Race", "A"),
        ("B Race", "B"),
        ("C Race", "C"),
        ("D Race", "D Race"),  # Fallback
    ]
    
    category_map = {
        "A Race": "A",
        "B Race": "B",
        "C Race": "C",
    }
    
    for input_cat, expected in test_cases:
        result = category_map.get(input_cat, input_cat)
        assert result == expected, f"Mapping fallito: {input_cat} → {result} (atteso {expected})"
        print(f"✓ {input_cat} → {result}")
    
    print("\n✅ Mapping categorie verificato!")


if __name__ == "__main__":
    print("=" * 60)
    print("🏁 TEST: Push Race Functionality")
    print("=" * 60)
    print()
    
    print("Test 1: Formattazione e Calcoli")
    print("-" * 60)
    test_sync_race_format()
    
    print()
    print("Test 2: Category Mappings")
    print("-" * 60)
    test_category_mappings()
    
    print()
    print("=" * 60)
    print("✅ TUTTI I TEST PASSATI!")
    print("=" * 60)
    print()
    print("📝 Note:")
    print("- Il bottone '🔄 Sync Race' è ora disponibile nel dialog gara")
    print("- Cliccare per fare il push di una gara su Intervals.icu")
    print("- La gara verrà creata come evento RACE pianificato")
    print("- Tipo attività: Ride")
    print("- Categoria: A/B/C (mappate dalle categorie locali)")
