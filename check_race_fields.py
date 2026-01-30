import json
spec = json.load(open('INFO/openapi-spec.json'))
schema = spec['components']['schemas'].get('EventEx', {})
props = schema.get('properties', {})

print("EventEx properties rilevanti per race:")
for key in ['distance', 'moving_time', 'duration_minutes']:
    if key in props:
        print(f"\n{key}:")
        print(f"  {json.dumps(props[key], indent=4)}")
