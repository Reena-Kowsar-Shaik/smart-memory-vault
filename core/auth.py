"""
Authentication & Password Security Engine
Role: Member 1
Handles password hashing (bcrypt), registration validation, and login authentication.
"""

import re
import bcrypt
from core.database import UserRepository, get_db
from core.models import User


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if a plaintext password matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), 
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email format using Regex."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email.strip()))


def register_user(username: str, email: str, password: str) -> dict:
    """
    Register a new user in the system.
    Returns: {"success": True, "user": {...}} or {"success": False, "error": "..."}
    """
    username = username.strip()
    email = email.lower().strip()

    if not username or len(username) < 3:
        return {"success": False, "error": "Username must be at least 3 characters long."}

    if not validate_email(email):
        return {"success": False, "error": "Please enter a valid email address."}

    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters long."}

    # Check if email is already taken
    existing = UserRepository.get_by_email(email)
    if existing:
        return {"success": False, "error": "An account with this email already exists."}

    # Hash and save
    pwd_hash = hash_password(password)
    new_user = UserRepository.create_user(username, email, pwd_hash)

    return {"success": True, "user": new_user}


def login_user(email: str, password: str) -> dict | None:
    """
    Authenticate user credentials.
    Returns serialized user dict if successful, None otherwise.
    """
    email = email.lower().strip()
    with get_db() as session:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            return None

        if verify_password(password, user.password_hash):
            return user.to_dict()

    return None
