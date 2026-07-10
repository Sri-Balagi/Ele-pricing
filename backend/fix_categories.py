import json

c = json.load(open('app/data/components.json', encoding='utf-8'))
for x in c:
    if x['category'] == 'Documentation': x['category'] = 'Control'
    if x['category'] == 'Treatment': x['category'] = 'Structural'
    if x['category'] == 'Doors': x['category'] = 'Door'

json.dump(c, open('app/data/components.json', 'w', encoding='utf-8'), indent=2)
