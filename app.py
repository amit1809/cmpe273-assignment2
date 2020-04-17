from flask import Flask, escape, request, jsonify, g
import sqlite3


app = Flask(__name__)

tests = []
test = []
test_id = 1
'''
@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'
'''

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    test = {
        "id": "1",
        "subject": "History",
        "answer_keys": {
        "1": "A",
        "2": "B",
        "3": "C",
        "..": "..",
        "49": "D",
        "50": "E"
    }
    }

    test2 = {
        "id": "2",
        "subject": "English",
        "answer_keys": {
        "1": "A",
        "2": "B",
        "3": "C",
        "..": "..",
        "49": "D",
        "50": "E"
    }
    }
    global test_id
    cur = get_db().cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS test_record(test_id INT, subject TEXT, answer_keys BLOB)")
    cur.execute("INSERT INTO test_record(test_id, subject, answer_keys) VALUES(:id,:subject,:answer_keys)", test)
    cur.execute("INSERT INTO test_record(test_id, subject, answer_keys) VALUES(:id,:subject,:answer_keys)", test2)
    cur.execute("SELECT * FROM test_record")
    #cur.execute("INSERT INTO test_record(test_id, subject, answer_keys) VALUES(1,'A','B')")
   # cur.execute("INSERT INTO cars VALUES(2,'Math','XYZ')")
    rows = cur.fetchall();
    print(rows)
    return "Success"

@app.route('/api/tests', methods=['POST'])
def add_test():
    global test_id
    if not request.is_json:
        return "Please pass JSON object"
    content = request.get_json()
    last_student_id += 1
    students.append({'id': last_student_id, 'name': content["name"]})
    return jsonify(students)
