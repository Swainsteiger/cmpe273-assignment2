from flask import Flask, escape, request, jsonify
import json

aapp = Flask(__name__)


stud = {
}




'''
{"subject":"Math", "answer_key":{"1":"A","2":"A","3":"C","4":"D","5":"C","6":"D","7":"A","8":"C","9":"C","10":"B","11":"A","12":"D","13":"D","14":"C","15":"D","16":"B","17":"C","18":"D","19":"A","20":"A","21":"A","22":"A","23":"C","24":"D","25":"D","26":"D","27":"A","28":"C","29":"C","30":"B","31":"A","32":"D","33":"D","34":"C","35":"C","36":"B","37":"D","38":"D","39":"A","40":"B","41":"D","42":"B","43":"C","44":"D","45":"A","46":"A","47":"B","48":"A","49":"C","50":"D"}}

{"subject":"Distributed Systems", "answer_key":{"1":"B","2":"A","3":"C","4":"D","5":"C","6":"D","7":"A","8":"D","9":"C","10":"D","11":"A","12":"C","13":"B","14":"C","15":"D","16":"D","17":"C","18":"D","19":"A","20":"A","21":"B","22":"A","23":"C","24":"D","25":"D","26":"D","27":"A","28":"C","29":"C","30":"B","31":"A","32":"A","33":"D","34":"C","35":"C","36":"B","37":"D","38":"D","39":"A","40":"B","41":"D","42":"B","43":"C","44":"A","45":"A","46":"A","47":"C","48":"B","49":"C","50":"C"}}

{"subject":"Software Design", "answer_key":{"1":"D","2":"A","3":"B","4":"A","5":"B","6":"D","7":"A","8":"D","9":"C","10":"B","11":"A","12":"C","13":"C","14":"C","15":"A","16":"D","17":"A","18":"D","19":"C","20":"A","21":"C","22":"A","23":"C","24":"D","25":"D","26":"D","27":"A","28":"C","29":"C","30":"C","31":"A","32":"A","33":"B","34":"C","35":"C","36":"C","37":"D","38":"A","39":"A","40":"B","41":"D","42":"A","43":"C","44":"D","45":"A","46":"A","47":"D","48":"B","49":"C","50":"C"}}
'''




tests = {} #[{"subject":"Math","answer_key":{"1":"A","..":"..","50":"B"}}, etc...]
test_ids = []
sid = 0
tid = 0


@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'




@app.route('/api/tests/', methods=['POST'])
def create_test():
    global tid
    req = request.json
    print(req)
    temp = {
        "test_id":str(tid),
        "subject":req["subject"],
        "answer_key":req["answer_key"],
        "submissions":[]
    }
    tests[req["subject"]] = temp
    tid += 1
    test_ids.append(temp)
    return temp, 201


@app.route('/api/tests/<id>', methods=['GET'])
def get_tests(id=0):
    return test_ids[int(id)], 201


@app.route('/api/tests/<id>/scantrons/', methods=['POST'])
def upload_scantron(id=0):
    global sid
    req = request.json
    temp = {
        "name":req["name"],
        "scantron_id":str(sid),
        "subject":req["subject"],
        "score":"",
        "result":""
    }
    graded = grade_scantron(req["answers"], test_ids[int(id)]["answer_key"])
    temp["score"] = str(graded[0])
    temp["result"] = graded[1]
    test_ids[int(id)]["submissions"].append(temp)
    return temp, 201


def grade_scantron(answers, key):
    graded = {}
    score = 0
    for question, answer in answers.items():
        temp = {
            "actual":answer,
            "expected":key[question]
        }
        graded[question] = temp
        if (answer == key[question]):
            score += 1
    return [score, graded]
