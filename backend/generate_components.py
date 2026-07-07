import json

components = []

# Structural
components.extend([
    {"id": "COMP-FRAME-01", "name": "Standard Car Frame", "description": "Standard steel car frame.", "category": "Structural", "unit": "pcs"},
    {"id": "COMP-FRAME-02", "name": "Heavy Duty Car Frame", "description": "Reinforced steel car frame for high capacity.", "category": "Structural", "unit": "pcs"},
    {"id": "COMP-CWT-01", "name": "Counterweight Frame", "description": "Standard counterweight frame.", "category": "Structural", "unit": "pcs"},
    {"id": "COMP-CWT-02", "name": "Filler Weights", "description": "Cast iron filler weights.", "category": "Structural", "unit": "kg"},
    {"id": "COMP-RAIL-01", "name": "Guide Rail T89", "description": "Standard guide rail.", "category": "Structural", "unit": "mm"},
    {"id": "COMP-RAIL-02", "name": "Guide Rail T127", "description": "Heavy duty guide rail.", "category": "Structural", "unit": "mm"},
    {"id": "COMP-BRACKET-01", "name": "Standard Rail Bracket", "description": "Wall mounting bracket.", "category": "Structural", "unit": "pcs"},
])

# Mechanical
components.extend([
    {"id": "COMP-MOT-10", "name": "Traction Motor 10kW", "description": "Gearless traction machine.", "category": "Mechanical", "unit": "kW"},
    {"id": "COMP-MOT-15", "name": "Traction Motor 15kW", "description": "High power gearless machine.", "category": "Mechanical", "unit": "kW"},
    {"id": "COMP-MOT-22", "name": "Traction Motor 22kW", "description": "Very high power gearless machine.", "category": "Mechanical", "unit": "kW"},
    {"id": "COMP-ROPE-08", "name": "Suspension Rope 8mm", "description": "Steel wire rope.", "category": "Mechanical", "unit": "mm"},
    {"id": "COMP-ROPE-10", "name": "Suspension Rope 10mm", "description": "Heavy steel wire rope.", "category": "Mechanical", "unit": "mm"},
    {"id": "COMP-PULLEY-01", "name": "Deflector Sheave 320mm", "description": "Standard sheave.", "category": "Mechanical", "unit": "pcs"},
    {"id": "COMP-PULLEY-02", "name": "Deflector Sheave 400mm", "description": "Large sheave.", "category": "Mechanical", "unit": "pcs"},
    {"id": "COMP-OVS-01", "name": "Overspeed Governor 1.0", "description": "Governor for 1.0m/s.", "category": "Mechanical", "unit": "pcs"},
    {"id": "COMP-OVS-02", "name": "Overspeed Governor 1.6", "description": "Governor for 1.6m/s.", "category": "Mechanical", "unit": "pcs"},
    {"id": "COMP-OVS-03", "name": "Overspeed Governor 2.5", "description": "Governor for 2.5m/s.", "category": "Mechanical", "unit": "pcs"},
])

# Electrical
components.extend([
    {"id": "COMP-CBL-01", "name": "Traveling Cable", "description": "Flat traveling cable.", "category": "Electrical", "unit": "mm"},
    {"id": "COMP-ENC-01", "name": "Rotary Encoder", "description": "Motor feedback encoder.", "category": "Electrical", "unit": "pcs"},
    {"id": "COMP-SW-01", "name": "Limit Switch", "description": "Shaft limit switch.", "category": "Electrical", "unit": "pcs"},
    {"id": "COMP-LIGHT-01", "name": "LED Cabin Light", "description": "Standard lighting.", "category": "Electrical", "unit": "pcs"},
    {"id": "COMP-FAN-01", "name": "Cabin Fan", "description": "Ventilation fan.", "category": "Electrical", "unit": "pcs"},
    {"id": "COMP-BAT-01", "name": "Emergency Battery", "description": "UPS for emergency rescue.", "category": "Electrical", "unit": "pcs"},
])

