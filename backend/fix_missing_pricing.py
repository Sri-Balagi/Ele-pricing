import json
import uuid


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


comps = load_json("app/data/components.json")
pricing = load_json("app/data/pricing.json")

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

existing_comp_prices = {
    p["entity_id"]
    for p in pricing["pricing_records"]
    if p["entity_type"] == "COMPONENT"
}

for c in comps:
    cid = c["id"]
    if cid not in existing_comp_prices:
        amount = comp_prices.get(cid, 500.0)
        pricing["pricing_records"].append(
            {
                "record_id": f"PRC-{uuid.uuid4().hex[:8].upper()}",
                "entity_type": "COMPONENT",
                "entity_id": cid,
                "currency": "EUR",
                "amount": float(amount),
                "effective_date": "2024-01-01T00:00:00Z",
                "active": True,
            }
        )

save_json("app/data/pricing.json", pricing)
