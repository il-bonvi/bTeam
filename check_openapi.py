import json

spec = json.load(open('INFO/openapi-spec.json'))
path_item = spec['paths'].get('/api/v1/athlete/{id}/events', {})
post_op = path_item.get('post', {})
req_body = post_op.get('requestBody', {})
content = req_body.get('content', {})
schema = content.get('application/json', {}).get('schema', {})

print("[POST /api/v1/athlete/{id}/events]")
print("\nRequest Body Schema:")
if schema:
    # Check if it's a $ref
    if '$ref' in schema:
        print(f"Reference: {schema['$ref']}")
        # Extract and print
        ref_path = schema['$ref'].replace('#/components/schemas/', '')
        component_schema = spec.get('components', {}).get('schemas', {}).get(ref_path, {})
        print(json.dumps(component_schema, indent=2)[:3000])
    else:
        print(json.dumps(schema, indent=2)[:3000])
else:
    print("No schema found")
