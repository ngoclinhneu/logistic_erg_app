# auth.py
import hashlib
import sqlite3
from database import get_connection

def check_login(username, password):
    try:
        conn = get_connection(); c = conn.cursor()
        input_hash = hashlib.sha256(str.encode(password)).hexdigest()
        c.execute('SELECT role, full_name FROM users WHERE username=? AND password_hash=?', (username, input_hash))
        user = c.fetchone(); conn.close()
        return user if user else None
    except: return None

def create_user_sql(username, password, role, fullname):
    try:
        conn = get_connection(); c = conn.cursor()
        hashed_pw = hashlib.sha256(str.encode(password)).hexdigest()
        c.execute("INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)", (username, hashed_pw, role, fullname))
        conn.commit(); conn.close()
        return True, "User created successfully!"
    except sqlite3.IntegrityError: return False, "Username already exists!"
    except Exception as e: return False, str(e)

def change_password_sql(username, new_pass):
    conn = get_connection(); c = conn.cursor()
    hashed_pw = hashlib.sha256(str.encode(new_pass)).hexdigest()
    c.execute("UPDATE users SET password_hash=? WHERE username=?", (hashed_pw, username))
    conn.commit(); conn.close()