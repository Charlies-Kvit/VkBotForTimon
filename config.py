from api_key import token
from data import db_session

db_session.global_init('db/db.sqlite')
token = token
posts = ['пользователь', 'агент', 'администратор']
