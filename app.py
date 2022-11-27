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
    links1 = ["http://aclweb.org/anthology/D18-1291.pdf", "http://aclweb.org/anthology/D18-1047.pdf", "http://aclweb.org/anthology/D18-1059.pdf"]
    links2 = ["http://aclweb.org/anthology/D18-1344.pdf", "http://aclweb.org/anthology/D16-1071.pdf", "http://aclweb.org/anthology/D18-1482.pdf"]
    return render_template('upload.html', links1 = links1, links2 = links2)

@app.route('/summaryPage',  methods = ['GET'])
def summaryPage():
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
    links = ["http://aclweb.org/anthology/D18-1291.pdf", "http://aclweb.org/anthology/D18-1047.pdf", "http://aclweb.org/anthology/D18-1059.pdf"]
    title = "Mercury"
    content = "Mercury is the smallest and fastest planet in the solar system. It is also the closest planet to the sun. It is named after the Roman messenger god Mercury, the fastest Roman god. The planet Mercury was known by ancient people thousands of years ago."
    return render_template('summary.html', links = links, title = title, content = content)

@app.route('/login', methods = ['GET'])
def login():
    return render_template('upload.html')

@app.route('/getSummary', methods = ['GET'])
def getSummary():
    input = """Mercury The smallest planet in our solar system is Mercury, which is also closest to the Sun. The geological features of Mercury consist of lobed ridges and impact craters. Being closest to the Sun the Mercury’s temperature sores extremely high during the day time. Mercury can go as high as 450 degree Celsius but surprisingly the nights here are freezing cold. Mercury has a diameter of 4,878 km and Mercury does not have any natural satellite like Earth. Venus Venus is also said to be the hottest planet of our solar system. It has a toxic atmosphere that always traps heat. Venus is also the brightest planet and it is visible to the naked eye. Venus has a thick silicate layer around an iron core which is also similar to that of Earth. Astronomers have seen traces of internal geological activity on Venus planet. Venus has a diameter of 12,104 km and it is just like Mars. Venus also does not have any natural satellite like Earth. Earth Earth is the largest inner planet. It is covered two-third with water. Earth is the only planet in our solar system where life is possible. Earth’s atmosphere which is rich in nitrogen and oxygen makes it fit for the survival of various species of flora and fauna. However human activities are negatively impacting its atmosphere. Earth has a diameter of 12,760 km and Earth has one natural satellite that is the moon. Get the huge list of more than 500 Essay Topics and Ideas Mars Mars is the fourth planet from the Sun and it is often referred to as the Red Planet. This planet has a reddish appeal because of the iron oxide present on this planet. Mars planet is a cold planet and it has geological features similar to that of Earth. This is the only reason why it has captured the interest of astronomers like no other planet. This planet has traces of frozen ice caps and it has been found on the planet. Mars has a diameter of 6,787 km and it has two natural satellites. Jupiter It is the largest planet in our solar system. Jupiter has a strong magnetic field. Jupiter largely consists of helium and hydrogen. It has a Great Red Spot and cloud bands. The giant storm is believed to have raged here for hundreds of years. Jupiter has a diameter of 139,822 km and it has as many as 79 natural satellites which are much more than of Earth and Mars. Saturn Saturn is the sixth planet from the Sun. It is also known for its ring system and these rings are made of tiny particles of ice and rock. Saturn’s atmosphere is quite like that of Jupiter because it is also largely composed of hydrogen and helium. Saturn has a diameter of 120,500 km and It has 62 natural satellites that are mainly composed of ice. As compare with Jupiter it has less satellite. Uranus Uranus is the seventh planet from the Sun. It is the lightest of all the giant and outer planets. Presence of Methane in the atmosphere this Uranus planet has a blue tint. Uranus core is colder than the other giant planets and the planet orbits on its side. Uranus has a diameter of 51,120 km and it has 27 natural satellites. Neptune Neptune is the last planet in our solar system. It is also the coldest of all the planets. Neptune is around the same size as the Uranus. And it is much more massive and dense. Neptune’s atmosphere is composed of helium, hydrogen, methane, and ammonia and it experiences extremely strong winds. It is the only planet in our solar system which is found by mathematical prediction. Neptune has a diameter of 49,530 km and it has 14 natural satellites which are more than of Earth and Mars. Conclusion Scientists and astronomers have been studying our solar system for centuries and then after they will findings are quite interesting. Various planets that form a part of our solar system have their own unique geological features and all are different from each other in several ways."""
    return render_template('summary.html', input = input)

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