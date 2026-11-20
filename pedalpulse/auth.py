"""Small JSON-backed account store using salted SHA-256 password hashes."""
import hashlib
import json
import os
import secrets

USERS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")


def _load_users():
    if not os.path.exists(USERS_PATH):
        _save_users({})
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as file:
            users = json.load(file)
    except (ValueError, OSError):
        users = {}
    if "demo" not in users:
        users["demo"] = _password_entry("demo123")
        _save_users(users)
    return users


def _save_users(users):
    with open(USERS_PATH, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=2)


def _password_entry(password):
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return {"salt": salt, "hash": digest}


def login_user(username, password):
    if not username.strip() or not password:
        return False, "Enter both your username and password."
    entry = _load_users().get(username.strip())
    if not entry:
        return False, "Incorrect username or password."
    actual = hashlib.sha256((entry["salt"] + password).encode("utf-8")).hexdigest()
    if not secrets.compare_digest(actual, entry["hash"]):
        return False, "Incorrect username or password."
    return True, "Welcome back!"


def signup_user(username, password):
    username = username.strip()
    if not username or not password:
        return False, "Enter a username and password."
    if len(username) > 40:
        return False, "Usernames must be 40 characters or fewer."
    if len(password) < 6:
        return False, "Use a password with at least 6 characters."
    users = _load_users()
    if username in users:
        return False, "That username is already taken."
    users[username] = _password_entry(password)
    _save_users(users)
    return True, "Account created. You can log in now."
