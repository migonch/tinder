from app import app, db
from app.models import User, Like, Dislike, Message


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Like': Like,
        'Dislike': Dislike,
        'Message': Message
    }
