import csv
import os
import datetime as dt

strptime = dt.datetime.strptime

cc_data = list()
res_data = list()
for fn in os.listdir('data'):
    if fn.endswith('.csv'):
        with open('data/' + fn) as f:
            data = list(csv.reader(f))
            if data[0][1:4] == ['Payment_Code', 'Name', 'Mode_of_Entry']:
                cc_data = cc_data + data
            elif data[0][1:4] == ['Check-in', 'Check-out', 'Booked']:
                res_data = res_data + data

def process_evc(cc_data, res_data):

    output = dict()
    for row in res_data:
        if row[1] != 'Check-in':
            crs_id = row[-2]
            if crs_id not in output:
                if not row[-4].replace('.', '').isnumeric():
                    continue
                amount = float(row[-4])
                if amount < 0:
                    amount = 0.0
                output[crs_id] = {
                        'exp_id': row[-3],
                        'amount': amount,
                        'departure': strptime(row[2], '%Y-%m-%d').strftime('%-m/%-d/%Y'),
                        'cc': dict(),
                        'cc_total': 0.0,
                    }

    for row in cc_data:
        if len(row) == 19:
            crs_id = row[6]
            if crs_id in output and row[1] in ('MC', 'AX'):
                last_four = row[8]
                amount = -float(row[12])
                if last_four not in output[crs_id]['cc']:
                    output[crs_id]['cc'][last_four] = 0.0
                output[crs_id]['cc'][last_four] += amount
                output[crs_id]['cc_total'] += amount

    header = (
            'Confirmation #',
            'Expedia ID',
            'Departure',
            'Amount',
        )

    print(*header, sep=',')

    for crs_id, info in output.items():
        discrepancy = round(info['amount'] - info['cc_total'], 2)
        if discrepancy > 5 and info['amount'] != 0.0:
            if any(abs(info['amount'] - lf_amount) < 2 for lf_amount in info['cc'].values()):
                continue
            print(crs_id, info['exp_id'], info['departure'], discrepancy, sep=',')

if cc_data and res_data:
    process_evc(cc_data, res_data)
else:
    print('Missing reports.')

