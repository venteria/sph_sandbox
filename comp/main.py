import csv
import os
import datetime as dt

strptime = dt.datetime.strptime


tran_data = list()
guest_data = list()

for fn in os.listdir('data'):
    if fn.endswith('.csv'):
        with open('data/' + fn) as f:
            data = list(csv.reader(f))
        if data[0][1:3] == ['Transaction_Type', 'Charge_Code']:
            tran_data = data
        elif data[0][1:3] == ['Confirmation_Number', 'Status']:
            guest_data = data

if tran_data and guest_data:
    user_input = input('Do you want to print a list of (g)uests or (d)ates?')
    if user_input == 'g':
        print_type = 'guests'
    elif user_input == 'd':
        print_type = 'dates'
    else:
        print('Unknown option.')
        quit()
    final = dict()
    final_alt = dict()
    min_date = strptime(tran_data[-2][2], '%d %b %Y').date()
    max_date = strptime(tran_data[-2][3], '%d %b %Y').date()
    for row in guest_data[1:]:
        if len(row) > 12:
            guest_name = row[0]
            crs_id = row[1]
            status = row[3]
            if status not in ('Checked Out', 'In House'):
                continue
            arrival = strptime(row[4], '%b %d, %Y').date()
            departure = strptime(row[5], '%b %d, %Y').date()

            today = dt.date.today()

            until_date = min(departure, today)
            if until_date - arrival == 0:
                continue

            if crs_id not in final:
                final[crs_id] = {
                        'dates': list(),
                        'output': [
                                crs_id,
                                guest_name,
                                status,
                                arrival,
                                departure,
                                (departure - arrival).days,
                            ],
                    }

            date = arrival
            while date < until_date:
                if min_date <= date <= max_date:
                    final[crs_id]['dates'].append(date)
                date += dt.timedelta(1)

    for row in tran_data[1:]:
        if len(row) > 12:
            code = row[2]
            if code != 'RM':
                continue
            date = strptime(row[0], '%b %d, %Y').date()
            crs_id = row[5]
            amount = float(row[11])
            if amount < 0:
                continue
            if crs_id not in final:
                continue
            if date in final[crs_id]['dates']:
                final[crs_id]['dates'].remove(date)

    for crs_id in list(final.keys()):
        if len(final[crs_id]['dates']) == 0:
            del final[crs_id]
        else:
            for date in final[crs_id]['dates']:
                if date not in final_alt:
                    final_alt[date] = list()
                final_alt[date].append(crs_id)
            if final[crs_id]['output'][-1] == len(final[crs_id]['dates']):
                final[crs_id]['output'].append('Entire stay')
            else:
                final[crs_id]['output'].append(', '.join([
                        d.strftime('%-m/%-d')
                        for d in
                        final[crs_id]['dates']
                    ]))

    if print_type == 'guests':
        print()
        for entry in final.values():
            print(*entry['output'], sep=';')

    else:
        output = sorted(list(final_alt.items()), key=lambda x: x[0])
        for date, crs_nums in output:
            print()
            print(date.isoformat(), len(crs_nums), sep=':')
            print(*crs_nums, sep='\n')
else:
    print('Missing reports.')