# Control
components.extend([
    {"id": "COMP-CTRL-01", "name": "Simplex Controller", "description": "Main control board for 1 elevator.", "category": "Control", "unit": "pcs"},
    {"id": "COMP-CTRL-02", "name": "Duplex Controller", "description": "Main control board for 2 elevators.", "category": "Control", "unit": "pcs"},
    {"id": "COMP-DRV-10", "name": "Inverter Drive 10kW", "description": "V3F drive unit.", "category": "Control", "unit": "pcs"},
    {"id": "COMP-DRV-15", "name": "Inverter Drive 15kW", "description": "V3F drive unit.", "category": "Control", "unit": "pcs"},
    {"id": "COMP-DRV-22", "name": "Inverter Drive 22kW", "description": "V3F drive unit.", "category": "Control", "unit": "pcs"},
    {"id": "COMP-COP-01", "name": "Standard COP", "description": "Car Operating Panel.", "category": "Control", "unit": "pcs"},
    {"id": "COMP-LOP-01", "name": "Standard LOP", "description": "Landing Operating Panel.", "category": "Control", "unit": "pcs"},
])

# Safety
components.extend([
    {"id": "COMP-SAF-01", "name": "Safety Gear 630kg", "description": "Progressive safety gear.", "category": "Safety", "unit": "pcs"},
    {"id": "COMP-SAF-02", "name": "Safety Gear 1000kg", "description": "Progressive safety gear.", "category": "Safety", "unit": "pcs"},
    {"id": "COMP-SAF-03", "name": "Safety Gear 1600kg", "description": "Progressive safety gear.", "category": "Safety", "unit": "pcs"},
    {"id": "COMP-BUF-01", "name": "Polyurethane Buffer", "description": "Buffer for low speed.", "category": "Safety", "unit": "pcs"},
    {"id": "COMP-BUF-02", "name": "Oil Buffer", "description": "Hydraulic buffer for high speed.", "category": "Safety", "unit": "pcs"},
    {"id": "COMP-BRAKE-01", "name": "Machine Brake", "description": "Electromechanical brake.", "category": "Safety", "unit": "pcs"},
    {"id": "COMP-LC-01", "name": "Load Weighing Sensor", "description": "Measures cabin load.", "category": "Safety", "unit": "pcs"},
])

# Cabin
components.extend([
    {"id": "COMP-CAB-01", "name": "Cabin Shell", "description": "Bare steel cabin shell.", "category": "Cabin", "unit": "pcs"},
    {"id": "COMP-PNL-SS", "name": "SS Wall Panel", "description": "Stainless steel panel.", "category": "Cabin", "unit": "pcs"},
    {"id": "COMP-PNL-GL", "name": "Glass Wall Panel", "description": "Panoramic glass panel.", "category": "Cabin", "unit": "pcs"},
    {"id": "COMP-FLR-01", "name": "PVC Floor", "description": "Standard PVC flooring.", "category": "Cabin", "unit": "pcs"},
    {"id": "COMP-FLR-02", "name": "Stone Floor", "description": "Artificial stone flooring.", "category": "Cabin", "unit": "pcs"},
    {"id": "COMP-HAND-01", "name": "Handrail", "description": "Stainless steel handrail.", "category": "Cabin", "unit": "pcs"},
    {"id": "COMP-MIR-01", "name": "Half Mirror", "description": "Rear wall mirror.", "category": "Cabin", "unit": "pcs"},
])

# Door
components.extend([
    {"id": "COMP-DOP-CO", "name": "Door Operator CO", "description": "Center opening operator.", "category": "Door", "unit": "pcs"},
    {"id": "COMP-DOP-SO", "name": "Door Operator SO", "description": "Side opening operator.", "category": "Door", "unit": "pcs"},
    {"id": "COMP-DPL-CO", "name": "Car Door Panels CO", "description": "Set of center opening car doors.", "category": "Door", "unit": "pcs"},
    {"id": "COMP-DPL-SO", "name": "Car Door Panels SO", "description": "Set of side opening car doors.", "category": "Door", "unit": "pcs"},
    {"id": "COMP-LDR-CO", "name": "Landing Door CO", "description": "Center opening landing door.", "category": "Door", "unit": "pcs"},
    {"id": "COMP-LDR-SO", "name": "Landing Door SO", "description": "Side opening landing door.", "category": "Door", "unit": "pcs"},
    {"id": "COMP-LCURT-01", "name": "Light Curtain", "description": "Infrared door safety edge.", "category": "Door", "unit": "pcs"},
])

# Fill out metadata for components
for c in components:
    c["active"] = True
    c["metadata"] = {}
    c["specifications"] = {}
    c["manufacturer"] = "Generic"

with open("app/data/components.json", "w") as f:
    json.dump(components, f, indent=2)

print(f"Generated {len(components)} components.")
