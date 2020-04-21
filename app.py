from flask import Flask, escape, request, jsonify, g
import sqlite3
import os
from scan_scantron import scan_file
from handle_db import setup_db, close_connection, commit_db, get_db

app = Flask(__name__)

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
    #students.append({'id': last_student_id, 'name': content["name"]})
    subject_name = content["subject"]
    answers = content["answer_keys"]
    answer_list = list(answers.values())
    answer_str = ','.join(answer_list)
    #insert test details in DB
    cur = get_db().cursor()
    cur.execute("INSERT INTO test_details(test_id, subject, answer_keys) VALUES(?, ?, ?)", (test_id, subject_name, answer_str))
    commit_db()
    cur.execute("SELECT * FROM test_details WHERE test_id=?", (test_id,))
    row = cur.fetchall()
    test_id += 1
    close_connection()
    return jsonify(row), 201

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
    row = cur.fetchall()
    print(row)
    return jsonify(row), 201

@app.route('/api/tests/all', methods=['GET'])
def get_all_tests():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM test_details")
    row = cur.fetchall()
    print(row)
    return jsonify(row), 201