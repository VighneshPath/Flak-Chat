from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user_account"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"{self.id}\nUsername {self.username}\nemail {self.email}\npassword hash {self.password_hash}"


class Server(db.Model):
    __tablename__ = "server"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    owner = db.Column(db.Integer, db.ForeignKey(
        "user_account.id", ondelete='CASCADE'))

    def __repr__(self):
        return f"Server Id: {self.id}\nServer Name: {self.name}"


class Channel(db.Model):
    __tablename__ = "channel"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), default="General")
    server_id = db.Column(db.Integer, db.ForeignKey(
        "server.id", ondelete='CASCADE'))

    def __repr__(self):
        return f"Channel Id: {self.id}\nChannel Name: {self.name}\nServer Id: {self.server_id}"


class Member(db.Model):
    __tablename__ = "member"
    id = db.Column(db.Integer, primary_key=True)
    member_user_id = db.Column(db.Integer, db.ForeignKey(
        "user_account.id", ondelete='CASCADE'))
    server_id = db.Column(db.Integer, db.ForeignKey(
        "server.id", ondelete='CASCADE'))

    def __repr__(self):
        return "{} Belongs to Server {}".format(member_user_id, server_id)


class DirectMessage(db.Model):
    __tablename__ = "direct_message"
    message_id = db.Column(db.Integer, primary_key=True)
    sender_user_id = db.Column(db.Integer, db.ForeignKey(
        "user_account.id", ondelete='CASCADE'), nullable=False)
    receiver_user_id = db.Column(
        db.Integer, db.ForeignKey("user_account.id", ondelete='CASCADE'), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False,
                         default=datetime.datetime.utcnow)
    message_content = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "Sender: {}\nReceiver: {}\nContent: {}\nDate: {}".format(self.sender_user_id, self.receiver_user_id, self.message_content, self.pub_date)


class ChannelMessage(db.Model):
    __tablename__ = "channel_message"
    message_id = db.Column(db.Integer, primary_key=True)
    sender_user_id = db.Column(
        db.Integer, db.ForeignKey("user_account.id", ondelete='CASCADE'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey(
        "channel.id", ondelete='CASCADE'), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False,
                         default=datetime.datetime.utcnow)
    message_content = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "Sender: {}\nReceiver: {}\nContent: {}\nDate: {}".format(self.sender_user_id, self.channel_id, self.message_content, self.pub_date)
