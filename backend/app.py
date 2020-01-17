""" """
import json
import requests
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/markers', methods=['GET'])
def get_markers():
    return ""


@app.route('/alive', methods=['GET'])
def alive():
    return "yes"

@app.route('/markers', methods=['PUT'])
def set_marker():
    json.dump(request.json, open("markers.jsonl", 'a', newline='\n') )
    return "200 - OK"

@app.route('/food_types', methods=["GET"])
def food_types():
    return ','.join(["berry", "apple"])

if __name__ == "__main__":
    app.run()