# C:/Python312/python.exe -m flask --app server/api run
from flask import Flask
import torch

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello, World!", 200

@app.route("/model/<imgfile>")
def model(imgfile):
    pass