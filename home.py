from flask import Flask, render_template, request

def home(cars):
    return render_template("home.html", cars=cars)
