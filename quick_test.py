from storage_bteam import BTeamStorage
from pathlib import Path

# Initialize storage
data_dir = Path.home() / 'bFactor Project' / 'bTeam'
storage = BTeamStorage(data_dir)

# Get all activities
activities = storage.list_activities()

print(f'Total activities in database: {len(activities)}')

if activities:
    first = activities[0]
    print(f'\nFirst activity: {first["title"]}')
    print(f'  is_race: {first.get("is_race")}')
    print(f'  tags: {first.get("tags")}')
    print(f'  avg_watts: {first.get("avg_watts")}')
    print(f'  avg_hr: {first.get("avg_hr")}')
    print(f'  activity_type: {first.get("activity_type")}')
    print(f'  duration_minutes: {first.get("duration_minutes")}')
    print(f'  source: {first.get("source")}')
