import os
import datetime

from werkzeug.urls import url_parse
from flask import Flask, request, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

from home import home

k2_assigned = "njordan"
k3_assigned = "jpelletier"
k4_assigned = "N/A"
k2_problem = False
k3_problem = False
k4_problem = True
k2_location = "Waimea"
k3_location = "Hilo"
k4_location = "HP"
k2_report = "n/a"
k3_report = "n/a"
k4_report = "This car is missing it's rearview mirror. -jpelletier 04/05/21"
K2 = {
    "name": "K4",
    "location": k2_location,
    "assigned": k2_assigned,
    "issue": k2_problem,
    "issue_report": k2_report
}
K3 = {
    "name": "K4",
    "location": k3_location,
    "assigned": k3_assigned,
    "issue": k3_problem,
    "issue_report": k3_report
}
K4 = {
    "name": "K4",
    "location": k4_location,
    "assigned": k4_assigned,
    "issue": k4_problem,
    "issue_report": k4_report
}
cars = [K2, K3, K4]

@app.route('/',methods=['POST', 'GET'])
def home_():
    return home(cars)

@app.route('/report_issue',methods=['POST', 'GET'])
def report_issue_():
    return render_template("report_issue.html")

@app.route('/view_issues',methods=['POST', 'GET'])
def viewissues_():
    return render_template("viewissues.html", cars=cars)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=50009)
