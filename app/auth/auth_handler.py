from ..persistence.models import User
from ..persistence import db


def register(user_json):
    email = user_json["email"]
    username = user_json["username"]
    password = user_json["password"]

    user = User(email=email, username=username, password=password)

    db.session.add(user)
    db.session.commit()

    return user