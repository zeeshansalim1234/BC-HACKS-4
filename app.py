from firebase_admin import credentials, initialize_app, firestore
from flask import Flask, Blueprint, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import pickle
import json
import torch
from sentence_transformers import SentenceTransformer, util
from google.cloud import language_v1 

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("key.json")
initialize_app(cred)
db = firestore.client()
#user_Ref = db.collection('research')  

input = """For morphologically rich languages STEM and LAMB, perform significantly better than standard embeddings on word similarity and polarity evaluations. On a new WordNet-based evaluation, STEM and
LAMB are up to 50% better than standard embeddings. """
links = ["http://aclweb.org/anthology/D18-1291.pdf", "http://aclweb.org/anthology/D18-1047.pdf", "http://aclweb.org/anthology/D18-1059.pdf"]
set_answers = [" embeddings, i.e., (low-dimensional) word representations in vector space, have serious practical problems. First, large text corpora are necessary to train high-quality embeddings. Such corpora are not available for underresourced languages. Second, morphologically rich languages (MRLs) are a challenge for standard embedding models because many inflectional forms are rare or absent even in a large corpus.", "WordNet-based evaluation, STEM and LAMB are up to 50% better than standard embeddings."]
set_questions = ["Why should I use LAMB?", "How good is STEM and LAMB in contrast to standard embeddings?"]
question_answer = []
counter = -1

title = "corpus"
content = "A corpus is a collection of authentic text or audio organized into datasets. Authentic here means text written or audio spoken by a native of the language or dialect."
title2 = "lemmatization"
content2 = "Lemmatization is the grouping together of different forms of the same word. In search queries, lemmatization allows end users to query any version of a base word and get relevant results."


@app.route('/', methods = ['GET'])
def home():
    return render_template('index.html')

@app.route('/signUpPage',  methods = ['GET'])
def signUpPage():
    return render_template('account.html')

@app.route('/uploadPage',  methods = ['GET'])
def upload():
    return render_template('upload.html')

@app.route('/searchPapers',  methods = ['GET'])
def searchPapers():
    links1 = ["http://aclweb.org/anthology/D18-1291.pdf", "http://aclweb.org/anthology/D16-1071.pdf", "http://aclweb.org/anthology/D18-1059.pdf"]
    links2 = ["http://aclweb.org/anthology/D18-1344.pdf", "http://aclweb.org/anthology/D16-1047.pdf", "http://aclweb.org/anthology/D18-1482.pdf"]
    return render_template('upload.html', links1 = links1, links2 = links2)

@app.route('/summaryPage',  methods = ['GET'])
def summaryPage():
    global counter
    counter = -1
    return render_template('summary.html')

@app.route('/paperResults',  methods = ['GET'])
def paperResults():
    links = ["http://aclweb.org/anthology/D18-1291.pdf", "http://aclweb.org/anthology/D18-1047.pdf", "http://aclweb.org/anthology/D18-1059.pdf"]
    return render_template('summary.html', links = links)

@app.route('/dashboardPage',  methods = ['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/definition1',  methods = ['GET'])
def definition1():
    # links = ["http://aclweb.org/anthology/D18-1291.pdf", "http://aclweb.org/anthology/D18-1047.pdf", "http://aclweb.org/anthology/D18-1059.pdf"]
    return render_template('summary.html',title=title, content = content)

@app.route('/definition2',  methods = ['GET'])
def definition2():
    # links = ["http://aclweb.org/anthology/D18-1291.pdf", "http://aclweb.org/anthology/D18-1047.pdf", "http://aclweb.org/anthology/D18-1059.pdf"]
    
    return render_template('summary.html',title=title, content = content,title2=title2, content2 = content2)

@app.route('/login', methods = ['GET'])
def login():
    global counter
    counter = -1
    return render_template('upload.html')

@app.route('/question', methods = ['GET'])
def question():
    global counter
    counter+=1
    question_answer.append((set_questions[counter],set_answers[counter]))
    return render_template('summary.html', question_answers = question_answer, summary = input, links = links, title=title, content = content,title2=title2, content2 = content2)

@app.route('/getSummary', methods = ['GET'])
def getSummary():
    
    return render_template('summary.html', summary = input, links = links, title=title, content = content,title2=title2, content2 = content2)

@app.route('/tags', methods = ['POST'])
def tags():

    text_content = request.json['content']

    client = language_v1.LanguageServiceClient()

    # text_content = 'California is a state.'

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    content_categories_version = (
        language_v1.ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2)
    response = client.classify_text(request = {
        "document": document,
        "classification_model_options": {
            "v2_model": {
                "content_categories_version": content_categories_version
            }
        }
    })

    category = ""
    for elem in response.categories:
        category+=elem.name

    category = category.replace('/Other', '')
    categories = category.split("/")

    for elem in categories:
        if len(elem) < 1:
            categories.remove(elem)

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entities(request = {'document': document, 'encoding_type': encoding_type})

    result = []

    # Loop through entitites returned from the API
    for entity in response.entities:
        
        for mention in entity.mentions:

            if language_v1.Entity.Type(entity.type_).name != "OTHER" and language_v1.Entity.Type(entity.type_).name != "NUMBER":       
                result.append(mention.text.content)

    result = list(set(result))
    categories = list(set(categories))
    return jsonify({'tags':result, 'categories':categories}), 200


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