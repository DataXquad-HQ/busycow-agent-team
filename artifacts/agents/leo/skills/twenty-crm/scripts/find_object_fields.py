"""
Find all custom fields on a given object in Twenty CRM metadata API.
Handles the 10-item cap by paginating with notIn filter.
Verified working 2026-06-15.

Usage: python3 find_object_fields.py
"""
import subprocess, json

# Edit this to target a different object
TARGET_OBJECT_ID = "5ae439de-e1d6-40f1-846b-a4b482ad665a"  # person
# OTHER KNOWN IDs:
# company:     b77d396f-68cf-4ba4-a4ba-c423eed3a922
# opportunity: 61788876-89f8-4ac5-be6d-3d2fb7111b3c
# partnership: 7ef607fd-6b4d-4b87-ab96-60393f06af33
# engagement:  5de654a0-96b3-484a-b80e-b35b5b276a6d
# task:        a0ef39a6-8619-4ab7-a6ce-db4b85a33c81


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


# Collect ALL custom fields by paginating with notIn
seen_ids = set()
all_fields = []

for _ in range(10):  # max 10 pages of 10
    ids_json = json.dumps(list(seen_ids)) if seen_ids else "[]"
    filter_clause = f'objectMetadataId: {{ eq: "{TARGET_OBJECT_ID}" }}, isCustom: {{ is: true }}'
    if seen_ids:
        filter_clause += f', id: {{ notIn: {ids_json} }}'

    r = meta_raw({"query": f"""
    {{
      fields(filter: {{ {filter_clause} }}) {{
        edges {{ node {{ id name type options }} }}
      }}
    }}
    """})

    if "errors" in r:
        print(f"Error: {r['errors'][0]['message']}")
        break

    edges = r["data"]["fields"]["edges"]
    new_fields = [e["node"] for e in edges if e["node"]["id"] not in seen_ids]
    if not new_fields:
        break

    for n in new_fields:
        seen_ids.add(n["id"])
        all_fields.append(n)

    if len(edges) < 10:
        break  # last page

print(f"\nTotal custom fields found: {len(all_fields)}")
for n in sorted(all_fields, key=lambda x: x["name"]):
    opts = n.get("options") or []
    opts_str = f"  [{', '.join(o['value'] for o in opts)}]" if opts else ""
    print(f"  {n['id']}  {n['name']:35s} {n['type']:20s}{opts_str}")
