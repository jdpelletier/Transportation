from flask import Flask, render_template

def home():
    k2_assigned = "njordan"
    k3_assigned = "jpelletier"
    k4_assigned = "N/A"
    k2_problem = False
    k3_problem = False
    k4_problem = True
    k2_location = "Waimea"
    k3_location = "Hilo"
    k4_location = "HP"
    K2 = {
        "name": "K4",
        "location": k2_location,
        "assigned": k2_assigned,
        "issue": k2_problem
    }
    K3 = {
        "name": "K4",
        "location": k3_location,
        "assigned": k3_assigned,
        "issue": k3_problem
    }
    K4 = {
        "name": "K4",
        "location": k4_location,
        "assigned": k4_assigned,
        "issue": k4_problem
    }
    cars = [K2, K3, K4]

    return render_template("home.html", cars=cars)
