import csv
import os

tran_data = list()
for fn in os.listdir('data'):
    if fn.endswith('.csv'):
        with open('data/' + fn) as f:
            data = list(csv.reader(f))
            if data[0][1:3] == ['Transaction_Type', 'Charge_Code']:
                tran_data = data
                break

if not tran_data:
    print('Missing files.')
else:
    output = dict()
    for row in tran_data[1:]:
        if len(row) < 12:
            continue
        tran_type = row[1]
        account_id = row[5]
        if tran_type not in ('RoomCharge', 'Taxes'):
            continue
        if len(account_id) != 13:
            continue
        tran_code = row[2]
        amount = round(float(row[11]), 2)
        if account_id not in output:
            output[account_id] = {
                    'RoomCharge': 0.0,
                    'Taxes': 0.0,
                    '1000': 0.0,
                    '1001': 0.0,
                }
        output[account_id][tran_type] += amount
        if tran_type == 'Taxes':
            if tran_code not in output[account_id]:
                output[account_id][tran_code] = 0.0
            output[account_id][tran_code] += amount

    final = [['CRS #', 'Room', '1000', '1001']]
    for crs_id, data in output.items():
        final.append([
                crs_id,
                round(data['RoomCharge'], 2),
                round(data['1000'], 2),
                round(data['1001'], 2),
            ])
    if os.path.exists('output.csv'):
        os.remove('output.csv')
    with open('output.csv', 'w') as f:
        writer = csv.writer(f)
        for row in final:
            writer.writerow(row)
    print('Complete!')
