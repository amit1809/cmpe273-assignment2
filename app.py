from flask import Flask, escape, request, jsonify, g
import os
from scan_scantron import scan_jpeg_file, scan_json_file
from handle_db import setup_db, close_connection, commit_db, get_db
import handle_db

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

#location where scantrons will be saved
UPLOAD_LOCATION = os.getcwd()+"/files/"

#initial test and scantron ids
test_id = 1
scantron_id = 1

@app.route('/')
def welcome():
    return "Add test details and scantron"

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

    #Check if answers list is of size 50
    if(len(answer_list) != 50):
        return (f'Please re-check !! 50 Answers required but {len(answer_list)} provided')

    #Check all answers are valid
    if(check_valid_answers(answer_list) == False):
        return (f'Answers are not valid !! Should be from this list: ["A","B","C","D","E"]')

    answer_str = ','.join(answer_list)

    #insert test details in DB
    handle_db.insert_test(test_id, subject_name, answer_str)

    #last_inserted = handle_db.query_test(test_id)
    last_inserted = handle_db.get_dict_output_from_query_test(test_id)
    test_id += 1
    close_connection()
    return jsonify(last_inserted), 201

@app.route('/api/tests/<int:file_id>/scantrons', methods=['POST'])
def upload_scantrons_json(file_id):
    global scantron_id
    FILE_PATH = os.path.join(UPLOAD_LOCATION, str(file_id) + ".json")
    with open(FILE_PATH, "wb") as fp:
        fp.write(request.data)
    file_contents = scan_json_file(FILE_PATH)
    insert_data = handle_scantron(file_contents, FILE_PATH)

    return jsonify(insert_data), 201

@app.route('/api/tests/<int:file_id>/scantrons_jpeg', methods=['POST'])
def upload_scantrons_jpeg(file_id):
    global scantron_id
    FILE_PATH = os.path.join(UPLOAD_LOCATION, str(file_id)+".jpeg")
    with open(FILE_PATH, "wb") as fp:
        fp.write(request.data)
    file_contents = scan_jpeg_file(FILE_PATH)
    print(file_contents)
    return "Scantron uploaded", 201

@app.route('/api/tests/<int:test_id>', methods=['GET'])
def get_test_details(test_id):
    result = handle_db.get_dict_output_from_query_test(test_id)
    scantrons = handle_db.get_dict_query_scantrons_for_test(test_id)
    result["submissions"] = scantrons
    return jsonify(result), 201

def handle_scantron(content, file_path):
    global scantron_id
    #scantron_url = content["scantron_url"]
    scantron_url = "http://localhost:5000/files/"+ file_path[file_path.index("/files/") + len("/files/"):]
    name = content["name"]
    subject_name = content["subject"]
    answers = content["answers"]
    scantron_answers_list = list(answers.values())

    # Check if answers list is of size 50
    if (len(scantron_answers_list) != 50):
        return (f'Please re-check !! 50 Answers required but {len(scantron_answers_list)} provided')

    # Check all answers are valid
    if (check_valid_answers(scantron_answers_list) == False):
        return (f'Answers are not valid !! Should be from this list: "A","B","C","D","E"')

    scantron_answers_str = ','.join(scantron_answers_list)
    cur = get_db().cursor()

    # get test_id and answers key for subject name
    cur.execute("SELECT test_id FROM test_details WHERE subject=?", (subject_name,))

    # If test case details not exist
    if (cur.fetchone() == None):
        return (f'Test cases details for subject: {subject_name} not exist, please provide same first')

    cur.execute("SELECT test_id FROM test_details WHERE subject=?", (subject_name,))
    test_id = str(cur.fetchone()[0])
    cur.execute("SELECT answer_keys FROM test_details WHERE subject=?", (subject_name,))
    answer_key = str(cur.fetchone()[0])

    # get score by comparing answer_key and scantron_answers
    answer_key_list = list(answer_key.split(","))

    # Verify answers and calculate score
    score = get_score(answer_key_list, scantron_answers_list)

    # insert scantron details in DB
    handle_db.insert_scantron(scantron_id, scantron_url, name, subject_name, score, scantron_answers_str, test_id)

    last_inserted = handle_db.get_dict_output_from_query_scantron(scantron_id)
    scantron_id += 1
    close_connection()
    return last_inserted

def get_score(answer_key, scantron_key):
    score = 0
    for i in range(len(answer_key)):
        if(answer_key[i] == scantron_key[i]):
            score += 1
    print(f"Score:{score}")
    return score

def check_valid_answers(answer_list):
    valid_answers = ["A", "B", "C", "D", "E"]
    check = all(item in valid_answers for item in answer_list)
    return check
