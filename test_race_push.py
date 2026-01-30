#!/usr/bin/env python
from intervals_client_v2 import IntervalsAPIClient
from config_bteam import load_config
from datetime import datetime, timedelta

config = load_config()
api_key = config.get('intervals_api_key')

if api_key:
    client = IntervalsAPIClient(api_key=api_key)
    
    # Test con RACE_B - payload minimo
    print("[TEST 1] RACE_B con solo campi essenziali...")
    try:
        start = datetime.fromisoformat('2026-03-10T10:00:00')
        end = start + timedelta(hours=3)
        result = client.create_event(
            athlete_id='0',
            category='RACE_B',
            start_date_local='2026-03-10T10:00:00',
            end_date_local=end.isoformat(),
            name='Test B Race'
        )
        print(f"[SUCCESS] Event ID: {result.get('id')}, Category: {result.get('category')}")
    except Exception as e:
        print(f"[ERROR] {e}\n")
    
    # Test con RACE_B - con type
    print("[TEST 2] RACE_B con type='Ride'...")
    try:
        start = datetime.fromisoformat('2026-03-11T10:00:00')
        end = start + timedelta(hours=3)
        result = client.create_event(
            athlete_id='0',
            category='RACE_B',
            start_date_local='2026-03-11T10:00:00',
            end_date_local=end.isoformat(),
            name='Test B Race 2',
            activity_type='Ride'
        )
        print(f"[SUCCESS] Event ID: {result.get('id')}, Category: {result.get('category')}")
    except Exception as e:
        print(f"[ERROR] {e}\n")
        
    # Test con RACE_B - con description
    print("[TEST 3] RACE_B con description...")
    try:
        start = datetime.fromisoformat('2026-03-12T10:00:00')
        end = start + timedelta(hours=3)
        result = client.create_event(
            athlete_id='0',
            category='RACE_B',
            start_date_local='2026-03-12T10:00:00',
            end_date_local=end.isoformat(),
            name='Test B Race 3',
            description='Test description',
            activity_type='Ride'
        )
        print(f"[SUCCESS] Event ID: {result.get('id')}, Category: {result.get('category')}")
    except Exception as e:
        print(f"[ERROR] {e}\n")
else:
    print("No API key found")
