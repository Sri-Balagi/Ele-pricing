import json
import random


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


comps = load_json("app/data/components.json")
opts = load_json("app/data/feature_options.json")
pricing = load_json("app/data/pricing.json")

# Add missing components for Type A, B, C
missing_components = [
    {
        "id": "COMP-PNL-PC",
        "name": "Painted Steel Wall Panel",
        "category": "Cabin",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-MOT-37",
        "name": "Traction Motor 37kW",
        "category": "Mechanical",
        "unit": "kW",
        "active": True,
    },
    {
        "id": "COMP-DRV-37",
        "name": "Inverter Drive 37kW",
        "category": "Electrical",
        "unit": "kW",
        "active": True,
    },
    {
        "id": "COMP-CERT-EN",
        "name": "EN 81-20/50 Certification",
        "category": "Documentation",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-CERT-ATEX",
        "name": "ATEX Explosion Proof Cert",
        "category": "Documentation",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-CERT-DNV",
        "name": "DNV Marine Certification",
        "category": "Documentation",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-COR-C3",
        "name": "C3 Corrosion Protection",
        "category": "Treatment",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-COR-C4",
        "name": "C4 Corrosion Protection",
        "category": "Treatment",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-COR-C5",
        "name": "C5 Marine Corrosion Protection",
        "category": "Treatment",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-BRACKET-02",
        "name": "Heavy Duty Rail Bracket",
        "category": "Structural",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-FRAME-INC",
        "name": "Inclined Car Frame",
        "category": "Structural",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-VIB-STD",
        "name": "Standard Isolation Pads",
        "category": "Mechanical",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-VIB-ANTI",
        "name": "Anti-Vibration Mounts",
        "category": "Mechanical",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-VIB-SEIS",
        "name": "Seismic Isolation System",
        "category": "Mechanical",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-DOOR-STD",
        "name": "Standard Doors",
        "category": "Doors",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-DOOR-FIR1",
        "name": "EI60 Fire Doors",
        "category": "Doors",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-DOOR-FIR2",
        "name": "EI120 Fire Doors",
        "category": "Doors",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-FRAME-03",
        "name": "Ultra Heavy Duty Frame",
        "category": "Structural",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-PNL-ROB",
        "name": "Robust Vandal-Proof Panels",
        "category": "Cabin",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-PNL-BLST",
        "name": "Blast Resistant Panels",
        "category": "Cabin",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-MON-NONE",
        "name": "Local Alarm System",
        "category": "Electrical",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-MON-GSM",
        "name": "GSM Remote Monitoring",
        "category": "Electrical",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-MON-SCADA",
        "name": "SCADA Integration Module",
        "category": "Electrical",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-CTRL-TRIP",
        "name": "Triplex Controller",
        "category": "Electrical",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-DEST-AI",
        "name": "AI Destination Dispatch CPU",
        "category": "Electrical",
        "unit": "pcs",
        "active": True,
    },
    {
        "id": "COMP-NRG-REGEN",
        "name": "Regenerative Drive Unit",
        "category": "Electrical",
        "unit": "pcs",
        "active": True,
    },
]

comp_ids = {c["id"] for c in comps}
for m in missing_components:
    if m["id"] not in comp_ids:
        m.update(
            {
                "description": "",
                "metadata": {},
                "specifications": {},
                "manufacturer": "Generic",
            }
        )
        comps.append(m)

save_json("app/data/components.json", comps)

comp_prices = {
    "COMP-FRAME-01": 1200,
    "COMP-FRAME-02": 2000,
    "COMP-FRAME-03": 3500,
    "COMP-FRAME-INC": 4000,
    "COMP-CWT-01": 800,
    "COMP-CWT-02": 500,
    "COMP-RAIL-01": 300,
    "COMP-RAIL-02": 500,
    "COMP-BRACKET-01": 50,
    "COMP-BRACKET-02": 120,
    "COMP-MOT-10": 3500,
    "COMP-MOT-15": 4500,
    "COMP-MOT-22": 6000,
    "COMP-MOT-37": 9500,
    "COMP-ROPE-08": 400,
    "COMP-ROPE-10": 600,
    "COMP-PULLEY-01": 350,
    "COMP-PULLEY-02": 500,
    "COMP-OVS-01": 400,
    "COMP-OVS-02": 500,
    "COMP-OVS-03": 800,
    "COMP-CBL-01": 300,
    "COMP-ENC-01": 250,
    "COMP-SW-01": 100,
    "COMP-LIGHT-01": 150,
    "COMP-FAN-01": 100,
    "COMP-BAT-01": 200,
    "COMP-CTRL-01": 5000,
    "COMP-CTRL-02": 6500,
    "COMP-CTRL-TRIP": 9000,
    "COMP-DRV-10": 1500,
    "COMP-DRV-15": 2000,
    "COMP-DRV-22": 3000,
    "COMP-DRV-37": 4500,
    "COMP-COP-01": 800,
    "COMP-LOP-01": 150,
    "COMP-SAF-01": 400,
    "COMP-SAF-02": 600,
    "COMP-SAF-03": 900,
    "COMP-BUF-01": 150,
    "COMP-BUF-02": 450,
    "COMP-BRAKE-01": 600,
    "COMP-LC-01": 350,
    "COMP-CAB-01": 2500,
    "COMP-PNL-SS": 1800,
    "COMP-PNL-GL": 3500,
    "COMP-PNL-PC": 1200,
    "COMP-PNL-ROB": 2800,
    "COMP-PNL-BLST": 5000,
    "COMP-FLR-01": 200,
    "COMP-FLR-02": 900,
    "COMP-HAND-01": 150,
    "COMP-MIR-01": 250,
    "COMP-DOP-CO": 1200,
    "COMP-DOP-SO": 1100,
    "COMP-DPL-CO": 600,
    "COMP-DPL-SO": 500,
    "COMP-LDR-CO": 800,
    "COMP-LDR-SO": 750,
    "COMP-LCURT-01": 300,
    "COMP-CERT-EN": 500,
    "COMP-CERT-ATEX": 3000,
    "COMP-CERT-DNV": 2500,
    "COMP-COR-C3": 400,
    "COMP-COR-C4": 800,
    "COMP-COR-C5": 1500,
    "COMP-VIB-STD": 100,
    "COMP-VIB-ANTI": 350,
    "COMP-VIB-SEIS": 1200,
    "COMP-DOOR-STD": 600,
    "COMP-DOOR-FIR1": 1400,
    "COMP-DOOR-FIR2": 2200,
    "COMP-MON-NONE": 100,
    "COMP-MON-GSM": 600,
    "COMP-MON-SCADA": 1500,
    "COMP-DEST-AI": 3500,
    "COMP-NRG-REGEN": 4000,
}

