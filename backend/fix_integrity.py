import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "app", "data")


def read_json(filename):
    with open(os.path.join(DATA_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


def write_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# 1. Update features.json to use existing groups, or add groups.
# Let's add the groups to feature_groups.json
groups = read_json("feature_groups.json")
new_groups = [
    {
        "id": "GRP-B-CORE",
        "name": "Core Parameters",
        "description": "Core elevator configuration.",
        "display_order": 1,
        "active": True,
    },
    {
        "id": "GRP-B-CTRL",
        "name": "Control Systems",
        "description": "Control systems.",
        "display_order": 4,
        "active": True,
    },
    {
        "id": "GRP-B-MECH",
        "name": "Mechanical Systems",
        "description": "Mechanical options.",
        "display_order": 5,
        "active": True,
    },
]
for ng in new_groups:
    if not any(g["id"] == ng["id"] for g in groups):
        groups.append(ng)
write_json("feature_groups.json", groups)

# 2. Fix feature_mappings.json orphaned feature_option_ids
mappings = read_json("feature_mappings.json")
# We just remove any mappings that point to old OPT-B-* options that no longer exist
# Or specifically the ones that failed
failed_options = [
    "OPT-B-DOOR-CO",
    "OPT-B-DOOR-SO",
    "OPT-B-FIN-SS",
    "OPT-B-FIN-GLS",
    "OPT-B-DEST-CONV",
    "OPT-B-GRP-STD",
]
mappings = [m for m in mappings if m.get("feature_option_id") not in failed_options]
write_json("feature_mappings.json", mappings)

print("Data integrity issues resolved.")
