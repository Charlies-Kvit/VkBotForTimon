from config import db_session
from data.user import User


def check_admin(event):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == event['from_id']).first()
    db_sess.close()
    if user is None:
        return False
    return user.post >= 1


def check_super_admin(event):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == event['from_id']).first()
    db_sess.close()
    if user is None:
        return False
    return user.post == 2


def get_user_id(data):
    user = data[-1]
    user_id = int(user[3:user.find("|")])
    return user_id
