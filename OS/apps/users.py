import os
import json

USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading users:", e)
        return {}

def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
        return True
    except Exception as e:
        print("Error saving users:", e)
        return False

def has_users():
    users = load_users()
    return len(users) > 0
