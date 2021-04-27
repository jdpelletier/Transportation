import pymysql.cursors
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

conn = pymysql.connect(user='sched', password='sched', host='mysqlserver', database='schedules', autocommit=True)
cur.execute(f'select * from dailySched where Date={today}')
rows = cur.fetchall()

for row in rows:
    if row[6] == 'SU':
        print(row[2])
