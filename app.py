from flask import Flask, escape, request, jsonify, g
import os
from scan_scantron import scan_file
from handle_db import setup_db, close_connection, commit_db, get_db
import json

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

#location where scantrons will be saved
UPLOAD_LOCATION = os.getcwd()

#initial test and scantron ids
test_id = 1
scantron_id = 1

@app.route('/')
def welcome():
    return "Add test and scantron"

@app.before_first_request
def setup():
    setup_db()
    return "Success"

@app.route('/api/tests', methods=['POST'])
def add_test():
    global test_id
    if not request.is_json:
        return "Please pass JSON object for test details"
    content = request.get_json()
    subject_name = content["subject"]
    answers = content["answer_keys"]
    answer_list = list(answers.values())
    answer_str = ','.join(answer_list)

    #insert test details in DB
    cur = get_db().cursor()
    cur.execute("INSERT INTO test_details(test_id, subject, answer_keys) VALUES(?, ?, ?)", (test_id, subject_name, answer_str))
    commit_db()
    cur.execute("SELECT * FROM test_details WHERE test_id=?", (test_id,))
    # get column name along with query result for json format
    r = [dict((cur.description[i][0], value) \
              for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.connection.close()
    test_id += 1
    close_connection()
    print(r)
    return jsonify(r), 201

@app.route('/api/tests/temp/scantrons', methods=['POST'])
def upload_scantrons_details():
    global scantron_id
    if not request.is_json:
        return "Please pass JSON object for test details"
    content = request.get_json()
    scantron_url = content["scantron_url"]
    name = content["name"]
    subject_name = content["subject"]
    answers = content["scanned_answers"]
    scantron_answers_list = list(answers.values())
    scantron_answers_str = ','.join(scantron_answers_list)
    cur = get_db().cursor()

    #get test_id and answers key for subject name
    cur.execute("SELECT test_id FROM test_details WHERE subject=?", (subject_name,))
    test_id = str(cur.fetchone()[0])
    cur.execute("SELECT answer_keys FROM test_details WHERE subject=?", (subject_name,))
    answer_key = str(cur.fetchone()[0])

    #get score by comparing answer_key and scantron_answers
    answer_key_list = list(answer_key.split(","))

    # Verify answers and calculate score
    score = get_score(answer_key_list, scantron_answers_list)

    # insert scantron details in DB
    cur.execute("INSERT INTO scantron_details(scantron_id, scantron_url, name, subject, score, "
                "result, test_id) VALUES(?, ?, ?, ?, ?, ?, ?)", (scantron_id, scantron_url, name, subject_name, score,
                                                                 scantron_answers_str, test_id))
    commit_db()
    cur.execute("SELECT * FROM scantron_details WHERE scantron_id=?", (scantron_id,))

    # get column name along with query result for json format
    r = [dict((cur.description[i][0], value) \
              for i, value in enumerate(row)) for row in cur.fetchall()]

    scantron_id += 1
    close_connection()
    return jsonify(r), 201

@app.route('/api/tests/<int:file_id>/scantrons', methods=['POST'])
def upload_scantrons(file_id):
    global scantron_id
    FILE_PATH = os.path.join(UPLOAD_LOCATION, str(file_id)+".jpeg")
    with open(FILE_PATH, "wb") as fp:
        fp.write(request.data)
    file_contents = scan_file(FILE_PATH)
    print(file_contents)


        #scantron_id += 1
    return "Scantron uploaded", 201

@app.route('/api/tests/<int:test_id>', methods=['GET'])
def get_test_details(test_id):
    cur = get_db().cursor()
    cur.execute("SELECT * FROM test_details WHERE test_id=?", (test_id,))

    # get column name along with query result for json format
    r = [dict((cur.description[i][0], value) \
              for i, value in enumerate(row)) for row in cur.fetchall()]
    print(r)
    return jsonify(r), 201

@app.route('/api/tests/all', methods=['GET'])
def get_all_tests():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM test_details")

    # get column name along with query result for json format
    r = [dict((cur.description[i][0], value) \
              for i, value in enumerate(row)) for row in cur.fetchall()]
    print(r)
    return jsonify(r), 201

@app.route('/api/scantrons/all', methods=['GET'])
def get_all_scantrons():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM scantron_details")

    # get column name along with query result for json format
    r = [dict((cur.description[i][0], value) \
              for i, value in enumerate(row)) for row in cur.fetchall()]
    print(r)
    return jsonify(r), 201

def get_score(answer_key, scantron_key):
    print(answer_key)
    print(scantron_key)
    score = 0
    for i in range(len(answer_key)):
        if(answer_key[i] == scantron_key[i]):
            score += 1
    print(f"Score:{score}")
    return score
