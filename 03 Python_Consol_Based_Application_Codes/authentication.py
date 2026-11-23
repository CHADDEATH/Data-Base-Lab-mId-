"""
Pak Voyage - Authentication & User Security Module
Handles Tourist registration, secure SHA-256 password hashing, validation, and session login.
"""

import hashlib
import re
from database import execute_query, execute_non_query, execute_insert_returning_id

SALT = "PakVoyage_2026_SecureSalt_"

def hash_password(password):
    """Generates a secure SHA-256 hash with salt."""
    salted = SALT + password
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def is_valid_email(email):
    """Validates email format using regex."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def register_tourist(full_name, username, age_str, country, email, password, confirm_password):
    """
    Validates and registers a new tourist user into Oracle Database.
    Returns (success_bool, message, user_id).
    """
    # 1. Check required fields
    if not all([full_name, username, age_str, country, email, password, confirm_password]):
        return False, "All registration fields are required.", None

    full_name = full_name.strip()
    username = username.strip()
    country = country.strip()
    email = email.strip().lower()

    # 2. Validate passwords match
    if password != confirm_password:
        return False, "Password and confirmation password do not match.", None

    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    # 3. Validate age
    try:
        age = int(age_str)
        if age < 12 or age > 120:
            return False, "Age must be between 12 and 120 years.", None
    except ValueError:
        return False, "Age must be a valid integer number.", None

    # 4. Validate email
    if not is_valid_email(email):
        return False, "Invalid email address format.", None

    # 5. Check username uniqueness in Oracle
    check_user_sql = "SELECT USER_ID FROM USERS WHERE LOWER(USERNAME) = LOWER(:u)"
    existing_user = execute_query(check_user_sql, {"u": username})
    if existing_user:
        return False, f"Username '{username}' is already taken. Please choose another.", None

    # 6. Check email uniqueness in Oracle
    check_email_sql = "SELECT USER_ID FROM USERS WHERE LOWER(EMAIL) = LOWER(:e)"
    existing_email = execute_query(check_email_sql, {"e": email})
    if existing_email:
        return False, f"Email address '{email}' is already registered.", None

    # 7. Hash password securely
    pwd_hash = hash_password(password)

    # 8. Insert into USERS table
    insert_sql = """
        INSERT INTO USERS (FULL_NAME, USERNAME, AGE, COUNTRY, EMAIL, PASSWORD_HASH, CREATED_AT, STATUS)
        VALUES (:name, :uname, :age, :country, :email, :pwd, SYSDATE, 'ACTIVE')
        RETURNING USER_ID INTO :out_id
    """
    params = {
        "name": full_name,
        "uname": username,
        "age": age,
        "country": country,
        "email": email,
        "pwd": pwd_hash
    }
    new_id, err = execute_insert_returning_id(insert_sql, params)
    if err:
        return False, f"Database error during registration: {err}", None

    return True, f"Welcome to Pak Voyage, {full_name}! Account created successfully.", new_id

def authenticate_tourist(username, password):
    """
    Authenticates a tourist against Oracle Database.
    Returns (success_bool, message, user_dict).
    """
    if not username or not password:
        return False, "Username and password are required.", None

    username = username.strip()
    pwd_hash = hash_password(password)

    sql = """
        SELECT USER_ID, FULL_NAME, USERNAME, AGE, COUNTRY, EMAIL, CREATED_AT, STATUS
        FROM USERS
        WHERE LOWER(USERNAME) = LOWER(:u) AND PASSWORD_HASH = :p
    """
    users = execute_query(sql, {"u": username, "p": pwd_hash})
    if not users:
        return False, "Invalid username or password.", None

    user = users[0]
    if user.get("status") != "ACTIVE":
        return False, "This account has been deactivated. Please contact administrator.", None

    return True, f"Sign in successful! Welcome back, {user['full_name']}.", user

def ensure_initial_admin():
    """
    Ensures the default administrator account 'bilal' / 'ROMAN' exists in ADMIN_USERS table.
    """
    from config import DEFAULT_ADMIN
    uname = DEFAULT_ADMIN["username"]
    pwd = DEFAULT_ADMIN["password"]
    pwd_hash = hash_password(pwd)

    sql = "SELECT ADMIN_ID FROM ADMIN_USERS WHERE LOWER(USERNAME) = LOWER(:u)"
    existing = execute_query(sql, {"u": uname})
    if not existing:
        ins_sql = """
            INSERT INTO ADMIN_USERS (USERNAME, PASSWORD_HASH, FULL_NAME, EMAIL, ROLE, CREATED_AT)
            VALUES (:u, :p, :name, :email, 'ADMINISTRATOR', SYSDATE)
        """
        execute_non_query(ins_sql, {
            "u": uname,
            "p": pwd_hash,
            "name": "Bilal (System Administrator)",
            "email": "admin@pakvoyage.gov.pk"
        })

def authenticate_admin(username, password):
    """
    Authenticates system administrator against Oracle Database.
    """
    if not username or not password:
        return False, "Admin credentials required.", None

    ensure_initial_admin()
    username = username.strip()
    pwd_hash = hash_password(password)

    sql = """
        SELECT ADMIN_ID, USERNAME, FULL_NAME, EMAIL, ROLE, CREATED_AT
        FROM ADMIN_USERS
        WHERE LOWER(USERNAME) = LOWER(:u) AND PASSWORD_HASH = :p
    """
    admins = execute_query(sql, {"u": username, "p": pwd_hash})
    if not admins:
        return False, "Invalid administrator credentials.", None

    return True, f"Administrator verified. Welcome, {admins[0]['full_name']}.", admins[0]

def change_admin_password(admin_id, old_password, new_password, confirm_new_password):
    """Allows administrator to change their initial password."""
    if new_password != confirm_new_password:
        return False, "New passwords do not match."
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    old_hash = hash_password(old_password)
    check_sql = "SELECT ADMIN_ID FROM ADMIN_USERS WHERE ADMIN_ID = :aid AND PASSWORD_HASH = :old_p"
    if not execute_query(check_sql, {"aid": admin_id, "old_p": old_hash}):
        return False, "Incorrect current password."

    new_hash = hash_password(new_password)
    upd_sql = "UPDATE ADMIN_USERS SET PASSWORD_HASH = :new_p WHERE ADMIN_ID = :aid"
    ok, _, err = execute_non_query(upd_sql, {"new_p": new_hash, "aid": admin_id})
    if ok:
        return True, "Administrator password successfully updated."
    return False, f"Failed to update password: {err}"
