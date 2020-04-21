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