# Update prices in pricing.json
for p in pricing["pricing_records"]:
    if p["entity_type"] == "COMPONENT":
        cid = p["entity_id"]
        p["amount"] = float(comp_prices.get(cid, random.randint(150, 800)))

save_json("app/data/pricing.json", pricing)

# Mapping dictionary: option_id -> list of component_ids
mapping_rules = {
    # Type A
    "OPT-A-CAP-450": ["COMP-FRAME-01", "COMP-MOT-10", "COMP-SAF-01"],
    "OPT-A-CAP-630": ["COMP-FRAME-01", "COMP-MOT-10", "COMP-SAF-01"],
    "OPT-A-SPD-63": ["COMP-OVS-01", "COMP-BUF-01"],
    "OPT-A-SPD-100": ["COMP-OVS-01", "COMP-BUF-01"],
    "OPT-A-DOOR-CO": ["COMP-DOP-CO", "COMP-DPL-CO", "COMP-LDR-CO"],
    "OPT-A-DOOR-SO": ["COMP-DOP-SO", "COMP-DPL-SO", "COMP-LDR-SO"],
    "OPT-A-FIN-SS": ["COMP-CAB-01", "COMP-PNL-SS"],
    "OPT-A-FIN-PC": ["COMP-CAB-01", "COMP-PNL-PC"],
    # Type B
    "OPT-B-CAP-630": ["COMP-FRAME-01", "COMP-MOT-10", "COMP-DRV-10", "COMP-SAF-01"],
    "OPT-B-CAP-1000": ["COMP-FRAME-02", "COMP-MOT-15", "COMP-DRV-15", "COMP-SAF-02"],
    "OPT-B-CAP-1275": ["COMP-FRAME-02", "COMP-MOT-22", "COMP-DRV-22", "COMP-SAF-03"],
    "OPT-B-SPEED-10": ["COMP-OVS-01", "COMP-BUF-01"],
    "OPT-B-SPEED-16": ["COMP-OVS-02", "COMP-BUF-01"],
    "OPT-B-SPEED-25": ["COMP-OVS-03", "COMP-BUF-02"],
    "OPT-B-DOOR-CENTER": ["COMP-DOP-CO", "COMP-DPL-CO", "COMP-LDR-CO"],
    "OPT-B-DOOR-SIDE": ["COMP-DOP-SO", "COMP-DPL-SO", "COMP-LDR-SO"],
    "OPT-B-DOOR-REAR": ["COMP-DOP-CO", "COMP-DPL-CO", "COMP-LDR-CO", "COMP-DOP-CO"],
    "OPT-B-WALL-SS": ["COMP-CAB-01", "COMP-PNL-SS"],
    "OPT-B-WALL-PC": ["COMP-CAB-01", "COMP-PNL-PC"],
    "OPT-B-WALL-GLASS": ["COMP-CAB-01", "COMP-PNL-GL"],
    "OPT-B-WALL-MIRROR": ["COMP-CAB-01", "COMP-PNL-SS", "COMP-MIR-01"],
    "OPT-B-FLOOR-PVC": ["COMP-FLR-01"],
    "OPT-B-FLOOR-MARBLE": ["COMP-FLR-02"],
    "OPT-B-CEIL-STD": ["COMP-LIGHT-01", "COMP-FAN-01"],
    "OPT-B-CEIL-HALO": ["COMP-LIGHT-01", "COMP-FAN-01"],
    "OPT-B-CEIL-STAR": ["COMP-LIGHT-01", "COMP-FAN-01"],
    "OPT-B-RAIL-FULL": ["COMP-RAIL-01"],
    "OPT-B-RAIL-NONE": [],
    "OPT-B-RAIL-REAR": ["COMP-RAIL-02"],
    "OPT-B-COP-PUSH": ["COMP-COP-01", "COMP-LOP-01"],
    "OPT-B-COP-TOUCH": ["COMP-COP-01", "COMP-LOP-01"],
    "OPT-B-DEST-NONE": [],
    "OPT-B-DEST-STD": ["COMP-CTRL-01"],
    "OPT-B-DEST-AI": ["COMP-DEST-AI"],
    "OPT-B-DRIVE-GEARED": ["COMP-DRV-15"],
    "OPT-B-DRIVE-GEARLESS": ["COMP-DRV-10"],
    "OPT-B-SUSP-ROPE": ["COMP-ROPE-10"],
    "OPT-B-SUSP-BELT": ["COMP-ROPE-08"],
    "OPT-B-CWT-SIDE": ["COMP-CWT-01", "COMP-CWT-02"],
    "OPT-B-CWT-REAR": ["COMP-CWT-01", "COMP-CWT-02"],
    "OPT-B-SHAFT-CONCRETE": ["COMP-BRACKET-01"],
    "OPT-B-SHAFT-STEEL": ["COMP-BRACKET-02"],
    "OPT-B-SHAFT-GLASS": ["COMP-BRACKET-02"],
    "OPT-B-NRG-OFF": [],
    "OPT-B-NRG-ECO": ["COMP-CTRL-01"],
    "OPT-B-NRG-REGEN": ["COMP-NRG-REGEN"],
    "OPT-B-GRP-SIMP": ["COMP-CTRL-01"],
    "OPT-B-GRP-DUP": ["COMP-CTRL-02"],
    "OPT-B-GRP-TRIP": ["COMP-CTRL-TRIP"],
    "OPT-B-PIT-STD": ["COMP-BUF-01"],
    "OPT-B-PIT-RED": ["COMP-BUF-01"],
    # Type C
    "OPT-C-CERT-EN": ["COMP-CERT-EN"],
    "OPT-C-CERT-ATEX": ["COMP-CERT-ATEX"],
    "OPT-C-CERT-DNV": ["COMP-CERT-DNV"],
    "OPT-C-DRV-75": ["COMP-MOT-10", "COMP-DRV-10"],
    "OPT-C-DRV-15": ["COMP-MOT-15", "COMP-DRV-15"],
    "OPT-C-DRV-22": ["COMP-MOT-22", "COMP-DRV-22"],
    "OPT-C-DRV-37": ["COMP-MOT-37", "COMP-DRV-37"],
    "OPT-C-COR-C3": ["COMP-COR-C3"],
    "OPT-C-COR-C4": ["COMP-COR-C4"],
    "OPT-C-COR-C5": ["COMP-COR-C5"],
    "OPT-C-SHF-CON": ["COMP-BRACKET-01"],
    "OPT-C-SHF-STL": ["COMP-BRACKET-02"],
    "OPT-C-SHF-RET": ["COMP-BRACKET-02"],
    "OPT-C-INC-0": ["COMP-FRAME-01"],
    "OPT-C-INC-15": ["COMP-FRAME-INC"],
    "OPT-C-INC-30": ["COMP-FRAME-INC"],
    "OPT-C-VIB-STD": ["COMP-VIB-STD"],
    "OPT-C-VIB-ANTI": ["COMP-VIB-ANTI"],
    "OPT-C-VIB-SEIS": ["COMP-VIB-SEIS"],
    "OPT-C-FIR-NONE": ["COMP-DOOR-STD"],
    "OPT-C-FIR-P1": ["COMP-DOOR-FIR1"],
    "OPT-C-FIR-P2": ["COMP-DOOR-FIR2"],
    "OPT-C-LOD-STD": ["COMP-FRAME-01"],
    "OPT-C-LOD-HVY": ["COMP-FRAME-02"],
    "OPT-C-LOD-ULT": ["COMP-FRAME-03"],
    "OPT-C-DRP-STD": ["COMP-PNL-SS"],
    "OPT-C-DRP-ROB": ["COMP-PNL-ROB"],
    "OPT-C-DRP-BLST": ["COMP-PNL-BLST"],
    "OPT-C-MON-NONE": ["COMP-MON-NONE"],
    "OPT-C-MON-GSM": ["COMP-MON-GSM"],
    "OPT-C-MON-SCADA": ["COMP-MON-SCADA"],
}

new_mappings = []
idx = 1
for opt_id, comp_ids in mapping_rules.items():
    for cid in comp_ids:
        new_mappings.append(
            {
                "id": f"MAP-AUTO-{idx}",
                "feature_option_id": opt_id,
                "component_id": cid,
                "quantity": 1,
                "action": "ADD",
                "active": True,
            }
        )
        idx += 1

save_json("app/data/feature_mappings.json", new_mappings)
print(f"Generated {len(new_mappings)} mappings for {len(mapping_rules)} options.")
