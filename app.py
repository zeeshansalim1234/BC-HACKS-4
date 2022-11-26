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
        return jsonify({'status': "success"}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    


@app.route('/get', methods = ['GET'])
def get():

    username = request.args.get('username')
    myTitle = request.args.get('title')

    try:
        result = db.collection(username).document(myTitle).get()
        if result.exists:
            return jsonify(result.to_dict()), 200
                
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/delete', methods = ['DELETE'])
def delete():

    username = request.args.get('username')
    myTitle = request.args.get('title')

    try:
        result = db.collection(username).document(myTitle).delete()
        return jsonify({'status': "success"}), 200
                
    except Exception as e:
        return f"An Error Occured: {e}"

if __name__ == "__main__":
    app.run(debug=True)