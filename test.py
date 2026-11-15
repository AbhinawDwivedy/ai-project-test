"""Vulnerable web application module for security testing and demonstration."""

import os
import pickle
import shutil
import sqlite3
from typing import Any, Optional

DB = "users.db"


def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection.

    Returns:
        sqlite3.Connection: SQLite database connection instance.
    """
    return sqlite3.connect(DB)


def init_db():
    """Initialize the SQLite database and create the users table if it does not exist."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")


def register(username, password):
    """Register a new user in the database.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.
    """
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # BUG 1: SQL Injection
            query = f"INSERT INTO users VALUES ('{username}', '{password}')"
            c.execute(query)

            conn.commit()
            print("User registered")
    except sqlite3.Error as e:
        print(f"Database registration error: {e}")


def login(username, password):
    """Authenticate a user against stored database credentials.

    Args:
        username (str): The username to authenticate.
        password (str): The password to authenticate.

    Returns:
        bool: True if authentication succeeds, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # BUG 2: SQL Injection again
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            result = c.execute(query).fetchone()

            if result:
                print("Login successful")
                return True
            else:
                print("Login failed")
                return False
    except sqlite3.Error as e:
        print(f"Database login error: {e}")
        return False


def run_backup(filename):
    """Create a backup copy of the specified file.

    Args:
        filename (str): Name or path of the file to back up.
    """
    # BUG 3: Command Injection
    try:
        shutil.copy(filename, "backup.db")
    except (IOError, OSError) as e:
        print(f"Backup error: {e}")


def load_session(session_file):
    """Load and deserialize session data from a pickle file.

    Args:
        session_file (str): Path to the serialized session file.

    Returns:
        Any: The deserialized session data object.
    """
    # BUG 4: Unsafe Deserialization (Remote Code Execution)
    try:
        with open(session_file, "rb") as f:
            data = pickle.load(f)
        return data
    except (IOError, OSError, pickle.PickleError) as e:
        print(f"Session error: {e}")
        return None


def debug_mode(user_input):
    """Execute arbitrary Python expression in debug mode.

    Args:
        user_input (str): Python expression string to evaluate.
    """
    # BUG 5: Arbitrary Code Execution
    try:
        eval(user_input)
    except Exception as e:
        print(f"Debug execution error: {e}")


if __name__ == "__main__":
    init_db()

    username = input("Username: ")
    password = input("Password: ")

    register(username, password)

    if login(username, password):
        run_backup(DB)
        load_session("session.pkl")
        cmd = input("Enter debug command: ")
        debug_mode(cmd)
