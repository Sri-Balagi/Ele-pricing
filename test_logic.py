import json
import os

with open(r'e:\Project\Ele-pricing\backend\app\data\dependencies.json', 'r', encoding='utf-8') as f:
    deps = json.load(f)

with open(r'e:\Project\Ele-pricing\backend\app\data\feature_options.json', 'r', encoding='utf-8') as f:
    opts = json.load(f)

with open(r'e:\Project\Ele-pricing\backend\app\data\features.json', 'r', encoding='utf-8') as f:
    feats = json.load(f)

optionId = "OPT-B-SPEED-25"
selectedIds = ["OPT-B-DRIVE-GEARED", "OPT-B-PIT-RED"]

conflicts = [d for d in deps if d.get('dependency_type') == 'EXCLUDES' and (
    (d['target_id'] == optionId and d['source_id'] in selectedIds) or 
    (d['source_id'] == optionId and d['target_id'] in selectedIds)
)]

messages = []
for c in conflicts:
    conflictingId = c['target_id'] if c['source_id'] == optionId else c['source_id']
    conflictOpt = next((o for o in opts if o['id'] == conflictingId), None)
    if conflictOpt:
        conflictFeat = next((f for f in feats if f['id'] == conflictOpt['feature_id']), None)
        if conflictFeat:
            messages.append(f"{conflictFeat['name']} ({conflictOpt['display_name']})")
        else:
            messages.append(conflictOpt['display_name'])
    else:
        messages.append("Unknown selection")

print(f"Incompatible with: {' and '.join(messages)}")
