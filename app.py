from firebase_admin import credentials, initialize_app, firestore
from flask import Flask, Blueprint, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("key.json")
initialize_app(cred)
db = firestore.client()
#user_Ref = db.collection('research')


@app.route('/add', methods = ['POST'])
def add():

    # endpoint can be used to ADD or EDIT records to Firebase
    # Pass it a username as an get argument

    username = request.json['username']
    summary = request.json['summary']
    questions = request.json['questions']
    answers = request.json['answers']
    recommendations = request.json['recommendations']
    content = request.json['content']
    title = request.json['title']

    try:
        input = {'Title': title, 'Content': content, 'Summary': summary, "Questions": questions, "Answers": answers, "Recommendations": recommendations}
        db.collection(str(username)).document(str(title)).set(input)
    except Exception as e:
        return f"An Error Occured: {e}"


@app.route('/get', methods = ['GET'])
def get():

    # Pass it a username as an get argument

    username = request.json['username']
    summary = request.json['summary']
    questions = request.json['questions']
    answers = request.json['answers']
    recommendations = request.json['recommendations']
    content = request.json['content']
    title = request.json['title']

    try:
        input = {'Title': title, 'Content': content, 'Summary': summary, "Questions": questions, "Answers": answers, "Recommendations": recommendations}
        db.collection(str(username)).document(str(title)).set(input)
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/delete', methods = ['DELETE'])
def delete():

    pass


if __name__ == "__main__":
    app.run(debug=True)