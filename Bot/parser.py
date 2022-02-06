import requests
from bs4 import BeautifulSoup
import lxml
from datetime import datetime
import sqlite3
import time

current_datetime = datetime.now()
current_weekday = current_datetime.weekday()

db = sqlite3.connect('table.db', check_same_thread=False)
sql = db.cursor()
db.commit()


def kan_check(day, gr):
    sql.execute(f"SELECT link FROM groups_link WHERE group_number = '{gr}'")
    link = sql.fetchone()[0]
    db.commit()
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'lxml')

    table_on_week_bs = soup.find_all(
        class_='table table-bordered table-condensed visible-xs visible-sm table-lessons noprint odd')
    if not table_on_week_bs:
        return True
    else:
        return False


def get_table(day, gr):
    print(day)
    print(gr)
    sql.execute(f"SELECT link FROM groups_link WHERE group_number = '{gr}'")
    link = sql.fetchone()[0]
    db.commit()
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'lxml')

    if day == 0:
        week_day = 'Monday'
    elif day == 1:
        week_day = 'Tuesday'
    elif day == 2:
        week_day = 'Wednesday'
    elif day == 3:
        week_day = 'Thursday'
    elif day == 4:
        week_day = 'Friday'
    elif day == 5:
        week_day = 'Saturday'

    table_on_week_bs = soup.find_all(
        class_='table table-bordered table-condensed visible-xs visible-sm table-lessons noprint odd')
    if kan_check(day, gr):

        table = (
            str('Каникулы!'), str('Каникулы!'), str('Каникулы!'), str('Каникулы!'), str('Каникулы!'), str(week_day),
            str(gr))

        return table

    else:

        day_bs = table_on_week_bs[day].find_all('div', class_="hidden for_print")

        table = []

        discipline_num = 0
        for i in day_bs:
            discipline_num += 1

            if i.find('span', class_='discipline') is not None:
                discipline = i.find('span', class_='discipline').text
            else:
                discipline = str(None)

            if i.find('span', class_='kind') is not None:
                kind = i.find('span', class_='kind').text
            else:
                kind = str(None)

            if i.find('span', class_='auditorium') is not None:
                auditorium = i.find('span', class_='auditorium').text
            else:
                auditorium = str(None)

            if i.find('span', class_='group') is not None:
                teacher = i.find('span', class_='group').text
            else:
                teacher = str(None)

            tup_table = tuple(
                [str(discipline_num), str(discipline), str(kind), str(auditorium), str(teacher), str(week_day),
                 str(gr)])
            table.append(tup_table)

    return table


def insert():
    global sql, db

    sql.execute("SELECT group_number FROM groups_link")
    groups = []
    for i in sql.fetchall():
        groups.append(i[0])

    db.commit()

    query = "INSERT INTO schedule VALUES(?, ?, ?, ?, ?, ?, ?)"
    for group in groups:
        for day in range(6):
            if not kan_check(day, group):
                sql.executemany(query, get_table(day, group))
            else:
                sql.execute(query, get_table(day, group))


while True:
    if current_weekday == 0:
        sql.execute("DELETE FROM schedule ")
        db.commit()
        insert()
        delay = 60 * 60 * 24 * 7
        time.sleep(delay)
