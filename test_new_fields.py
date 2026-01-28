#!/usr/bin/env python3
"""Test script to verify that new activity fields are being saved correctly."""

import json
from pathlib import Path
from storage_bteam import BTeamStorage, Activity

# Initialize storage
data_dir = Path.home() / "bFactor Project" / "bTeam"
storage = BTeamStorage(data_dir)

# Get all activities
activities = storage.list_activities()

print(f"Total activities in database: {len(activities)}\n")

if activities:
    # Show first activity with all fields
    first_activity = activities[0]
    print("=" * 80)
    print(f"Sample Activity: {first_activity['title']}")
    print("=" * 80)
    
    for key, value in first_activity.items():
        if key == "intervals_payload" and value:
            # Show only the first 200 chars of payload
            payload_str = value[:200] + "..." if len(value) > 200 else value
            print(f"  {key}: {payload_str}")
        elif key == "tags" and isinstance(value, list):
            print(f"  {key}: {value} (parsed as list)")
        else:
            print(f"  {key}: {value}")
    
    # Check which activities have race flags or tags
    print("\n" + "=" * 80)
    print("Activities with special flags:")
    print("=" * 80)
    
    races = [a for a in activities if a.get("is_race")]
    tagged = [a for a in activities if a.get("tags") and len(a.get("tags", [])) > 0]
    
    print(f"\n✓ Activities marked as races: {len(races)}")
    for activity in races[:5]:  # Show first 5
        tags = activity.get("tags", [])
        print(f"  - {activity['title']} (tags: {tags})")
    
    print(f"\n✓ Activities with tags: {len(tagged)}")
    for activity in tagged[:5]:  # Show first 5
        tags = activity.get("tags", [])
        print(f"  - {activity['title']} (tags: {tags})")
    
    # Check for power/HR data
    print("\n" + "=" * 80)
    print("Activities with power/HR data:")
    print("=" * 80)
    
    power_activities = [a for a in activities if a.get("avg_watts")]
    hr_activities = [a for a in activities if a.get("avg_hr")]
    
    print(f"\n✓ Activities with power data: {len(power_activities)}")
    for activity in power_activities[:5]:
        avg_w = activity.get("avg_watts")
        norm_w = activity.get("normalized_watts")
        print(f"  - {activity['title']}: avg={avg_w}W, norm={norm_w}W")
    
    print(f"\n✓ Activities with HR data: {len(hr_activities)}")
    for activity in hr_activities[:5]:
        avg_hr = activity.get("avg_hr")
        max_hr = activity.get("max_hr")
        print(f"  - {activity['title']}: avg={avg_hr}bpm, max={max_hr}bpm")

print("\n✓ Test complete!")
