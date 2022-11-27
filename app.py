from firebase_admin import credentials, initialize_app, firestore
from flask import Flask, Blueprint, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import pickle
import json
import torch
from sentence_transformers import SentenceTransformer, util
from google.cloud import language 

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("key.json")
initialize_app(cred)
db = firestore.client()
#user_Ref = db.collection('research') 

@app.route('/', methods = ['GET'])
def home():

    return jsonify({'message': "Hello World"}), 200

@app.route('/tags', methods = ['POST'])
def tags():
    pass 

@app.route('/recommendations', methods = ['POST'])
def recommendations():

    #model = SentenceTransformer('allenai-specter')

    title = request.json['title']
    abstract = request.json['summary']

    with open("model.sav", "rb") as f:
        model = pickle.load(f)
    
    with open("papers.json") as fin:
        papers = json.load(fin)

    corpus_embeddings = torch.load('tensor_research_papers.pt')  # 974 paper embeddings

    query_embedding = model.encode(title+'[SEP]'+abstract, convert_to_tensor=True)
    search_hits = util.semantic_search(query_embedding, corpus_embeddings)
    search_hits = search_hits[0]  # Get the hits for the first query
    result = []

    for hit in search_hits:

        related_paper = papers[hit['corpus_id']]
        result.append({'title': related_paper['title'], 'abstract': related_paper['abstract'], 'url': related_paper['url'], 'score': hit['score']})

    return jsonify(result), 200

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