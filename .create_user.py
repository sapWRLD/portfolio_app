from app import app, db, User
from werkzeug.security import generate_password_hash

username = "TomKerstens"
password = "1579l9L6"

with app.app_context():
    new_user = User(
        user_name=username,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()
    print(f"User '{username}' created successfully!")
