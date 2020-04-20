from flask import Flask, escape, request, jsonify, g
import sqlite3
import os

app = Flask(__name__)

#location where scantrons will be saved
UPLOAD_LOCATION = os.getcwd()

DATABASE = 'database.db'

#initial test and scantron ids
test_id = 0
scantron_id = 0

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        print("DB Connection closed")

@app.route('/')
def index():
    global test_id
    cur = get_db().cursor()
    #Create test table
    cur.execute("CREATE TABLE IF NOT EXISTS test_record(test_id INT primary key, subject TEXT, answer_keys TEXT)")

    '''
    cur.execute("INSERT INTO test_record(test_id, subject, answer_keys) VALUES(:id,:subject,:answer_keys)", test)
    cur.execute("INSERT INTO test_record(test_id, subject, answer_keys) VALUES(:id,:subject,:answer_keys)", test2)
    cur.execute("SELECT * FROM test_record")
    '''
    rows = cur.fetchall();
    print(rows)
    close_connection()
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
    cur.execute("INSERT INTO test_record(test_id, subject, answer_keys) VALUES(?, ?, ?)", (test_id, subject_name, answer_str))
    cur.execute("SELECT * FROM test_record WHERE test_id=?", (test_id,))
    row = cur.fetchall()
    test_id += 1
    close_connection()
    return jsonify(row), 201

@app.route('/api/tests/scantrons', methods=['POST'])
def upload_scantrons():
    with open(os.path.join(UPLOAD_LOCATION, str(scantron_id)+".jpeg"), "wb") as fp:
        fp.write(request.data)
        #scantron_id += 1
    return "Scantron uploaded", 201
