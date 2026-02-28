#!/usr/bin/env python3
import sys
sys.path.insert(0, 'webapp')

from shared.storage import get_storage

race = get_storage().get_race(1)
if race:
    print(f"Race: {race['name']}")
    print(f"Number of stages: {len(race.get('stages', []))}")
    if race.get('stages'):
        for stage in race.get('stages', []):
            print(f"  Stage {stage['stage_number']}: {stage['distance_km']}km, elevation: {stage['elevation_m']}m" if stage['elevation_m'] else f"  Stage {stage['stage_number']}: {stage['distance_km']}km")
    else:
        print("  (no stages)")
else:
    print("Race not found")
