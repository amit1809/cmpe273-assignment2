from flask import Flask, escape, request, jsonify, g
import sqlite3

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection():
    get_db().close()
    print("DB Connection closed")

def commit_db():
    get_db().commit()
    print("DB Commited")

def setup_db():
    cur = get_db().cursor()

    # Dropping existing tables before application starts
    cur.execute("DROP TABLE IF EXISTS scantron_details")
    cur.execute("DROP TABLE IF EXISTS test_details")
    commit_db()

    #Create test table
    cur.execute("CREATE TABLE IF NOT EXISTS test_details(test_id INT primary key, subject TEXT, answer_keys TEXT)")

    #Create scantron table
    cur.execute("CREATE TABLE IF NOT EXISTS scantron_details(scantron_id INT primary key, scantron_url TEXT, "
                "name TEXT, subject TEXT, score INT, result TEXT, test_id INT not null, "
                "foreign key(test_id) references test_details(test_id))")
    commit_db()
    #close_connection()
    return "Success"

# get column name along with query result for json format
def get_json_object_from_query(db_cur):
    r = [dict((db_cur.description[i][0], value) \
              for i, value in enumerate(row)) for row in db_cur.fetchall()]
    return r
def query_scantron(key_value):
    cur = get_db().cursor()
    if(key_value == None):
        cur.execute("SELECT * FROM scantron_details")
    else:
        cur.execute("SELECT * FROM scantron_details WHERE scantron_id=?", (key_value,))

    return get_json_object_from_query(cur)

def query_test(key_value):
    cur = get_db().cursor()
    if(key_value == None):
        cur.execute("SELECT * FROM test_details")
    else:
        cur.execute("SELECT * FROM test_details WHERE test_id=?", (key_value,))

    return get_json_object_from_query(cur)

def insert_scantron(scantron_id, scantron_url, name, subject_name, score,scantron_answers_str, test_id):
    cur = get_db().cursor()
    cur.execute("INSERT INTO scantron_details(scantron_id, scantron_url, name, subject, score, "
                "result, test_id) VALUES(?, ?, ?, ?, ?, ?, ?)", (scantron_id, scantron_url, name, subject_name, score,
                                                                 scantron_answers_str, test_id))
    commit_db()

def insert_test(test_id, subject_name, answer_str):
    cur = get_db().cursor()
    cur.execute("INSERT INTO test_details(test_id, subject, answer_keys) VALUES(?, ?, ?)",
                (test_id, subject_name, answer_str))
    commit_db()

def query_scantrons_for_test(test_id):
    cur = get_db().cursor()
    cur.execute("SELECT * FROM scantron_details WHERE test_id=?", (test_id,))
    return get_json_object_from_query(cur)

def get_dict_query_scantrons_for_test(test_id):
    iterator = 1
    cur = get_db().cursor()
    output_dict={}
    cur.execute("SELECT scantron_id FROM scantron_details WHERE test_id=?", (test_id,))
    row = cur.fetchall()
    for val in row:
        output_dict[iterator] = get_dict_output_from_query_scantron(val[0])
        iterator+=1
    return output_dict

def get_dict_output_from_query_test(key_value):
    cur = get_db().cursor()
    cur.execute("SELECT * FROM test_details WHERE test_id=?", (key_value,))
    row  = cur.fetchall()
    out_dict={}
    answer_dict={}
    ans_list=[]
    scantron_list=[]
    for val in row:
        out_dict["test_id"] = val[0]
        out_dict["subject"] = val[1]
        ans_list = list(val[2].split(","))
    for i in range(len(ans_list)):
        answer_dict[i+1] = ans_list[i]
    out_dict["answer_keys"] = answer_dict
    out_dict["submissions"] = scantron_list
    return out_dict

def get_dict_output_from_query_scantron(key_value):
    cur = get_db().cursor()
    cur.execute("SELECT * FROM scantron_details WHERE scantron_id=?", (key_value,))
    row = cur.fetchall()
    out_dict = {}
    answer_dict = {}
    ans_list = []
    ans_compare = {}
    for val in row:
        out_dict["scantron_id"] = val[0]
        out_dict["scantron_url"] = val[1]
        out_dict["name"] = val[2]
        out_dict["subject_name"] = val[3]
        out_dict["score"] = val[4]
        ans_list = list(val[5].split(","))

    #get test details for answer keys
    cur.execute("SELECT answer_keys FROM test_details WHERE subject=?", (out_dict["subject_name"],))
    answer_key = str(cur.fetchone()[0])
    ans_key_list = list(answer_key.split(","))
    for i in range(len(ans_list)):
        ans_compare = {}
        ans_compare["actual"] = ans_list[i]
        ans_compare["expected"] = ans_key_list[i]
        answer_dict[i + 1] = ans_compare
    out_dict["result"] = answer_dict
    return out_dict
