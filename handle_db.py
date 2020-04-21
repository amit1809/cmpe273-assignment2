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
    global test_id
    cur = get_db().cursor()

    # Dropping existing tables before application starts
    cur.execute("DROP TABLE IF EXISTS scantron_details")
    cur.execute("DROP TABLE IF EXISTS test_details")
    commit_db()

    #Create test table
    cur.execute("CREATE TABLE IF NOT EXISTS test_details(test_id INT primary key, subject TEXT, answer_keys TEXT)")

    #Create scantron table
    cur.execute("CREATE TABLE IF NOT EXISTS scantron_details(scantron_id INT primary key, scantron_url TEXT, "
                "name TEXT, subject TEXT, answer_keys TEXT, score INT, result TEXT, test_id INT not null, "
                "foreign key(test_id) references test_details(test_id))")
    commit_db()
    #close_connection()
    return "Success"