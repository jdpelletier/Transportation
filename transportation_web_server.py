import os
import datetime

from werkzeug.urls import url_parse
from flask import Flask, request, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:\Users\johnp\Desktop\Keck\Software\Transportation\fleet.db'
db = SQLAlchemy(app)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    location = db.Column(db.String(20), nullable=False, default='Waimea')
    assignment = db.Column(db.String(20), unique=True)
    problem = db.Column(db.Boolean, nullable=False, default=False)
    reports = db.relationship('Report', backref='vehicle', lazy=True)

    def __repr__(self):
        return f"Vehicle('{self.name}', '{self.location}', '{self.problem}', '{self.assignment}')"

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    resolved = db.Column(db.Boolean, nullable=False, default=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)

    def __repr__(self):
        return f"Report('{self.vehicle_id}', '{self.date_posted}', '{self.content}', '{self.resolved}')"

@app.route('/', methods=['POST', 'GET'])
def statuspage():
    return render_template("statuspage.html", vehicles=Vehicle.query.order_by(Vehicle.name).all())

@app.route('/report_issue', methods=['POST', 'GET'])
def report_issue_():
    return render_template("report_issue.html", vehicles=Vehicle.query.order_by(Vehicle.name).all())

@app.route('/report_confirmed', methods=['POST'])
def report_confirmed_():
    text = request.form.get("issuetext")
    vehicle_name = request.form.get("vehicleselect")
    vehicle = Vehicle.query.filter_by(name=vehicle_name).first()
    vehicle.problem = True
    report = Report(content=text, vehicle_id=vehicle.id)
    db.session.add(report)
    db.session.commit()
    return render_template("report_confirmed.html")

@app.route('/view_issues', methods=['POST', 'GET'])
def viewissues_():
    return render_template("viewissues.html", vehicles=Vehicle.query.order_by(Vehicle.name).all())

@app.route('/resolve_issue', methods=['POST'])
def resolve_issue_():
    resolution_id = request.form['submit']
    report = Report.query.filter_by(id=resolution_id).first()
    vehicle = Vehicle.query.get(report.vehicle_id)
    return render_template("resolve_issue.html", vehicle=vehicle, report=report)

@app.route('/resolution_confirmed', methods=['POST'])
def resolution_confirmed_():
    text = request.form.get("resolutiontext")
    resolution_id = request.form['submit']
    report = Report.query.filter_by(id=resolution_id).first()
    report.resolved=True
    vehicle = Vehicle.query.get(report.vehicle_id)
    resolved_list = []
    reports = Report.query.filter_by(vehicle_id=report.vehicle_id).all()
    for problem in reports:
        resolved_list.append(problem.resolved)
    if all(resolved_list):
        vehicle.problem = False
    # resolution = Report(content=text, vehicle_id=vehicle.id, resolved=True)
    # db.session.add(resolution)
    db.session.commit()
    return render_template("resolution_confirmed.html")

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=50009)
