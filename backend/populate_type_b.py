import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "app", "data")

def read_json(filename):
    with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# 1. Update features.json
features = read_json("features.json")
features = [f for f in features if f["category_id"] != "CAT-B"]

cat_b_features = [
    {"id": "FEAT-B-CAPACITY", "name": "Load Capacity", "description": "Maximum payload.", "category_id": "CAT-B", "group_id": "GRP-B-CORE", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-SPEED", "name": "Rated Speed", "description": "Travel speed.", "category_id": "CAT-B", "group_id": "GRP-B-CORE", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-DOOR-TYPE", "name": "Door Opening Type", "description": "Door mechanism.", "category_id": "CAT-B", "group_id": "GRP-B-DOOR", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-CABIN-FINISH", "name": "Cabin Wall Finish", "description": "Interior walls.", "category_id": "CAT-B", "group_id": "GRP-B-CABIN", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-STOPS", "name": "Number of Stops", "description": "Floor count.", "category_id": "CAT-B", "group_id": "GRP-B-CORE", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-DOOR-DIM", "name": "Door Dimensions", "description": "Door size.", "category_id": "CAT-B", "group_id": "GRP-B-DOOR", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-FLOORING", "name": "Cabin Flooring", "description": "Floor material.", "category_id": "CAT-B", "group_id": "GRP-B-CABIN", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-CEILING", "name": "Ceiling Design", "description": "Lighting design.", "category_id": "CAT-B", "group_id": "GRP-B-CABIN", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-HANDRAIL", "name": "Handrails", "description": "Support rails.", "category_id": "CAT-B", "group_id": "GRP-B-CABIN", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-COP", "name": "Operating Panel (COP)", "description": "User interface.", "category_id": "CAT-B", "group_id": "GRP-B-CTRL", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-DEST-CTRL", "name": "Destination Control System", "description": "Dispatch algorithm.", "category_id": "CAT-B", "group_id": "GRP-B-CTRL", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-DRIVE", "name": "Drive System", "description": "Motor technology.", "category_id": "CAT-B", "group_id": "GRP-B-MECH", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-SUSPENSION", "name": "Suspension Type", "description": "Lifting medium.", "category_id": "CAT-B", "group_id": "GRP-B-MECH", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-CWT-LOC", "name": "Counterweight Location", "description": "Weight placement.", "category_id": "CAT-B", "group_id": "GRP-B-MECH", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-SHAFT", "name": "Shaft Type", "description": "Enclosure structure.", "category_id": "CAT-B", "group_id": "GRP-B-MECH", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-ENERGY-MODE", "name": "Energy Savings Mode", "description": "Power efficiency.", "category_id": "CAT-B", "group_id": "GRP-B-CTRL", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-GROUP-CTRL", "name": "Group Control", "description": "Elevator grouping.", "category_id": "CAT-B", "group_id": "GRP-B-CTRL", "required": True, "configurable": True, "active": True, "metadata": {}},
    {"id": "FEAT-B-PIT-DEPTH", "name": "Pit Depth", "description": "Bottom clearance.", "category_id": "CAT-B", "group_id": "GRP-B-MECH", "required": True, "configurable": True, "active": True, "metadata": {}}
]

features.extend(cat_b_features)
write_json("features.json", features)

# 2. Update feature_options.json
options = read_json("feature_options.json")
options = [o for o in options if not o["feature_id"].startswith("FEAT-B-")]

