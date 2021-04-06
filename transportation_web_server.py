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

from home import home

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    location = db.Column(db.String(20), nullable=False, default='Waimea')
    assignment = db.Column(db.String(20), unique=True)
    problem = db.Column(db.Boolean, nullable=False, default=False)
    reports = db.relationship('Report', backref='vehicle', lazy=True)

    def __repr__(self):
        return f"Vehicle('{self.name}', '{self.location}', '{self.problem}')"

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)

    def __repr__(self):
        return f"Report('{self.vehicle_id}', '{self.date_posted}', '{self.content}')"

@app.route('/',methods=['POST', 'GET'])
def home_():
    return home(Vehicle)

@app.route('/report_issue',methods=['POST', 'GET'])
def report_issue_():
    return render_template("report_issue.html")

@app.route('/view_issues',methods=['POST', 'GET'])
def viewissues_():
    return render_template("viewissues.html", vehicles=Vehicle.query.all())

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=50009)
