import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "data")


def load_json(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


def save_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    categories = load_json("categories.json")
    if not any(c["id"] == "CAT-D" for c in categories):
        categories.append(
            {
                "id": "CAT-D",
                "name": "Type D Custom",
                "description": "Premium commercial elevator with 50 advanced configurable features.",
                "active": True,
                "metadata": {"max_stops": 20, "base_cost": 48000.0},
            }
        )
        save_json("categories.json", categories)

    groups = load_json("feature_groups.json")
    new_groups = [
        {
            "id": "GRP-D-PERFORMANCE",
            "name": "Performance",
            "description": "Core performance",
            "order": 1,
            "active": True,
        },
        {
            "id": "GRP-D-AESTHETICS",
            "name": "Aesthetics & Materials",
            "description": "Visual customization",
            "order": 2,
            "active": True,
        },
        {
            "id": "GRP-D-CABIN",
            "name": "Cabin Layout",
            "description": "Cabin configuration",
            "order": 3,
            "active": True,
        },
        {
            "id": "GRP-D-COMFORT",
            "name": "Comfort & Environment",
            "description": "Passenger comfort",
            "order": 4,
            "active": True,
        },
        {
            "id": "GRP-D-SECURITY",
            "name": "Security & Access",
            "description": "Access control",
            "order": 5,
            "active": True,
        },
        {
            "id": "GRP-D-SMART",
            "name": "Smart & Technology",
            "description": "Digital features",
            "order": 6,
            "active": True,
        },
    ]
    for ng in new_groups:
        if not any(g["id"] == ng["id"] for g in groups):
            groups.append(ng)
    save_json("feature_groups.json", groups)

    features = load_json("features.json")
    # Clone B features to D
    b_features = [f for f in features if f["category_id"] == "CAT-B"]
    for bf in b_features:
        new_id = bf["id"].replace("FEAT-B-", "FEAT-D-")
        if not any(f["id"] == new_id for f in features):
            new_f = dict(bf)
            new_f["id"] = new_id
            new_f["category_id"] = "CAT-D"
            # Map old group to new group
            if (
                "PERFORMANCE" in bf["group_id"]
                or "SPEED" in bf["group_id"]
                or "CAPACITY" in bf["group_id"]
            ):
                new_f["group_id"] = "GRP-D-PERFORMANCE"
            elif "CABIN" in bf["group_id"] or "FINISH" in bf["group_id"]:
                new_f["group_id"] = "GRP-D-AESTHETICS"
            else:
                new_f["group_id"] = "GRP-D-CABIN"
            features.append(new_f)

    # Add 32 new features
    new_feat_defs = [
        ("FEAT-D-MIRROR", "Mirror Configuration", "GRP-D-AESTHETICS"),
        ("FEAT-D-KICKPLATE", "Kickplate Material", "GRP-D-AESTHETICS"),
        ("FEAT-D-BUMPER", "Bumper Rails", "GRP-D-AESTHETICS"),
        ("FEAT-D-DOOR-FINISH", "Door Surface Finish", "GRP-D-AESTHETICS"),
        ("FEAT-D-ARCHITRAVE", "Architrave Style", "GRP-D-AESTHETICS"),
        ("FEAT-D-THRESHOLD", "Sill Material", "GRP-D-AESTHETICS"),
        ("FEAT-D-CAR-MAT", "Custom Car Mats", "GRP-D-AESTHETICS"),
        ("FEAT-D-EXT-DISPLAY", "Exterior Indicator", "GRP-D-SMART"),
        ("FEAT-D-VENTILATION", "Ventilation System", "GRP-D-COMFORT"),
        ("FEAT-D-AIR-PURIFIER", "Air Purifier", "GRP-D-COMFORT"),
        ("FEAT-D-MUSIC", "Background Music", "GRP-D-COMFORT"),
        ("FEAT-D-CHIME", "Arrival Chime", "GRP-D-COMFORT"),
        ("FEAT-D-VOICE", "Voice Annunciator", "GRP-D-COMFORT"),
        ("FEAT-D-SANITIZER", "Hand Sanitizer", "GRP-D-COMFORT"),
        ("FEAT-D-LIGHTING", "Cabin Lighting", "GRP-D-COMFORT"),
        ("FEAT-D-VIBRATION", "Anti-Vibration", "GRP-D-PERFORMANCE"),
        ("FEAT-D-RFID", "RFID Card Reader", "GRP-D-SECURITY"),
        ("FEAT-D-FINGERPRINT", "Biometric Scanner", "GRP-D-SECURITY"),
        ("FEAT-D-CAMERA", "CCTV Camera", "GRP-D-SECURITY"),
        ("FEAT-D-VIP-MODE", "VIP Priority Mode", "GRP-D-SECURITY"),
        ("FEAT-D-ALARM", "Emergency Alarm", "GRP-D-SECURITY"),
        ("FEAT-D-PHONE", "Intercom System", "GRP-D-SECURITY"),
        ("FEAT-D-ACCESS-CTRL", "Floor Lockout", "GRP-D-SECURITY"),
        ("FEAT-D-EVACUATION", "Evacuation Mode", "GRP-D-SECURITY"),
        ("FEAT-D-TOUCHLESS", "Touchless Buttons", "GRP-D-SMART"),
        ("FEAT-D-APP-CALL", "App Calling", "GRP-D-SMART"),
        ("FEAT-D-IOT", "IoT Maintenance", "GRP-D-SMART"),
        ("FEAT-D-DISPLAY-AD", "In-Cabin Ad Screen", "GRP-D-SMART"),
        ("FEAT-D-WIFI", "Wi-Fi Router", "GRP-D-SMART"),
        ("FEAT-D-REGEN-DRIVE", "Regenerative Drive", "GRP-D-PERFORMANCE"),
        ("FEAT-D-BUTTON-COLOR", "Button Color", "GRP-D-SMART"),
        ("FEAT-D-SEISMIC", "Seismic Sensor", "GRP-D-SECURITY"),
    ]
    for fid, fname, gid in new_feat_defs:
        if not any(f["id"] == fid for f in features):
            features.append(
                {
                    "id": fid,
                    "name": fname,
                    "description": f"Configuration for {fname}",
                    "category_id": "CAT-D",
                    "group_id": gid,
                    "required": True,
                    "configurable": True,
                    "active": True,
                    "metadata": {},
                }
            )
    save_json("features.json", features)

    options = load_json("feature_options.json")
    components = load_json("components.json")
    mappings = load_json("feature_mappings.json")
    pricing = load_json("pricing.json")

    # Clone B options to D
    b_options = [o for o in options if o["feature_id"].startswith("FEAT-B-")]
    for bo in b_options:
        new_id = bo["id"].replace("OPT-B-", "OPT-D-")
        new_fid = bo["feature_id"].replace("FEAT-B-", "FEAT-D-")
        if not any(o["id"] == new_id for o in options):
            new_o = dict(bo)
            new_o["id"] = new_id
            new_o["feature_id"] = new_fid
            options.append(new_o)

            # Clone mappings for this option
            b_maps = [m for m in mappings if m["feature_option_id"] == bo["id"]]
            for bm in b_maps:
                new_map = dict(bm)
                new_map["id"] = "MAP-" + new_id + "-" + bm["component_id"][-6:]
                new_map["feature_option_id"] = new_id
                if not any(m["id"] == new_map["id"] for m in mappings):
                    mappings.append(new_map)

    # Options for new 32 features
    new_opt_defs = {
        "FEAT-D-MIRROR": [
            ("OPT-D-MIRROR-NONE", "None", True, 0),
            ("OPT-D-MIRROR-HALF", "Half-Height", False, 300),
            ("OPT-D-MIRROR-FULL", "Full-Height", False, 600),
        ],
        "FEAT-D-KICKPLATE": [
            ("OPT-D-KICK-NONE", "None", True, 0),
            ("OPT-D-KICK-SS", "Stainless Steel", False, 200),
            ("OPT-D-KICK-BRASS", "Brass", False, 500),
        ],
        "FEAT-D-BUMPER": [
            ("OPT-D-BUMPER-NONE", "None", True, 0),
            ("OPT-D-BUMPER-WOOD", "Single Wood", False, 400),
            ("OPT-D-BUMPER-SS", "Double SS", False, 700),
        ],
        "FEAT-D-DOOR-FINISH": [
            ("OPT-D-DOOR-PAINT", "Painted", True, 0),
            ("OPT-D-DOOR-SS", "Hairline SS", False, 800),
            ("OPT-D-DOOR-GLASS", "Glass", False, 1500),
        ],
        "FEAT-D-ARCHITRAVE": [
            ("OPT-D-ARCH-NARROW", "Narrow", True, 0),
            ("OPT-D-ARCH-WIDE", "Wide", False, 400),
            ("OPT-D-ARCH-WRAP", "Full Wrap", False, 900),
        ],
        "FEAT-D-THRESHOLD": [
            ("OPT-D-THRESH-ALU", "Aluminum", True, 0),
            ("OPT-D-THRESH-BRONZE", "Bronze", False, 500),
        ],
        "FEAT-D-CAR-MAT": [
            ("OPT-D-MAT-NONE", "None", True, 0),
            ("OPT-D-MAT-RUBBER", "Rubber", False, 100),
            ("OPT-D-MAT-CARPET", "Premium Carpet", False, 300),
        ],
        "FEAT-D-EXT-DISPLAY": [
            ("OPT-D-EXT-DOT", "Dot-Matrix", True, 0),
            ("OPT-D-EXT-7SEG", "7-Segment", False, 100),
            ("OPT-D-EXT-TFT", "TFT LCD", False, 600),
        ],
        "FEAT-D-VENTILATION": [
            ("OPT-D-VENT-STD", "Standard Fan", True, 0),
            ("OPT-D-VENT-HIGH", "High-Capacity", False, 250),
            ("OPT-D-VENT-CROSS", "Cross-Flow", False, 500),
        ],
        "FEAT-D-AIR-PURIFIER": [
            ("OPT-D-PURIFY-NONE", "None", True, 0),
            ("OPT-D-PURIFY-HEPA", "HEPA Filter", False, 400),
            ("OPT-D-PURIFY-UVC", "UV-C + Ionizer", False, 900),
        ],
        "FEAT-D-MUSIC": [
            ("OPT-D-MUSIC-NONE", "None", True, 0),
            ("OPT-D-MUSIC-STD", "Standard Speakers", False, 300),
            ("OPT-D-MUSIC-PREM", "Premium Audio", False, 800),
        ],
        "FEAT-D-CHIME": [
            ("OPT-D-CHIME-STD", "Standard Ding", True, 0),
            ("OPT-D-CHIME-SOFT", "Soft Chime", False, 100),
            ("OPT-D-CHIME-MELODY", "Custom Melody", False, 300),
        ],
        "FEAT-D-VOICE": [
            ("OPT-D-VOICE-NONE", "None", True, 0),
            ("OPT-D-VOICE-SINGLE", "Single Language", False, 200),
            ("OPT-D-VOICE-MULTI", "Multi-Lingual", False, 500),
        ],
        "FEAT-D-SANITIZER": [
            ("OPT-D-SANI-NONE", "None", True, 0),
            ("OPT-D-SANI-MANUAL", "Manual", False, 100),
            ("OPT-D-SANI-AUTO", "Touchless Auto", False, 250),
        ],
        "FEAT-D-LIGHTING": [
            ("OPT-D-LIGHT-COOL", "Cool White", True, 0),
            ("OPT-D-LIGHT-WARM", "Warm White", False, 100),
            ("OPT-D-LIGHT-RGB", "RGB Ambient", False, 600),
        ],
        "FEAT-D-VIBRATION": [
            ("OPT-D-VIBE-STD", "Standard", True, 0),
            ("OPT-D-VIBE-PREM", "Premium Acoustic", False, 800),
        ],
        "FEAT-D-RFID": [
            ("OPT-D-RFID-NONE", "None", True, 0),
            ("OPT-D-RFID-WALL", "Wall-Mounted", False, 400),
            ("OPT-D-RFID-INT", "Integrated COP", False, 700),
        ],
        "FEAT-D-FINGERPRINT": [
            ("OPT-D-FINGER-NONE", "None", True, 0),
            ("OPT-D-FINGER-OPTIC", "Optic Scanner", False, 900),
        ],
        "FEAT-D-CAMERA": [
            ("OPT-D-CAM-NONE", "None", True, 0),
            ("OPT-D-CAM-DOME", "Dome Camera", False, 350),
            ("OPT-D-CAM-PIN", "Hidden Pinhole", False, 700),
        ],
        "FEAT-D-VIP-MODE": [
            ("OPT-D-VIP-NONE", "None", True, 0),
            ("OPT-D-VIP-KEY", "Key-Switch", False, 200),
            ("OPT-D-VIP-CARD", "Card-Activated", False, 400),
        ],
        "FEAT-D-ALARM": [
            ("OPT-D-ALARM-LOCAL", "Local Bell", True, 0),
            ("OPT-D-ALARM-CONN", "Connected Alarm", False, 500),
        ],
        "FEAT-D-PHONE": [
            ("OPT-D-PHONE-ANALOG", "Analog", True, 0),
            ("OPT-D-PHONE-IP", "IP/Digital", False, 400),
            ("OPT-D-PHONE-VIDEO", "Video Intercom", False, 900),
        ],
        "FEAT-D-ACCESS-CTRL": [
            ("OPT-D-ACC-NONE", "None", True, 0),
            ("OPT-D-ACC-TIME", "Time-Based", False, 600),
            ("OPT-D-ACC-FLOOR", "Floor-by-Floor", False, 1200),
        ],
        "FEAT-D-EVACUATION": [
            ("OPT-D-EVAC-STD", "Standard Recall", True, 0),
            ("OPT-D-EVAC-ADV", "Advanced Evacuation", False, 1500),
        ],
        "FEAT-D-TOUCHLESS": [
            ("OPT-D-TOUCH-NONE", "None", True, 0),
            ("OPT-D-TOUCH-HOVER", "Hover Sensor", False, 800),
        ],
        "FEAT-D-APP-CALL": [
            ("OPT-D-APP-NONE", "None", True, 0),
            ("OPT-D-APP-BT", "Bluetooth Enabled", False, 600),
        ],
        "FEAT-D-IOT": [
            ("OPT-D-IOT-BASIC", "Basic Telemetry", True, 0),
            ("OPT-D-IOT-ADV", "Advanced AI Monitoring", False, 1200),
        ],
        "FEAT-D-DISPLAY-AD": [
            ("OPT-D-DISP-NONE", "None", True, 0),
            ("OPT-D-DISP-15", "15-inch Screen", False, 700),
            ("OPT-D-DISP-21", "21-inch HD", False, 1300),
        ],
        "FEAT-D-WIFI": [
            ("OPT-D-WIFI-NONE", "None", True, 0),
            ("OPT-D-WIFI-4G", "4G Router", False, 400),
            ("OPT-D-WIFI-5G", "5G Router", False, 800),
        ],
        "FEAT-D-REGEN-DRIVE": [
            ("OPT-D-REGEN-NONE", "None", True, 0),
            ("OPT-D-REGEN-EN", "Enabled", False, 2000),
        ],
        "FEAT-D-BUTTON-COLOR": [
            ("OPT-D-BTN-WHITE", "White", True, 0),
            ("OPT-D-BTN-BLUE", "Blue", False, 100),
            ("OPT-D-BTN-STATUS", "Red/Green Status", False, 300),
        ],
        "FEAT-D-SEISMIC": [
            ("OPT-D-SEISMIC-NONE", "None", True, 0),
            ("OPT-D-SEISMIC-ACT", "Active Sensor", False, 1100),
        ],
    }

    comp_id_idx = 1000
    for fid, opt_list in new_opt_defs.items():
        for oid, oname, is_def, cost in opt_list:
            if not any(o["id"] == oid for o in options):
                options.append(
                    {
                        "id": oid,
                        "name": oname,
                        "description": oname,
                        "feature_id": fid,
                        "is_default": is_def,
                        "active": True,
                        "metadata": {},
                    }
                )

            if cost > 0:
                comp_id = f"COMP-FEAT-D-{comp_id_idx}"
                comp_id_idx += 1
                if not any(c["id"] == comp_id for c in components):
                    components.append(
                        {
                            "id": comp_id,
                            "name": oname + " Component",
                            "description": "Component for " + oname,
                            "category": "Cabin",
                            "unit": "pcs",
                            "active": True,
                            "metadata": {},
                            "specifications": {},
                            "manufacturer": "EleCorp",
                        }
                    )

                map_id = f"MAP-D-{comp_id_idx}"
                if not any(m["feature_option_id"] == oid for m in mappings):
                    mappings.append(
                        {
                            "id": map_id,
                            "feature_option_id": oid,
                            "component_id": comp_id,
                            "quantity": 1,
                            "action": "ADD",
                            "active": True,
                        }
                    )

                if not any(
                    p.get("entity_id") == comp_id for p in pricing["pricing_records"]
                ):
                    pricing["pricing_records"].append(
                        {
                            "entity_id": comp_id,
                            "entity_type": "COMPONENT",
                            "base_cost": cost,
                            "markup_percentage": 20.0,
                            "price": round(cost * 1.20, 2),
                        }
                    )

    save_json("feature_options.json", options)
    save_json("components.json", components)
    save_json("feature_mappings.json", mappings)
    save_json("pricing.json", pricing)

    # Add 37 Dependencies
    deps = load_json("dependencies.json")

    # 1-10 (Clone B to D)
    b_deps = [
        d
        for d in deps
        if isinstance(d.get("source_id"), str) and "OPT-B" in d["source_id"]
    ]
    for bd in b_deps:
        new_id = bd["id"].replace("-B-", "-D-")
        if not any(d["id"] == new_id for d in deps):
            new_d = dict(bd)
            new_d["id"] = new_id
            if "OPT-B" in new_d.get("source_id", ""):
                new_d["source_id"] = new_d["source_id"].replace("OPT-B", "OPT-D")
            if "OPT-B" in new_d.get("target_id", ""):
                new_d["target_id"] = new_d["target_id"].replace("OPT-B", "OPT-D")
            deps.append(new_d)

    new_deps_def = [
        (
            "OPT-D-REGEN-EN",
            "OPT-D-DRIVE-GEARLESS",
            "REQUIRES",
            "Regenerative Drive requires Gearless Motor",
        ),
        (
            "OPT-D-IOT-ADV",
            "OPT-D-DEST-AI",
            "REQUIRES",
            "Advanced IoT requires AI Destination",
        ),
        (
            "OPT-D-TOUCH-HOVER",
            "OPT-D-BTN-STATUS",
            "EXCLUDES",
            "Touchless buttons replace physical backlit buttons",
        ),
        (
            "OPT-D-TOUCH-HOVER",
            "OPT-D-FINGER-OPTIC",
            "EXCLUDES",
            "Touchless hygiene conflicts with fingerprint",
        ),
        (
            "OPT-D-DISP-21",
            "OPT-D-MIRROR-FULL",
            "EXCLUDES",
            "Large screen blocks full mirror",
        ),
        ("OPT-D-APP-BT", "OPT-D-WIFI-5G", "REQUIRES", "App calling requires 5G"),
        (
            "OPT-D-CAM-PIN",
            "OPT-D-CABIN-FINISH-SS",
            "REQUIRES",
            "Pinhole camera requires SS panel",
        ),
        (
            "OPT-D-PHONE-VIDEO",
            "OPT-D-WIFI-5G",
            "REQUIRES",
            "Video intercom requires 5G",
        ),
        (
            "OPT-D-PURIFY-UVC",
            "OPT-D-VENT-CROSS",
            "REQUIRES",
            "UVC purifier requires cross ventilation",
        ),
        (
            "OPT-D-VIP-CARD",
            "OPT-D-RFID-INT",
            "REQUIRES",
            "Card VIP requires integrated RFID",
        ),
        (
            "OPT-D-SANI-AUTO",
            "OPT-D-CABIN-FINISH-SS",
            "REQUIRES",
            "Sanitizer requires SS wall",
        ),
        (
            "OPT-D-BUMPER-WOOD",
            "OPT-D-CABIN-FINISH-SS",
            "EXCLUDES",
            "Wood bumper clashes with SS wall",
        ),
        (
            "OPT-D-DOOR-GLASS",
            "OPT-D-SHAFT-GLASS",
            "REQUIRES",
            "Glass doors require glass shaft",
        ),
        (
            "OPT-D-THRESH-BRONZE",
            "OPT-D-CABIN-FINISH-SS",
            "EXCLUDES",
            "Bronze threshold clashes with SS wall",
        ),
        (
            "OPT-D-LIGHT-RGB",
            "OPT-D-CEILING-CUSTOM",
            "REQUIRES",
            "RGB light requires custom ceiling",
        ),
        (
            "OPT-D-MUSIC-PREM",
            "OPT-D-VIBE-PREM",
            "REQUIRES",
            "Premium audio requires premium acoustic pads",
        ),
        (
            "OPT-D-EVAC-ADV",
            "OPT-D-PHONE-VIDEO",
            "REQUIRES",
            "Advanced evac requires video intercom",
        ),
        (
            "OPT-D-SEISMIC-ACT",
            "OPT-D-PIT-RED",
            "EXCLUDES",
            "Seismic sensor requires standard pit",
        ),
        (
            "OPT-D-ACC-FLOOR",
            "OPT-D-RFID-WALL",
            "REQUIRES",
            "Floor lockout requires wall RFID",
        ),
        (
            "OPT-D-SPEED-25",
            "OPT-D-VIBE-PREM",
            "REQUIRES",
            "High speed requires premium anti-vibration",
        ),
        (
            "OPT-D-CAP-1000",
            "OPT-D-VENT-CROSS",
            "REQUIRES",
            "High capacity requires cross ventilation",
        ),
        (
            "OPT-D-KICK-BRASS",
            "OPT-D-THRESH-BRONZE",
            "REQUIRES",
            "Brass kickplate requires bronze threshold",
        ),
        (
            "OPT-D-MAT-RUBBER",
            "OPT-D-FLOOR-MARBLE",
            "EXCLUDES",
            "Rubber mats excluded on premium marble",
        ),
        (
            "OPT-D-VOICE-MULTI",
            "OPT-D-DISP-21",
            "REQUIRES",
            "Multi-lingual voice requires 21-inch screen",
        ),
        (
            "OPT-D-DOOR-DIM-1200",
            "OPT-D-SHAFT-GLASS",
            "EXCLUDES",
            "Extra wide door excluded on glass shaft",
        ),
        (
            "OPT-D-ALARM-CONN",
            "OPT-D-IOT-BASIC",
            "REQUIRES",
            "Connected alarm requires basic IoT",
        ),
        (
            "OPT-D-ARCH-WRAP",
            "OPT-D-DOOR-SS",
            "REQUIRES",
            "Full wrap architrave requires SS door",
        ),
    ]

    idx = 100
    for src, tgt, dtype, desc in new_deps_def:
        did = f"DEP-D-{idx}"
        idx += 1
        if not any(d["id"] == did for d in deps):
            deps.append(
                {
                    "id": did,
                    "source_id": src,
                    "target_id": tgt,
                    "dependency_type": dtype,
                    "description": desc,
                    "priority": 100,
                    "condition_expression": None,
                }
            )
    save_json("dependencies.json", deps)

    print("Type D data generated successfully.")


if __name__ == "__main__":
    main()
