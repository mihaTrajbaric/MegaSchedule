import datetime
import pandas as pd
import numpy as np
from datetime import timezone
import csv
from hungarian import Hungarian

global holidays_list


def min_max_timestamp(start_year=2018, start_day=1, start_month=10, end_year=2019, end_day=25, end_month=6):
    """nekako studentsko solsko leto"""
    min_timestamp = (datetime.datetime(start_year, start_month, start_day).replace(tzinfo=timezone.utc).timestamp())
    max_timestamp = (datetime.datetime(end_year, end_month, end_day).replace(tzinfo=timezone.utc).timestamp())
    return min_timestamp, max_timestamp


def holidays_to_timestamp(year1, year2):
    ts_list_year1 = [datetime.datetime(year1, x[1], x[0]).replace(tzinfo=timezone.utc).timestamp() for x in holidays_list]
    ts_list_year2 = [datetime.datetime(year2, x[1], x[0]).replace(tzinfo=timezone.utc).timestamp() for x in holidays_list]
    return ts_list_year1 + ts_list_year2


def gen_days(min_timestamp, max_timestamp, iso_weekday):
    """creates a list of every day between timestamps, that is the weekday (1 monday, 7 sunday)"""
    date1 = datetime.datetime.fromtimestamp(min_timestamp).replace(tzinfo=timezone.utc)
    day = 60 * 60 * 24
    week = day * 7
    year1 = date1.year
    holidays = set(holidays_to_timestamp(year1,year1+1))

    min_weekday = date1.isoweekday()
    diff = iso_weekday - min_weekday
    if diff < 0:
        diff += 7

    timestamp_list = []
    timestamp = min_timestamp + diff * day
    while timestamp <= max_timestamp:
        if timestamp not in holidays:
            timestamp_list.append(timestamp)
        timestamp += week
    return timestamp_list


def read_birthsdays(file_in):
    """
    reads list of birthsdays
    :param file_in: csv file file_in
    :return: names and birthsdays (lists)
    """
    df = pd.read_csv(file_in, delimiter=';', encoding="utf8", names=['name', 'date'])
    leto = datetime.datetime.now().year
    df['day'] = df['date'].astype(str).str[:2]
    df['month'] = df['date'].astype(str).str[3:5]
    df['year'] = np.where((df['month'].astype(int) < 8), leto + 1, leto)
    df['timestamp'] = pd.to_datetime(df[['year', 'month', 'day']])
    ljudje = df[['name', 'timestamp']].copy()

    imena = ljudje['name'].values.tolist()
    rojstni_dnevi = [int(x / 1000000000) for x in ljudje['timestamp'].values.tolist()]
    return imena, rojstni_dnevi


def write_schedule(file_out, result, imena, vaje_vozlisca, rojstni_dnevi):
    """
    writes schedule to csv
    """
    with open(file_out, 'w') as csvfile:
        fieldnames = ['vaja', 'ime', 'rojstni dan', 'dni']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

        writer.writeheader()
        for par in result:
            ime = imena[par[0]]
            vaja = datetime.datetime.fromtimestamp(vaje_vozlisca[par[1]]).replace(tzinfo=timezone.utc).date()
            rojstni_dan = datetime.datetime.fromtimestamp(rojstni_dnevi[par[0]]).replace(tzinfo=timezone.utc).date()
            razdalja = abs(rojstni_dan - vaja).days

            writer.writerow({'vaja': vaja, 'ime': ime, 'rojstni dan': rojstni_dan, 'dni': razdalja})


def run(file_in, file_out, boundaries):
    vaje = [int(x) for x in gen_days(boundaries[0], boundaries[1], 1)]
    imena, rojstni_dnevi = read_birthsdays(file_in=file_in)
    # ker castita dva na vajo podvojimo vsak element
    vaje_vozlisca = []
    mnozica = [0]
    while len(vaje_vozlisca) < len(rojstni_dnevi):

        vaje_vozlisca = [x for x in vaje for _ in mnozica]
        mnozica.append(0)

    assert len(vaje_vozlisca) >= len(rojstni_dnevi)

    # vsak stolpec ena vaja, vrstica en clovek
    matrika = [[int(abs(vaja - clovek) / 86400) for vaja in vaje_vozlisca] for clovek in rojstni_dnevi]

    matching = Hungarian(matrika)
    matching.calculate()

    result = matching.get_results()
    potential = matching.get_total_potential()

    result = sorted(result, key=lambda tup: tup[1])

    write_schedule(file_out=file_out, result=result, imena=imena, vaje_vozlisca=vaje_vozlisca,
                   rojstni_dnevi=rojstni_dnevi)

    print("potential:", potential)


if __name__ == '__main__':
    holidays_list = [(24, 12), (31, 12), (29, 4)]
    a = min_max_timestamp(start_year=2018, start_month=11, start_day=26)
    run(file_in='letosnji_custom.csv', file_out='razpored_test.csv', boundaries=a)

