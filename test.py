# vulnerable_app.py
# Intentionally vulnerable Python script for security testing

import sqlite3
import os
import pickle

DB = "users.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    conn.commit()
    conn.close()

def register(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # BUG 1: SQL Injection
    query = f"INSERT INTO users VALUES ('{username}', '{password}')"
    c.execute(query)

    conn.commit()
    conn.close()
    print("User registered")

def login(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # BUG 2: SQL Injection again
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = c.execute(query).fetchone()

    conn.close()

    if result:
        print("Login successful")
        return True
    else:
        print("Login failed")
        return False


def run_backup(filename):
    # BUG 3: Command Injection
    os.system("cp " + filename + " backup.db")


def load_session(session_file):
    # BUG 4: Unsafe Deserialization (Remote Code Execution)
    with open(session_file, "rb") as f:
        data = pickle.load(f)
    return data


def debug_mode(user_input):
    # BUG 5: Arbitrary Code Execution
    eval(user_input)


if __name__ == "__main__":
    init_db()

    username = input("Username: ")
    password = input("Password: ")

    register(username, password)

    if login(username, password):
        cmd = input("Enter debug command: ")
        debug_mode(cmd)
