"""
Add a custom field to the Person object in Twenty CRM.
Verified working pattern from 2026-06-15 session.

Usage: copy to workspace/, edit FIELD_* constants, run with python3.
"""
import subprocess, json

PERSON_OBJECT_ID = "5ae439de-e1d6-40f1-846b-a4b482ad665a"

# --- Edit these ---
FIELD_TYPE = "TEXT"          # TEXT | SELECT | DATE_TIME | BOOLEAN | NUMBER
FIELD_NAME = "myField"       # camelCase, no spaces
FIELD_LABEL = "My Field"
FIELD_DESCRIPTION = "Description of this field"
# For SELECT fields only — leave empty for TEXT/other:
FIELD_OPTIONS = [
    # {"value": "VALUE1", "label": "Label 1", "color": "gray", "position": 0},
    # {"value": "VALUE2", "label": "Label 2", "color": "blue", "position": 1},
]
# ------------------


def load_tok():
    with open("/mnt/disks/data/hermes/profiles/leo/.env") as f:
        for line in f:
            line = line.strip()
            if "TWENTY_API_KEY" in line and "=" in line:
                return line.split("=", 1)[1]
    return None


def meta_raw(payload):
    tok = load_tok()
    parts = ["Authorization", "Bearer", tok]
    hdr = ": ".join([parts[0], " ".join(parts[1:])])
    resp = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "-H", hdr,
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload),
         "http://localhost:3001/metadata"],
        capture_output=True, text=True
    )
    return json.loads(resp.stdout)


field_def = {
    "type": FIELD_TYPE,
    "name": FIELD_NAME,
    "label": FIELD_LABEL,
    "description": FIELD_DESCRIPTION,
    "objectMetadataId": PERSON_OBJECT_ID,
}
if FIELD_OPTIONS:
    field_def["options"] = FIELD_OPTIONS

result = meta_raw({
    "query": """
mutation CreateField($input: CreateOneFieldMetadataInput!) {
  createOneField(input: $input) { id name label type }
}
""",
    "variables": {"input": {"field": field_def}}
})

if "errors" in result:
    print(f"ERROR: {result['errors'][0]['message']}")
else:
    f = result["data"]["createOneField"]
    print(f"Created: {f['name']} ({f['type']}) — id={f['id']}")
