import json
from flask import Flask, request, jsonify

app = Flask(__name__)

app.route("/check", ['POST'])
def spell_check():
    #Get data body
    data = request.get_json()
    
    #Predict
    predict = 0
    #
    return jsonify(predict)

if __name__ == "__main__":
    app.run(debug=True)