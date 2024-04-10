import time
from datetime import datetime, timezone, timedelta
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, String

db = SQLAlchemy()


def get_current_time(time_delta=8):
    """
    Get the current time adjusted by the specified time delta.
    :param time_delta: int, the number of hours to adjust the current time by (default is 8)
    :return: datetime, the current time adjusted by the time delta
    """
    return datetime.now(tz=timezone(timedelta(hours=time_delta)))


def current_millis():
    """
    A function that returns the current time in milliseconds.
    """
    return int(round(time.time() * 1000))


class Role(db.Model):
    """
    Role table
    """
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
        }


class User(db.Model):
    """
    User table
    """
    __tablename__ = "user"
    id = db.Column(String(36),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()),
                   unique=True,
                   nullable=False)
    username = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref='users')
    pw_hash = db.Column(db.String(1000), nullable=False)
    experiments = db.Column(db.BigInteger, nullable=True)
    created_at = db.Column(DateTime(timezone=True), default=get_current_time())
    updated_at = db.Column(DateTime(timezone=True), default=get_current_time())

    def __init__(self, password, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role_id': self.role_id,
            'role': self.role.name if self.role else None,
            'experiments': self.experiments,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Token(db.Model):
    id = db.Column(String(36),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(64),
                         index=True,
                         unique=True,
                         nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=True)
    refresh_token = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(DateTime(timezone=True), default=get_current_time())
    updated_at = db.Column(DateTime(timezone=True), default=get_current_time())

    def __repr__(self):
        return f'<RefreshToken {self.username}>'
