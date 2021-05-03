import math
import random
import pymysql.cursors
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import urllib.request
import json
from operator import itemgetter

tomorrow_date = datetime.now() + timedelta(days=1)
tomorrow = tomorrow_date.strftime("%Y-%m-%d")

##Car assignment function
def assign_cars(people, cur, location):
    cur.execute(f'select * from Vehicle where location="{location}"')
    rows = cur.fetchall()
    early_passengers = []
    late_passengers = []
    for person in people:
        if (person['pickup'] == location) and (person['time'] == '7a'):
            early_passengers.append(person)
        elif (person['pickup'] == location) and (person['time'] == '9a'):
            late_passengers.append(person)
    early_car_count = math.ceil(len(early_passengers)/3)
    late_car_count = math.ceil(len(late_passengers)/3)
    early_car_list = []
    late_car_list = []
    for car in range(early_car_count):
        vehicle = random.choice(rows)
        early_car_list.append(vehicle[1])
        rows.remove(vehicle)
    for car in range(late_car_count):
        vehicle = random.choice(rows)
        late_car_list.append(vehicle[1])
        cur.execute(f'UPDATE Vehicle SET assignment="Summit" where name="{vehicle[1]}"')
        rows.remove(vehicle)
    for car in early_car_list:
        i = 0
        for passenger in early_passengers:
            if passenger['assignment'] == '':
                passenger['assignment'] = car
                i += 1
            if i == 3:
                break
    for car in late_car_list:
        i = 0
        for passenger in late_passengers:
            if passenger['assignment'] == '':
                passenger['assignment'] = car
                i += 1
            if i == 3:
                break
    return people


##Connect to daily schedule
conn = pymysql.connect(user='sched', password='sched', host='mysqlserver', database='schedules', autocommit=True)
cur = conn.cursor()
cur.execute(f'select * from dailySched where Date="{tomorrow}" and DelFlag = 0 order by Basecamp, startTime, Name')
rows = cur.fetchall()

employees_list = []
##Add all employees working that day to employee list
for row in rows:
    if row[6] == 'SU':
        dic = {'name':row[2],'pickup':row[4], 'destination':'SU', 'time':row[7], 'note':row[14], 'assignment': ''}
        employees_list.append(dic)

##Add night staff
url = "https://www.keck.hawaii.edu/software/db_api/telSchedule.php?"
sendUrl = "".join((url, f"cmd=getNightStaff&date={tomorrow}"))
data = urllib.request.urlopen(sendUrl)
data = data.read().decode("utf8")
data = json.loads(data)

night_staff = []
#TODO night staff assignment
for employee in data:

    if employee['Type'] in ['oa', 'oao', 'oat', 'oato', 'na', 'nah', 'na1', 'na2', 'nah2']:
        dic = {'name':f"{employee['LastName']}, {employee['FirstName']}", 'pickup':'HP', 'destination':'SU', 'time':'5:00 pm', 'note':'', 'assignment': 'K12'}
        night_staff.append(dic)

    if employee['Type'] in ['oao', 'oaro', 'nah2']:
        if employee['Type']=='oao':
            dic = {'name':f"{employee['LastName']}, {employee['FirstName']}", 'pickup':'', 'destination':'HP', 'time':'3:00 pm', 'note':'', 'assignment': 'K1'}
        elif employee['Type']=='oaro':
            dic = {'name':f"{employee['LastName']}, {employee['FirstName']}", 'pickup':'', 'destination':'HQ', 'time':'3:00 pm', 'note':'', 'assignment': 'K1'}
        elif employee['Type']=='nah2':
            dic = {'name':f"{employee['LastName']}, {employee['FirstName']}", 'pickup':'', 'destination':'HP', 'time':'9:30 pm', 'note':'', 'assignment': 'K1'}

        sendUrl2 = "".join((url, f"cmd=getEmployee&lastname={employee['LastName']}"))
        data2 = urllib.request.urlopen(sendUrl2)
        data2= data2.read().decode("utf8")
        data2 = json.loads(data2)
        if dic['pickup'] == '':
            dic['pickup'] = data2[0]['BaseCamp']
        #Skip if BaseCampe is Waimea and going to HQ
        if (dic['pickup']=='Waimea') and (dic['destination']=='HQ'):
            continue
        night_staff.append(dic)

##Add night staff to all employees
employees_list.extend(sorted(night_staff, key=itemgetter('pickup')))

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

#Pair people with cars
locations = ['Hilo', 'Waimea', 'HP']
conn = sqlite3.connect('/home/jpelletier/Documents/jpelletier/Transportation/fleet.db')
cur = conn.cursor()
for location in locations:
    employees_list = assign_cars(employees_list, cur, location)


##Create rideBoard
location = ''
time = ''
content = f"A ride board has been created for {tomorrow}.\n"
print(f"A ride board has been created for {tomorrow}.")
for employee in employees_list:
    if (employee['pickup'] != location) or (employee['time'] != time):
        location = employee['pickup']
        if location == 'Waimea':
            report_location = 'HQ'
        else:
            report_location = location
        time = employee['time']
        if time == '7a':
            report_time = '5:00 am'
        elif time == '9a':
            report_time = '7:00 am'
        elif time in ['3:00 pm', '5:00 pm', '9:30 pm']:
            report_time = time
        line = f"\n{report_location} to {employee['destination']} {report_time}\n"
        content += line
        print(f"{report_location} to {employee['destination']} {report_time}")
    if 'HP' in employee['note']:
        line = f"     {employee['name']} (HPP)\n"
        content += line
        print(f"     {employee['name']} {employee['assignment']} (HPP)")
    else:
        line = f"     {employee['name']}\n"
        content += line
        print(f"     {employee['name']} {employee['assignment']}")

##Email rideBoard
# msg = MIMEText(content)
# msg['Subject'] =f"Ride Board for {tomorrow}"
# msg['To'] = 'jpelletier@keck.hawaii.edu'
# msg['From'] = 'jpelletier@keck.hawaii.edu'
# s = smtplib.SMTP('localhost')
# s.send_message(msg)
# s.quit()
