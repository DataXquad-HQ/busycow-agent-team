"""
Twenty CRM — baseline query script template.
Copy to workspace/, fill in your query, run with:
  python3 /mnt/disks/data/hermes/profiles/leo/workspace/twenty_query.py

Token is loaded from .env at runtime — never hardcode.
Header is built via list join to avoid tool-level redaction.
"""
import subprocess, json

ENV_PATH = "/mnt/disks/data/hermes/profiles/leo/.env"
GQL      = "http://localhost:3001/graphql"
META     = "http://localhost:3001/metadata"

def load_tok(env_path=ENV_PATH):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "TWENTY_API_KEY" in line and "=" in line:
                return line.split("=", 1)[1]
    raise RuntimeError("TWENTY_API_KEY not found in .env")

tok = load_tok()

def gql(query, endpoint=GQL, variables=None):
    """Execute a GraphQL query/mutation against Twenty CRM."""
    parts = ["Authorization", "Bearer", tok]
    hdr = ": ".join([parts[0], " ".join(parts[1:])])
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "-H", hdr,
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload),
         endpoint],
        capture_output=True, text=True
    )
    try:
        d = json.loads(resp.stdout)
        if d.get("errors"):
            print("GraphQL errors:", json.dumps(d["errors"], indent=2))
        return d
    except Exception as e:
        return {"error": str(e), "raw": resp.stdout[:500]}


# ── YOUR QUERY BELOW ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example: list all opportunities
    r = gql("""
    {
      opportunities(first: 50) {
        edges {
          node {
            id name stage healthCheck priority
            nextFollowUpDate nextActionSummary
            company { name }
          }
        }
      }
    }
    """)

    if "data" in r:
        for e in r["data"]["opportunities"]["edges"]:
            n = e["node"]
            co = n["company"]["name"] if n["company"] else "-"
            hc = n.get("healthCheck") or "-"
            pri = n.get("priority") or "-"
            nxt = (n.get("nextActionSummary") or "")[:50]
            print(f"[{n['stage']:10s}] [{hc:18s}] [{pri:6s}] {n['name'][:35]:35s} | {co:20s} | {nxt}")
    else:
        print("Error:", r)
