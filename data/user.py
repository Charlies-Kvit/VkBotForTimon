import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    post = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    user_blocked = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    loyal = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    request_id = orm.relationship('Request', back_populates='user')