cat_b_options = [
    # Capacity
    {"id": "OPT-B-CAP-630", "feature_id": "FEAT-B-CAPACITY", "display_name": "630 kg (8 persons)", "internal_value": 630, "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-CAP-1000", "feature_id": "FEAT-B-CAPACITY", "display_name": "1000 kg (13 persons)", "internal_value": 1000, "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-CAP-1275", "feature_id": "FEAT-B-CAPACITY", "display_name": "1275 kg (17 persons)", "internal_value": 1275, "description": "", "active": True, "metadata": {}},
    # Speed
    {"id": "OPT-B-SPEED-10", "feature_id": "FEAT-B-SPEED", "display_name": "1.0 m/s", "internal_value": 1.0, "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-SPEED-16", "feature_id": "FEAT-B-SPEED", "display_name": "1.6 m/s", "internal_value": 1.6, "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-SPEED-25", "feature_id": "FEAT-B-SPEED", "display_name": "2.5 m/s", "internal_value": 2.5, "description": "", "active": True, "metadata": {}},
    # Door Type
    {"id": "OPT-B-DOOR-SIDE", "feature_id": "FEAT-B-DOOR-TYPE", "display_name": "Side Opening", "internal_value": "SIDE", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-DOOR-CENTER", "feature_id": "FEAT-B-DOOR-TYPE", "display_name": "Center Opening", "internal_value": "CENTER", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-DOOR-REAR", "feature_id": "FEAT-B-DOOR-TYPE", "display_name": "Rear Opening", "internal_value": "REAR", "description": "", "active": True, "metadata": {}},
    # Cabin Finish
    {"id": "OPT-B-WALL-PC", "feature_id": "FEAT-B-CABIN-FINISH", "display_name": "Powder Coated", "internal_value": "PC", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-WALL-SS", "feature_id": "FEAT-B-CABIN-FINISH", "display_name": "Hairline SS", "internal_value": "SS", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-WALL-MIRROR", "feature_id": "FEAT-B-CABIN-FINISH", "display_name": "Mirror SS", "internal_value": "MIRROR", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-WALL-GLASS", "feature_id": "FEAT-B-CABIN-FINISH", "display_name": "Glass Panoramic", "internal_value": "GLASS", "description": "", "active": True, "metadata": {}},
    # Door Dim
    {"id": "OPT-B-DIM-800", "feature_id": "FEAT-B-DOOR-DIM", "display_name": "800x2000 mm", "internal_value": 800, "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-DIM-900", "feature_id": "FEAT-B-DOOR-DIM", "display_name": "900x2100 mm", "internal_value": 900, "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-DIM-1000", "feature_id": "FEAT-B-DOOR-DIM", "display_name": "1000x2100 mm", "internal_value": 1000, "description": "", "active": True, "metadata": {}},
    # Flooring
    {"id": "OPT-B-FLOOR-PVC", "feature_id": "FEAT-B-FLOORING", "display_name": "PVC", "internal_value": "PVC", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-FLOOR-STONE", "feature_id": "FEAT-B-FLOORING", "display_name": "Artificial Stone", "internal_value": "STONE", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-FLOOR-MARBLE", "feature_id": "FEAT-B-FLOORING", "display_name": "Natural Marble", "internal_value": "MARBLE", "description": "", "active": True, "metadata": {}},
    # Ceiling
    {"id": "OPT-B-CEIL-STD", "feature_id": "FEAT-B-CEILING", "display_name": "Standard LED", "internal_value": "STD", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-CEIL-HALO", "feature_id": "FEAT-B-CEILING", "display_name": "Halo LED", "internal_value": "HALO", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-CEIL-STAR", "feature_id": "FEAT-B-CEILING", "display_name": "Starry Night", "internal_value": "STAR", "description": "", "active": True, "metadata": {}},
    # Handrail
    {"id": "OPT-B-RAIL-NONE", "feature_id": "FEAT-B-HANDRAIL", "display_name": "None", "internal_value": "NONE", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-RAIL-REAR", "feature_id": "FEAT-B-HANDRAIL", "display_name": "Single Rear", "internal_value": "REAR", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-RAIL-FULL", "feature_id": "FEAT-B-HANDRAIL", "display_name": "Three Sides", "internal_value": "FULL", "description": "", "active": True, "metadata": {}},
    # COP
    {"id": "OPT-B-COP-PUSH", "feature_id": "FEAT-B-COP", "display_name": "Push Button", "internal_value": "PUSH", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-COP-TOUCH", "feature_id": "FEAT-B-COP", "display_name": "Touchscreen", "internal_value": "TOUCH", "description": "", "active": True, "metadata": {}},
    # Dest Ctrl
    {"id": "OPT-B-DEST-NONE", "feature_id": "FEAT-B-DEST-CTRL", "display_name": "None", "internal_value": "NONE", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-DEST-STD", "feature_id": "FEAT-B-DEST-CTRL", "display_name": "Standard DCS", "internal_value": "STD", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-DEST-AI", "feature_id": "FEAT-B-DEST-CTRL", "display_name": "Advanced AI DCS", "internal_value": "AI", "description": "", "active": True, "metadata": {}},
    # Drive
    {"id": "OPT-B-DRIVE-GEARED", "feature_id": "FEAT-B-DRIVE", "display_name": "Geared Traction", "internal_value": "GEARED", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-DRIVE-GEARLESS", "feature_id": "FEAT-B-DRIVE", "display_name": "Gearless Traction", "internal_value": "GEARLESS", "description": "", "active": True, "metadata": {}},
    # Suspension
    {"id": "OPT-B-SUSP-ROPE", "feature_id": "FEAT-B-SUSPENSION", "display_name": "Steel Rope", "internal_value": "ROPE", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-SUSP-BELT", "feature_id": "FEAT-B-SUSPENSION", "display_name": "Polyurethane Belt", "internal_value": "BELT", "description": "", "active": True, "metadata": {}},
    # CWT Loc
    {"id": "OPT-B-CWT-SIDE", "feature_id": "FEAT-B-CWT-LOC", "display_name": "Side", "internal_value": "SIDE", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-CWT-REAR", "feature_id": "FEAT-B-CWT-LOC", "display_name": "Rear", "internal_value": "REAR", "description": "", "active": True, "metadata": {}},
    # Shaft
    {"id": "OPT-B-SHAFT-CONCRETE", "feature_id": "FEAT-B-SHAFT", "display_name": "Concrete", "internal_value": "CONC", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-SHAFT-STEEL", "feature_id": "FEAT-B-SHAFT", "display_name": "Steel Frame", "internal_value": "STEEL", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-SHAFT-GLASS", "feature_id": "FEAT-B-SHAFT", "display_name": "Glass Panoramic", "internal_value": "GLASS", "description": "", "active": True, "metadata": {}},
    # Energy
    {"id": "OPT-B-NRG-OFF", "feature_id": "FEAT-B-ENERGY-MODE", "display_name": "Off", "internal_value": "OFF", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-NRG-ECO", "feature_id": "FEAT-B-ENERGY-MODE", "display_name": "EcoMode", "internal_value": "ECO", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-NRG-REGEN", "feature_id": "FEAT-B-ENERGY-MODE", "display_name": "Regen Drive", "internal_value": "REGEN", "description": "", "active": True, "metadata": {}},
    # Group Ctrl
    {"id": "OPT-B-GRP-SIMP", "feature_id": "FEAT-B-GROUP-CTRL", "display_name": "Simplex", "internal_value": "SIMP", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-GRP-DUP", "feature_id": "FEAT-B-GROUP-CTRL", "display_name": "Duplex", "internal_value": "DUP", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-GRP-TRIP", "feature_id": "FEAT-B-GROUP-CTRL", "display_name": "Triplex", "internal_value": "TRIP", "description": "", "active": True, "metadata": {}},
    # Pit Depth
    {"id": "OPT-B-PIT-STD", "feature_id": "FEAT-B-PIT-DEPTH", "display_name": "Standard", "internal_value": "STD", "description": "", "active": True, "metadata": {}},
    {"id": "OPT-B-PIT-RED", "feature_id": "FEAT-B-PIT-DEPTH", "display_name": "Reduced", "internal_value": "RED", "description": "", "active": True, "metadata": {}}
]

options.extend(cat_b_options)
write_json("feature_options.json", options)

# 3. Add to dependencies.json
deps = read_json("dependencies.json")
# Filter out old OPT-B rules just in case
deps = [d for d in deps if not d["source_id"].startswith("OPT-B-")]

new_deps = [
    {"id": "DEP-B-1", "source_id": "OPT-B-SHAFT-GLASS", "target_id": "OPT-B-CWT-REAR", "dependency_type": "EXCLUDES", "description": "Glass Panoramic Shaft EXCLUDES Rear Counterweight"},
    {"id": "DEP-B-2", "source_id": "OPT-B-SPEED-25", "target_id": "OPT-B-DRIVE-GEARED", "dependency_type": "EXCLUDES", "description": "Rated Speed 2.5 m/s EXCLUDES Geared Traction Drive"},
    {"id": "DEP-B-3", "source_id": "OPT-B-SPEED-25", "target_id": "OPT-B-PIT-RED", "dependency_type": "EXCLUDES", "description": "Rated Speed 2.5 m/s EXCLUDES Reduced Pit Depth"},
    {"id": "DEP-B-4", "source_id": "OPT-B-FLOOR-MARBLE", "target_id": "OPT-B-CAP-630", "dependency_type": "EXCLUDES", "description": "Natural Marble Flooring EXCLUDES Load Capacity 630kg"},
    {"id": "DEP-B-5", "source_id": "OPT-B-SUSP-BELT", "target_id": "OPT-B-SPEED-25", "dependency_type": "EXCLUDES", "description": "Polyurethane Belt Suspension EXCLUDES Rated Speed 2.5 m/s"},
    {"id": "DEP-B-6", "source_id": "OPT-B-DEST-AI", "target_id": "OPT-B-COP-PUSH", "dependency_type": "EXCLUDES", "description": "Advanced AI Destination Control EXCLUDES Push Button COP"},
    {"id": "DEP-B-7", "source_id": "OPT-B-GRP-TRIP", "target_id": "OPT-B-DEST-NONE", "dependency_type": "EXCLUDES", "description": "Triplex Group Control EXCLUDES Destination Control None"},
    {"id": "DEP-B-8", "source_id": "OPT-B-SHAFT-GLASS", "target_id": "OPT-B-WALL-SS", "dependency_type": "EXCLUDES", "description": "Glass Panoramic Shaft EXCLUDES Hairline SS Cabin Wall"},
    {"id": "DEP-B-9", "source_id": "OPT-B-NRG-REGEN", "target_id": "OPT-B-DRIVE-GEARED", "dependency_type": "EXCLUDES", "description": "Regen Drive Energy Mode EXCLUDES Geared Traction Drive"},
    {"id": "DEP-B-10", "source_id": "OPT-B-DIM-1000", "target_id": "OPT-B-CAP-630", "dependency_type": "EXCLUDES", "description": "Door Dimension 1000mm EXCLUDES Load Capacity 630kg"},
    # We should also ensure bidirectionality where it makes sense, but EXCLUDES is naturally checked symmetrically by our frontend logic.
]
deps.extend(new_deps)
write_json("dependencies.json", deps)


# 4. Update pricing.json
pricing = read_json("pricing.json")
p_records = pricing.get("pricing_records", [])
# Filter out old CAT-B prices
p_records = [p for p in p_records if not p["entity_id"].startswith("OPT-B-")]

# Assign basic prices to mimic previous patterns
new_prices = {
    "OPT-B-CAP-630": 0, "OPT-B-CAP-1000": 30, "OPT-B-CAP-1275": 70,
    "OPT-B-SPEED-10": 0, "OPT-B-SPEED-16": 30, "OPT-B-SPEED-25": 70,
    "OPT-B-DOOR-SIDE": 0, "OPT-B-DOOR-CENTER": 30, "OPT-B-DOOR-REAR": 70,
    "OPT-B-WALL-PC": 0, "OPT-B-WALL-SS": 50, "OPT-B-WALL-MIRROR": 100, "OPT-B-WALL-GLASS": 300,
    "OPT-B-DIM-800": 0, "OPT-B-DIM-900": 20, "OPT-B-DIM-1000": 50,
    "OPT-B-FLOOR-PVC": 0, "OPT-B-FLOOR-STONE": 80, "OPT-B-FLOOR-MARBLE": 150,
    "OPT-B-CEIL-STD": 0, "OPT-B-CEIL-HALO": 40, "OPT-B-CEIL-STAR": 120,
    "OPT-B-RAIL-NONE": 0, "OPT-B-RAIL-REAR": 10, "OPT-B-RAIL-FULL": 30,
    "OPT-B-COP-PUSH": 0, "OPT-B-COP-TOUCH": 200,
    "OPT-B-DEST-NONE": 0, "OPT-B-DEST-STD": 100, "OPT-B-DEST-AI": 300,
    "OPT-B-DRIVE-GEARED": 0, "OPT-B-DRIVE-GEARLESS": 250,
    "OPT-B-SUSP-ROPE": 0, "OPT-B-SUSP-BELT": 180,
    "OPT-B-CWT-SIDE": 0, "OPT-B-CWT-REAR": 50,
    "OPT-B-SHAFT-CONCRETE": 0, "OPT-B-SHAFT-STEEL": 500, "OPT-B-SHAFT-GLASS": 1500,
    "OPT-B-NRG-OFF": 0, "OPT-B-NRG-ECO": 100, "OPT-B-NRG-REGEN": 400,
    "OPT-B-GRP-SIMP": 0, "OPT-B-GRP-DUP": 50, "OPT-B-GRP-TRIP": 150,
    "OPT-B-PIT-STD": 0, "OPT-B-PIT-RED": 200,
}

for eid, val in new_prices.items():
    p_records.append({
        "entity_id": eid,
        "entity_type": "FEATURE_OPTION",
        "base_cost": val,
        "markup_percentage": 0.0,
        "price": val
    })

pricing["pricing_records"] = p_records
write_json("pricing.json", pricing)

# Note: components.json and feature_mappings.json would be updated similarly to map physical components, 
# but for the configuration Wizard, updating `feature_options` is sufficient to render and validate constraints! 
# We'll skip deep component mapping logic to keep this concise, since the UI logic acts on feature_options directly.

print("Type-B constraints and features successfully populated!")
