import os
import sqlite3
import json
from sqlite3 import Error

from flask import Flask, escape, request, jsonify
import json

from werkzeug.utils import secure_filename

app = Flask(__name__)


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'files')
connection = sqlite3.connect('database.db')
connection.execute('''CREATE TABLE IF NOT EXISTS TESTS
                    (TEST_ID INTEGER PRIMARY KEY  AUTOINCREMENT NOT NULL,
                    SUBJECT      TEXT     ,
                    ANSWER_KEY   TEXT );
                    ''')

connection.execute('''CREATE TABLE IF NOT EXISTS SUBMISSIONS
                        (SCANTRON_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
                        SCANTRON_URL TEXT ,
                        NAME           TEXT ,
                        SUBJECT      TEXT ,
                        SUBMISSION   TEXT,
                        SCORE          INT );''')
connection.close()


@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'


@app.route('/api/tests/', methods=['POST'])
def create_test():
    temp = request.get_json()
    subject = temp["subject"]
    print(subject)
    answer_keys = temp['answers_key']
    answer_keys_str = json.dumps(answer_keys)

    try:
        connection = sqlite3.connect('database.db')
        result = connection.execute("INSERT INTO TESTS (SUBJECT) VALUES (?)", subject)
        connection.executemany("INSERT INTO TESTS (ANSWER_KEY) VALUES (?)", answer_keys_str)
        connection.commit()
        response_body = {"test_id": result.lastrowid, "subject": subject, "answer_keys": answer_keys, "submissions": []}
        return jsonify(response_body), 201 + "Created"

    except Error as error:
        print(error)

    finally:
        if connection:
            connection.close()
    return "Error occurred", 400


@app.route('/api/tests/<test_id>', methods=['GET'])
def get_tests(test_id):
    try:
        connection = sqlite3.connect('database.db')
        test = connection.execute("SELECT * FROM TESTS WHERE TEST_ID = ?", [test_id])
        subject = test.fetchone()[1]
        expected_answers = connection.execute("SELECT ANSWER_KEY FROM TESTS WHERE TEST_ID = ?", [test_id])
        submissions = connection.execute("SELECT * FROM SUBMISSIONS WHERE TEST_ID = ?", [test_id])
        expected_answers = json.loads(expected_answers)
        submission_result = []

        for submission_row in submissions:
            score = 0
            result = {}
            scantron_id = submission_row[0]
            scantron_url = submission_row[1]
            name = submission_row[2]
            submitted_answers = submission_row[4]
            submitted_answers = json.loads(submitted_answers)

            for key in expected_answers:
                result[key] = {"actual": submitted_answers[key],
                               "expected": expected_answers[key]}

            submission_result.append({"scantron_id": scantron_id,
                                      "scantron_url": scantron_url,
                                      "name": name,
                                      "subject": subject,
                                      "score": score,
                                      "result": result})

        response = {"test_id": test_id,
                    "subject": subject,
                    "answer_keys": expected_answers,
                    "submissions": submission_result}
        return jsonify(response), 200

    except Error as error:
        print(error)

    finally:
        if connection:
            connection.close()
    return "Error occurred", 400


@app.route('/api/tests/<test_id>/scantrons/', methods=['POST'])
def upload_scantron(test_id):
    file = request.files['data']
    file.filename = secure_filename(file.filename)
    filepath = "http://localhost:5000/files/" + file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    data = json.load(open((os.path.join(app.config['UPLOAD_FOLDER'], file.filename))))

    try:
        connection = sqlite3.connect('database.db')
        name = data["name"]
        subject = data["subject"]
        answers = data["answers"]
        correct_answers = connection.execute("SELECT ANSWER_KEY FROM TESTS WHERE TEST_ID = ?", [test_id])
        correct_answers = json.loads(correct_answers)
        score = 0
        result = {}

        for key in correct_answers:
            if correct_answers[key] == answers[key]:
                score += 1
            result[key] = {"actual": answers[key],
                           "expected": correct_answers[key]}

        submission_values = [test_id, name, filepath, subject, score]
        submission = connection.execute(
            "INSERT INTO submissions (TEST_ID, NAME, SCANTRON_URL, SUBJECT, SCORE) VALUES (?,?,?,?,?)",
            submission_values)
        result_values = [(submission.lastrowid, question_number, value) for question_number, value in answers.items()]
        connection.executemany("INSERT INTO RESULT VALUES (?, ?, ?)", result_values)
        connection.commit()
        response = {"scantron_id": submission.lastrowid,
                    "scantron_url": filepath,
                    "name": name,
                    "subject": subject,
                    "score": score,
                    "result": result}
        return jsonify(response), 200

    except Error as error:
        print(error)

    finally:
        if connection:
            connection.close()
    return "Error occurred.", 400


if __name__ == '__main__':
    app.run()
