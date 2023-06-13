import csv
import os
import datetime as dt
import copy


OTA_TE_RATE_PLANS = [
        'SS1',
        'SOE',
        'SOR',
        'SOA',
        'SF1',
        'SF2',
        'SF3',
        'SOQPL2',
        'SOQHL3',
        'SOQHL2',
        'SOQPL1',
        'LNZM',
        'SPD5',
        'SEG',
        'SEG2',
        'SDO',
        'SMAO',
        'SMA1',
        'SMA2',
        'SOGC',
        'SP5',
        'SPD3',
        'SPD7',
        'SHOP1',
        'SH2C',
    ]

OTA_TE_RATE_PLANS_INC = [
        'SOEP',
        'SMA1P',
        'SSP',
        'SED',
        'S3A',
        'SAP',
        'SWR1',
        'SPD5P',
        'LC1X',
]

input(
        'Please collect the following files from SPH in CSV format and put '
        'them in the "data" folder:\n\n'
        ' *** Front Office > Standard Guest List\n'
        ' *** Accounting > Tax Exempt\n\n'
        'Once that is done, press any key to continue.'
    )

guest_data = None
te_data = None

for fn in os.listdir('data'):
    if fn.endswith('.csv'):
        with open('data/' + fn) as f:
            data = list(csv.reader(f))
        if data[0][2:5] == ['Status', 'Secondary_Status', 'Arrival_Date']:
            guest_data = data
        elif data[0][2:5] == ['GUEST_NAME', 'CONFIRM_NO', 'Exempt_Type']:
            te_data = data

if not te_data:
    print('Missing tax-exempt data.')
if not guest_data:
    print('Missing guest data.')

if te_data and guest_data:
    cleaned_data = dict()
    for row in te_data:
        if len(row) > 7:
            date = row[0]
            rate_plan = row[1]
            crs_num = row[3]
            amount = row[7]

            if len(crs_num) != 13:
                continue

            if crs_num not in cleaned_data:
                cleaned_data[crs_num] = { 'rate_plan': rate_plan,
                                'dates': list(),
                                'amount': 0.0,
                        }
            if date not in cleaned_data[crs_num]['dates']:
                cleaned_data[crs_num]['dates'].append(date)
                cleaned_data[crs_num]['amount'] += float(amount)
                cleaned_data[crs_num]['amount'] = round(
                        cleaned_data[crs_num]['amount'], 2
                    )
    for row in guest_data:
        if len(row) > 8:
            crs_num = row[1]
            guest_name = row[0]
            room_num = row[11]
            if crs_num not in cleaned_data:
                continue
            date_ci = dt.datetime.strptime(row[4], '%b %d, %Y')
            date_co = dt.datetime.strptime(row[5], '%b %d, %Y')
            cleaned_data[crs_num]['los'] = (date_co - date_ci).days
            cleaned_data[crs_num]['guest_data'] = [
                    crs_num,
                    guest_name,
                    date_ci,
                    date_co,
                    room_num,
                    cleaned_data[crs_num]['rate_plan'],
                    cleaned_data[crs_num]['amount'],
                ]

    data_totals = {
            'ext_stay': 0.0,
            'ota': 0.0,
            'mistake': 0.0,
            'other': 0.0,
            'total': 0.0,
            'other_rp': list(),
            'other_crs': list(),
            'mistake_crs': list(),
        }

    for crs_num, subdata in copy.copy(cleaned_data).items():
        if subdata['amount'] == 0.0:
            del cleaned_data[crs_num]
            continue
        data_totals['total'] += subdata['amount']
        rate_plan = subdata['rate_plan']
        if subdata['los'] >= 30:
            category = 'ext_stay'
        elif rate_plan in OTA_TE_RATE_PLANS:
            category = 'ota'
        elif rate_plan.startswith('SBK') or rate_plan in OTA_TE_RATE_PLANS_INC:
            category = 'mistake'
            data_totals['mistake_crs'].append(crs_num)
        else:
            category = 'other'
            if rate_plan not in data_totals['other_rp']:
                data_totals['other_rp'].append(rate_plan)
            data_totals['other_crs'].append(crs_num)
        data_totals[category] += subdata['amount']

    for key in data_totals:
        if type(data_totals[key]) == float:
            data_totals[key] = round(data_totals[key], 2)

    print(
            f"\nTotal Tax-Exempt Revenue;{data_totals['total']}"
            f"\n30+ Night Guests;{data_totals['ext_stay']}"
            f"\nOTA Prepaids;{data_totals['ota']}"
            f"\nOther;{data_totals['other']+data_totals['mistake']}"
            "\n\nFlagged reservations:"
        )

    columns = [
            'Type',
            'Confirmation #',
            'Guest Name',
            'Arrival',
            'Departure',
            'Room #',
            'Rate Plan',
            'Exempted Revenue',
        ]

    print(*columns, sep=';')
    for crs_num in data_totals['mistake_crs']:
        print(*([
                'I think incorrectly exempted'
            ]+cleaned_data[crs_num]['guest_data']), sep=';')
    for crs_num in data_totals['other_crs']:
        print(*(['']+cleaned_data[crs_num]['guest_data']), sep=';')

    print()
    for rp in data_totals['other_rp']:
        print(rp)
