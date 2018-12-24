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


if __name__ == '__main__':
    app.run(host='10.55.200.178', port=5000)