from flask import Flask, render_template, request

def home(Vehicle):
    return render_template("home.html", vehicles=Vehicle.query.all())
