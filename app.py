from flask import Flask, request, jsonify
from predict import predict_sentence
from test import translate

app = Flask(__name__)

@app.route("/predict", methods=['POST'])
def spell_check():
    #Get data body
    data = request.get_json()
    
    #Predict
    predict = predict_sentence(data['text'])
    trans = translate(data['text'])
    #
    res = {
        "predict": predict,
        "translate": trans
    }
    return jsonify(res)

if __name__ == "__main__":
    app.run(debug=True)