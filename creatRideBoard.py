import pymysql.cursors
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

conn = pymysql.connect(user='sched', password='sched', host='mysqlserver', database='schedules', autocommit=True)
cur = conn.cursor()
cur.execute(f'select * from dailySched where Date="{today}" order by Basecamp, startTime, Name')
rows = cur.fetchall()

employees_list = []

for row in rows:
    if row[6] == 'SU':
        dic = {'name':row[2],'pickup':row[4],'time':row[7]}
        employees_list.append(dic)

conn = pymysql.connect(user='pcal', password='pcal', host='mysqlserver', database='pcal', autocommit=True)
cur = conn.cursor()
cur.execute(f'select * from loa where FromDate<="{today}" and ToDate>="{today}"')
rows = cur.fetchall()
for employee in employees_list:
    for row in rows:
        if employee['name'] == row[1]:
            employees_list.remove(employee)

location = ''
time = ''
for employee in employees_list:
    if (employee['pickup'] != location) or (employee['time'] != time):
        location = employee['pickup']
        time = employee['time']
        print(f"{location} to SU {time}")
    print(employee['name'])
