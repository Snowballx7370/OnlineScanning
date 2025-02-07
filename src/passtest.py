import bcrypt

def hash_password(password: str) -> str:
    """Hash a password."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    print(hashed_password.decode())
    return hashed_password.decode()

if __name__ == "__main__":
    stored_password_hash = hash_password("admin")

