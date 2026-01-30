#!/usr/bin/env python
from intervals_client_v2 import IntervalsAPIClient
from config_bteam import load_config

config = load_config()
api_key = config.get('intervals_api_key')

if api_key:
    client = IntervalsAPIClient(api_key=api_key)
    
    # Recupera gli ultimi eventi creati
    print("[TEST] Recupero ultimi eventi creati...")
    events = client.get_events(athlete_id='0', days_forward=60)
    
    if events:
        for i, evt in enumerate(events[:3]):  # Mostra primi 3
            print(f"\nEvent {i+1}:")
            print(f"  ID: {evt.get('id')}")
            print(f"  Category: {evt.get('category')}")
            print(f"  Name: {evt.get('name')}")
            print(f"  Type: {evt.get('type')}")
            print(f"  Start: {evt.get('start_date_local')}")
    else:
        print("No events found")
else:
    print("No API key")
