import pymysql.cursors
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import urllib.request
import json

tomorrow_date = datetime.now() + timedelta(days=1)
tomorrow = tomorrow_date.strftime("%Y-%m-%d")


##Connect to daily schedule
conn = pymysql.connect(user='sched', password='sched', host='mysqlserver', database='schedules', autocommit=True)
cur = conn.cursor()
cur.execute(f'select * from dailySched where Date="{tomorrow}" and DelFlag = 0 order by Basecamp, startTime, Name')
rows = cur.fetchall()

employees_list = []
##Add all employees working that day to employee list
for row in rows:
    if row[6] == 'SU':
        dic = {'name':row[2],'pickup':row[4], 'destination':'SU', 'time':row[7], 'note':row[14]}
        employees_list.append(dic)

##Add night staff
url = "https://www.keck.hawaii.edu/software/db_api/telSchedule.php?"
sendUrl = "".join((url, f"cmd=getNightStaff&date={tomorrow}"))
data = urllib.request.urlopen(sendUrl)
data = data.read().decode("utf8")
data = json.loads(data)

for employee in data:
    if employee['Type']=='oao':
        dic = {'name':f"{employee['LastName']}, {employee['FirstName']}", 'pickup':'', 'destination':'SU', 'time':'3:00 pm'}
    elif employee['Type']=='oaro':
        dic = {'name':f"{employee['LastName']}, {employee['FirstName']}", 'pickup':'', 'destination':'HQ', 'time':'3:00 pm'}
    elif employee['Type']=='nah2':
        dic = {'name':f"{employee['LastName']}, {employee['FirstName']}", 'pickup':'', 'destination':'SU', 'time':'9:30 pm'}
    elif employee['Type'] in ['oa', 'na', 'nah', 'oao', 'oaro']:
        dic = {'name':f"{employee['LastName']}, {employee['FirstName']}", 'pickup':'HP', 'destination':'SU', 'time':'5:00 pm'}
    sendUrl2 = "".join((url, f"cmd=getEmployee&lastname={employee['LastName']}"))
    data2 = urllib.request.urlopen(sendUrl2)
    data2= data2.read().decode("utf8")
    data2 = json.loads(data2)
    if dic['pickup'] == '':
        dic['pickup'] = data2[0]['BaseCamp']
    #Skip if BaseCampe is Waimea and going to HQ
    if (dic['pickup']=='Waimea') and (dic['destination'=='HQ']):
        continue
    employees_list.append(dic)

##Connect to pcal (leave) database
conn = pymysql.connect(user='pcal', password='pcal', host='mysqlserver', database='pcal', autocommit=True)
cur = conn.cursor()
cur.execute(f'select * from loa where FromDate<="{tomorrow}" and ToDate>="{tomorrow}"')
rows = cur.fetchall()
##Remove employees on leave
for employee in employees_list:
    for row in rows:
        if employee['name'] == row[1]:
            employees_list.remove(employee)

##Create rideBoard with daytime staff
location = ''
time = ''
content = f"A ride board has been created for {tomorrow}.\n"
print(f"A ride board has been created for {tomorrow}.")
for employee in employees_list:
    if (employee['pickup'] != location) or (employee['time'] != time):
        location = employee['pickup']
        time = employee['time']
        if time == '7a':
            time = '5:00 am'
        elif time == '9a':
            time = '7:00 am'
        line = f"\n{location} to SU {time}\n"
        content += line
        print(f"{location} to SU {time}")
    if 'HP' in employee['note']:
        line = f"     {employee['name']} (HPP)\n"
        content += line
        print(f"     {employee['name']} (HPP)")
    else:
        line = f"     {employee['name']}\n"
        content += line
        print(f"     {employee['name']}")

##Email rideBoard
msg = MIMEText(content)
msg['Subject'] =f"Ride Board for {tomorrow}"
msg['To'] = 'jpelletier@keck.hawaii.edu'
msg['From'] = 'jpelletier@keck.hawaii.edu'
s = smtplib.SMTP('localhost')
s.send_message(msg)
s.quit()
