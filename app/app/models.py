# models.py
# ==============================
# USER DATA SYSTEM (CORE)
# ==============================

users = {}

def create_user(email):
    if email not in users:
        users[email] = {
            "email": email,
            "resume_count": 0,
            "is_premium": False
        }

def get_user(email):
    return users.get(email)

def increment_resume(email):
    if email in users:
        users[email]["resume_count"] += 1

def make_premium(email):
    if email in users:
        users[email]["is_premium"] = True
