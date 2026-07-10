import json

p = json.load(open('app/data/pricing.json', encoding='utf-8'))

for record in p['pricing_records']:
    # If it's a new record we added that lacks 'price'
    if 'price' not in record:
        amt = record.get('amount', 500.0)
        record['price'] = amt
        record['base_cost'] = amt / 1.1
        record['markup_percentage'] = 10.0

    # If it's an existing record we appended 'amount' to
    if 'amount' in record:
        # overwrite the price with our generated realistic amount
        amt = record.pop('amount')
        record['price'] = amt
        record['base_cost'] = amt / 1.1

    # Remove invalid keys we accidentally added
    for k in ['record_id', 'currency', 'effective_date', 'active']:
        record.pop(k, None)

json.dump(p, open('app/data/pricing.json', 'w', encoding='utf-8'), indent=2)
