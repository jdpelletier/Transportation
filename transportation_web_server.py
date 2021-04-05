import os
import datetime

from werkzeug.urls import url_parse
from flask import Flask, request, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

from home import home

@app.route('/',methods=['POST', 'GET'])
def home_():
    return home()


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=50009)
