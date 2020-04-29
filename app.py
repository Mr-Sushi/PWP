import math
from flask import Flask, request
app = Flask("something")

@app.route("/client/")
def index():
    return app.send_static_file("html/client.html")