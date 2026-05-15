from flask import Flask
import random

app = Flask(__name__)

@app.route("/")
def home():
    if random.random() > 0.6:
        raise Exception("Simulated crash!")
    return "Healthy"

app.run(host="0.0.0.0", port=5000)
