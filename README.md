# MegaSchedule
Software for making a schedule of who should bring snacks to your weekly evening activity. 

## Problem

This problem can occur during certain evening activates (book club, LAN party, choir rehearsal,...).

Since it is always a good idea to enjoy snacks at the end of activity or during break, some clubs have a tradition that everybody takes care of it when it has birthday.
This system is far from perfect, mainly due to two reasons:
- birthdays are not distributed evenly
- there is always someone who 'forgets' on his birthday. Which of course is not cool. 

## Solution
MegaSchedule is solving this problem by introducing a schedule of who has to bring the snacks in a way that everybody takes care of this as close to their birthday as possible.
Script uses mathematically proven algorithm that minimizes average distance between member's birthday and date which is assigned to him.


### Mathematical background
MegaSchedule creates a complete bipartite graph G=(S,T;E) with n member vertices (S), n meeting vertices (T) and n*n edges (E).
Since number of members (n) and meetings (m) do not always match, alghorithm takes care of it:
- [m > n] it creates more then one vertice for each meeting. In this case more then one member will be assigned to some meetings.
- [m < n] it adds dummy meeting nodes (in form of padding to matrix). In this case not all meetings will be assigned to members.
Each edge has a nonnegative cost c(i,j) which represents distance (in days) between members's birthday and meeting date.
We want to find a perfect matching with a minimum total cost.
This script uses [Thom Dedecko's implementation](http://github.com/tdedecko/hungarian-algorithm) of [hungarian method](http://en.wikipedia.org/wiki/Hungarian_algorithm) for solving this problem.

## How to use MegaSchedule
### Input file format
Input file should be csv with delimiter ';' and two fields[name, date]. See [example](example_data/birthdays.csv).
### Parameters
- `file_in`: path to input file in [Input file format](#input-file-format)
- `file_out`: path to output file in csv format.
- `boundaries`: timestamps of start and end of activity
- `holidays_dates`: list of pairs with holidays (day, month), when activity will be canceled.
- `weekday`: day in the week of activity. Monday is 1, sunday is 7 etc.

### Sample code
```python
from Schedule import make_schedule, boundaries_to_timestamps

# list of pairs with holidays (day, month), when activity will be canceled
holidays_list = [(2, 12), (6, 1), (24, 12), (30, 12), (27, 4)]

# start and end date of activity in format (yyyy-mm-dd)
boundaries = boundaries_to_timestamps(start_date='2019-11-24',
                                      end_date='2020-6-15')

make_schedule(file_in='example_data/birthdays.csv',
              file_out='example_data/schedule_2019_20.csv',
              boundaries=boundaries,
              holidays_dates=holidays_list,
              weekday=1)  # (1 monday, 7 sunday)

```
