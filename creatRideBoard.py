import pymysql.cursors
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

conn = pymysql.connect(user='sched', password='sched', host='mysqlserver', database='schedules', autocommit=True)
cur = conn.cursor()
cur.execute(f'select * from dailySched where Date="{today}" order by startTime, Basecamp, Name')
rows = cur.fetchall()

employees_list = []

for row in rows:
    if row[6] == 'SU':
        dic = {'name':row[2],'pickup':row[4],'time':row[7]}
        employees_list.append(dic)

print(employees_list)
