import pymysql.cursors
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

todaydate = datetime.now() + timedelta(days=1)
today = todaydate.strftime("%Y-%m-%d")

conn = pymysql.connect(user='sched', password='sched', host='mysqlserver', database='schedules', autocommit=True)
cur = conn.cursor()
cur.execute(f'select * from dailySched where Date="{today}" and DelFlag = 0 order by Basecamp, startTime, Name')
rows = cur.fetchall()

employees_list = []

for row in rows:
    if row[6] == 'SU':
        dic = {'name':row[2],'pickup':row[4],'time':row[7], 'note':row[14]}
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
content = f"A rideboard has been created for {today}."
print(f"A rideboard has been created for {today}.")
for employee in employees_list:
    if (employee['pickup'] != location) or (employee['time'] != time):
        location = employee['pickup']
        time = employee['time']
        line = f"{location} to SU {time}\n"
        content += line
        print(f"{location} to SU {time}")
    if 'HP' in employee['note']:
        line = f"     {employee['name']} (HPP)\n"
        content += line
        print(f"     {employee['name']} (HPP)")
    else:
        line = f"     {employee['name']} (HPP)\n"
        content += line
        print(f"     {employee['name']}")


msg = MIMEText(content)
msg['Subject'] =f"Rideboard for {today}"
msg['To'] = 'jpelletier@keck.hawaii.edu'
msg['From'] = 'jpelletier@keck.hawaii.edu'
s = smtplib.SMTP('localhost')
s.send_message(msg)
s.quit()
