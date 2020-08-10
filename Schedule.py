import datetime
import pandas as pd
import numpy as np
from datetime import timezone
import csv
import math
from hungarian import Hungarian
import codecs


def boundaries_to_timestamps(start_date: str, end_date: str, date_format='%Y-%m-%d'):
    start_date_time_obj = datetime.datetime.strptime(start_date, date_format)
    end_date_time_obj = datetime.datetime.strptime(end_date, date_format)

    assert start_date_time_obj.year + 1 == end_date_time_obj.year

    min_timestamp = start_date_time_obj.replace(tzinfo=timezone.utc).timestamp()
    max_timestamp = end_date_time_obj.replace(tzinfo=timezone.utc).timestamp()

    return min_timestamp, max_timestamp


def holidays_to_timestamp(year1, year2, holidays_dates):
    ts_list_year1 = [datetime.datetime(year1, x[1], x[0]).replace(tzinfo=timezone.utc).timestamp() for x in
                     holidays_dates]
    ts_list_year2 = [datetime.datetime(year2, x[1], x[0]).replace(tzinfo=timezone.utc).timestamp() for x in
                     holidays_dates]
    return ts_list_year1 + ts_list_year2


def gen_days(min_timestamp, max_timestamp, holidays_dates, iso_weekday):
    """creates a list of days between timestamps, that is the weekday (1 monday, 7 sunday)"""
    date1 = datetime.datetime.fromtimestamp(min_timestamp).replace(tzinfo=timezone.utc)
    day = 60 * 60 * 24
    week = day * 7
    year1 = date1.year
    holidays = holidays_to_timestamp(year1, year1 + 1, holidays_dates)

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


def read_birthdays(file_in, year):
    """
    reads list of birthdays
    :param file_in: csv file file_in
    :param year: starting year
    :return: names and birthdays (lists)
    """
    df = pd.read_csv(file_in, delimiter=';', encoding="cp1250", names=['name', 'date'])
    df['day'] = df['date'].astype(str).str[:2]
    df['month'] = df['date'].astype(str).str[3:5]
    df['year'] = np.where((df['month'].astype(int) < 8), year + 1, year)
    df['timestamp'] = pd.to_datetime(df[['year', 'month', 'day']])
    people = df[['name', 'timestamp']].copy()

    names = people['name'].values.tolist()
    birthdays = [int(x / 1000000000) for x in people['timestamp'].values.tolist()]
    return names, birthdays


def write_schedule(file_out, result, names, nodes_meetings, birthdays):
    """
    writes schedule to csv
    """
    with codecs.open(file_out, 'w', "cp1250") as csvfile:
        fieldnames = ['meeting', 'name', 'birthday', 'difference[days]']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

        writer.writeheader()
        for pair in result:
            name = names[pair[0]]
            meeting = datetime.datetime.fromtimestamp(nodes_meetings[pair[1]]).replace(tzinfo=timezone.utc).date()
            birthday = datetime.datetime.fromtimestamp(birthdays[pair[0]]).replace(tzinfo=timezone.utc).date()
            distance = abs(birthday - meeting).days
            writer.writerow({'meeting': meeting, 'name': name, 'birthday': birthday, 'difference[days]': distance})


def make_schedule(file_in, file_out, boundaries, holidays_dates, weekday):
    meetings = [int(x) for x in
                gen_days(boundaries[0], boundaries[1], holidays_dates=holidays_dates, iso_weekday=weekday)]
    start_year = datetime.datetime.fromtimestamp(boundaries[0]).replace(tzinfo=timezone.utc).year
    names, birthdays = read_birthdays(file_in=file_in, year=start_year)

    persons_per_meeting = math.ceil(len(birthdays) / len(meetings))
    nodes_meetings = np.repeat(meetings, persons_per_meeting)

    # columns are meetings and rows are members
    matrix = [[int(abs(meeting - member) / 86400) for meeting in nodes_meetings] for member in birthdays]

    matching = Hungarian(matrix)
    matching.calculate()

    result = matching.get_results()
    potential = matching.get_total_potential()

    result = sorted(result, key=lambda tup: tup[1])

    write_schedule(file_out=file_out, result=result, names=names, nodes_meetings=nodes_meetings, birthdays=birthdays)

    print("potential:", potential)


if __name__ == '__main__':
    # list of pairs with holidays (day, month)
    holidays_list = [(2, 12), (6, 1), (24, 12), (30, 12), (27, 4)]

    # start and end date in format (yyyy-mm-dd)
    boundaries = boundaries_to_timestamps(start_date='2019-11-24',
                                          end_date='2020-6-15',
                                          date_format='%Y-%m-%d')

    make_schedule(file_in='example_data/birthdays.csv',
                  file_out='example_data/schedule_2019_20.csv',
                  boundaries=boundaries,
                  holidays_dates=holidays_list,
                  weekday=1)  # (1 monday, 7 sunday)
