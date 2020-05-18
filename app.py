from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import and_, or_
from flask_socketio import SocketIO, emit
import json

from models import *

print(datetime.datetime.now())

DATABASE_URL = "postgres://postgres:vighnesh@localhost:5432/chat"

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Set up socket
socketio = SocketIO(app)


def get_servername(server_id):
    return Server.query.filter_by(id=server_id).with_entities(Server.name).first()[0]


def get_username(user_id):
    return User.query.filter_by(id=user_id).with_entities(User.username).first()[0]


def login_required(func):
    def check_logged_in():
        if(session["user"] == None):
            return render_template("error.html", message="Unauthorized Entry")
        func()
    return check_logged_in


def get_server_channels(server_id):
    channels = Channel.query.filter_by(server_id=server_id).all()
    return channels


def get_user_friends(user_id):
    dms = DirectMessage.query.filter_by(sender_user_id=user_id).with_entities(DirectMessage.receiver_user_id).union(
        DirectMessage.query.filter_by(receiver_user_id=user_id).with_entities(DirectMessage.sender_user_id)).distinct().all()
    friends = []
    for tupl in dms:
        for number in tupl:
            new_dict = {}
            new_dict["id"] = number
            new_dict["username"] = get_username(number)
            friends.append(new_dict)
    return friends


"""def get_messages_with_friends(user_1, user_2):
    messages_with_user = DirectMessage.query.filter(or_(and_(DirectMessage.receiver_user_id == user_2, DirectMessage.sender_user_id == user_1), and_(
        DirectMessage.receiver_user_id == user_1, DirectMessage.sender_user_id == user_2))).order_by(desc(DirectMessage.pub_date)).all()
    # Cleaning Text so it can be read by Javascript
    # List of messages
    messages = []
    for message in messages_with_user:
        new_message = {}
        new_message["sender"] = get_username(message.sender_user_id)[0][0]
        new_message["receiver"] = get_username(message.receiver_user_id)[0][0]
        new_message["pub_date"] = message.pub_date.strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        new_message["content"] = message.message_content

        messages.append(new_message)
    return messages
"""


def get_user_servers(user_id):
    member_servers = Member.query.filter_by(
        member_user_id=user_id).with_entities(Member.server_id).all()
    print(member_servers)
    servers = []
    for tupl in member_servers:
        for number in tupl:
            servers.append(Server.query.filter_by(id=number).first())
    return servers


"""
def get_channel_messages(channel_id):
    channel_messages = ChannelMessage.query.filter_by(
        channel_id=channel_id).order_by(desc(ChannelMessage.pub_date)).all()
    # Cleaning Text so it can be read by Javascript
    # List of messages
    messages = []
    for message in channel_messages:
        new_message = {}
        new_message["sender"] = get_username(message.sender_user_id)[0][0]
        new_message["pub_date"] = message.pub_date.strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        new_message["content"] = message.message_content

        messages.append(new_message)
    return messages"""


@app.route("/")
def index():
    if(session.get("user") == None):
        return render_template("index.html")
    else:
        return redirect(url_for("dashboard"))


@app.route("/login")
def login():
    if(session.get("error_message") != None):
        message = session["error_message"]
        del session["error_message"]
        return render_template("login.html", message=message)
    return render_template("login.html", message="")


@app.route("/signup")
def signup():
    if(session.get("error_message") != None):
        message = session["error_message"]
        del session["error_message"]
        return render_template("signup.html", message=message)
    return render_template("signup.html", message="")


@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    if(request.method == "POST"):
        if("login_submit" in request.form):
            email = request.form.get("user_email")
            password = request.form.get("user_password")
            user = User.query.filter_by(email=email).first()
            print(user)
            if(user != None and user.verify_password(password)):
                session["user"] = user
                friends = get_user_friends(session["user"].id)
                servers = get_user_servers(session["user"].id)
                return render_template("dashboard.html", friends=friends, servers=servers, user=session["user"])

            else:
                session["error_message"] = "Incorrect Username or Password"
                return redirect(url_for("login"))

        else:
            username = request.form.get("user_name")
            email = request.form.get("user_email")
            password = request.form.get("user_password")
            # Check if user with username is already present
            print(email)
            # print(User.query.filter_by(email=email).first())
            if(User.query.filter_by(email=email).first() != None):
                session["error_message"] = "A user with that email already exist, please choose another one"
                return redirect(url_for("signup"))
            user = User(username=username, password=password, email=email)
            db.session.add(user)
            db.session.commit()
            session["user"] = user
            # Get Users Friends and Servers
            friends = get_user_friends(session["user"].id)
            servers = get_user_servers(session["user"].id)
            return render_template("dashboard.html", friends=friends, servers=servers, user=session["user"])
    else:
        if(session.get("user") != None):
            friends = get_user_friends(session["user"].id)
            servers = get_user_servers(session["user"].id)
            print(friends, servers)
            return render_template("dashboard.html", friends=friends, servers=servers, user=session["user"])
        return render_template("error.html", message="Please Log In or Sign Up First!")


@app.route("/logout")
def logout():
    del session["user"]
    return redirect(url_for('index'))


@app.route("/createserver")
def create_server():
    return render_template("createserver.html", user = session["user"])


@app.route("/joinserver")
def join_server():
    return render_template("joinserver.html",  user = session["user"])


@app.route("/addfriend")
def add_friend():
    return render_template("addfriend.html", user = session["user"])

@app.route("/addnewfriend", methods = ["POST"])
def add_new_friend():
    user_id = int(request.form.get("user_id").strip())
    friends = get_user_friends(session["user"].id)
    servers = get_user_servers(session["user"].id)
    if(User.query.filter_by(id = user_id).first() == None):
        return render_template("error.html", message = "No User with that User Id Exists")
    if(user_id == session["user"].id):
        return render_template("error.html", message = "Invalid User ID")
    existing_friends = get_user_friends(session["user"].id)
    flag = 0
    print(existing_friends)
    for friend in existing_friends:
        print(friend["id"])
        print(user_id)
        print(friend["id"] == user_id)
        if(friend["id"] == user_id):
            print("TRUE")
            flag = 1
            break
    if(flag == 0):
        new_friend = {}
        new_friend["id"] = user_id
        new_friend["username"] = get_username(user_id)
        friends.append(new_friend)
    return render_template("dashboard.html", friends = friends, servers = servers, user = session["user"])


@app.route("/createnewserver", methods = ["POST"])
def create_new_server():
    server_name = request.form.get("server_name")
    server = Server(name=server_name, owner = session["user"].id)
    db.session.add(server)
    db.session.commit()
    channel = Channel(server_id=server.id)
    member = Member(member_user_id=session["user"].id, server_id = server.id)
    db.session.add(channel)
    db.session.add(member)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route("/joinnewserver", methods=["POST"])
def join_new_server():
    server_id = int(request.form.get("server_id").strip())
    if(Member.query.filter(and_(Member.server_id == server_id, Member.member_user_id == session["user"].id)).first() != None):
        return render_template("error.html", message="You are already in that server!")
    if(Server.query.filter_by(id = server_id).first() == None):
        return render_template("error.html", message = "No Server with that server id exists!")
    member = Member(member_user_id=session["user"].id, server_id = server_id)
    db.session.add(member)
    db.session.commit()
    return redirect(url_for('dashboard'))



@app.route("/get_messages_with_friends", methods=["POST"])
def get_messages_with_friends():
    user_1 = request.form.get("user_1")
    user_2 = request.form.get("user_2")
    messages_with_user = DirectMessage.query.filter(or_(and_(DirectMessage.receiver_user_id == user_2, DirectMessage.sender_user_id == user_1), and_(
        DirectMessage.receiver_user_id == user_1, DirectMessage.sender_user_id == user_2))).order_by(DirectMessage.pub_date).all()
    # Cleaning Text so it can be read by Javascript
    # List of messages
    messages = []
    for message in messages_with_user:
        new_message = {}
        new_message["sender"] = get_username(message.sender_user_id)
        new_message["receiver"] = get_username(message.receiver_user_id)
        new_message["pub_date"] = message.pub_date.strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        new_message["content"] = message.message_content

        messages.append(new_message)
    print(messages)
    return json.dumps(messages)


@app.route("/get_channel_messages", methods=["POST"])
def get_channel_messages():
    channel_id = request.form.get("channel_id")
    channel_messages = ChannelMessage.query.filter_by(
        channel_id=channel_id).order_by(ChannelMessage.pub_date).all()
    # Cleaning Text so it can be read by Javascript
    # List of messages
    messages = []
    for message in channel_messages:
        new_message = {}
        new_message["sender"] = get_username(message.sender_user_id)
        new_message["pub_date"] = message.pub_date.strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        new_message["content"] = message.message_content

        messages.append(new_message)
    print(messages)
    return json.dumps(messages)

@app.route("/deleteserver/<int:id>")
def delete_server(id):
    server_channels = get_server_channels(id)
    for channel in server_channels:
        ChannelMessage.query.filter_by(channel_id = channel.id).delete
    Channel.query.filter_by(server_id = id).delete()
    Member.query.filter_by(server_id = id).delete()
    Server.query.filter_by(id = id).delete()
    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/deletechannel", methods = ["POST"])
def delete_channel():
    channel_id = int(request.form.get("channel_id").strip())
    server_id = int(request.form.get("submit").strip())
    ChannelMessage.query.filter_by(channel_id = channel_id).delete()
    db.session.commit()
    Channel.query.filter_by(id = channel_id).delete()
    db.session.commit()
    return redirect(url_for("server_dashboard", server_id = server_id))

@app.route("/serverdashboard/<int:server_id>")
def server_dashboard(server_id):
    server = Server.query.filter_by(id = server_id).first()
    return render_template("server_dashboard.html", server=server, channels=get_server_channels(server_id), user=session["user"])


@app.route("/showmessages/<int:user_id_1>/<int:user_id_2>")
def get_messages(user_id_1, user_id_2):
    return render_template("showmessages.html", messages=get_messages_with_friends(user_id_1, user_id_2))


@app.route('/createnewchannel', methods=["POST"])
def create_new_channel():
    channel_name = request.form.get("new_channel")
    server_id = int(request.form.get("submit").strip())
    new_channel = Channel(name = channel_name, server_id = server_id)
    db.session.add(new_channel)
    db.session.commit()
    # print("########################",channel_name, server_id)
    return redirect(url_for("server_dashboard", server_id = server_id))


@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))


@socketio.on('new message')
def new_message(data):
    message = {}
    message["content"] = data["message"]
    message["sender"] = get_username(data["sender"])
    message["receiver"] = get_username(int(data["receiver"]))
    namespace = f"/{data['namespace']}"
    user_message = DirectMessage(sender_user_id = data["sender"], receiver_user_id = int(data["receiver"]), pub_date = datetime.datetime.now(), message_content = data["message"])
    db.session.add(user_message)
    db.session.commit()
    # print(namespace)
    emit('add message', message, broadcast=True, namespace=namespace)

@socketio.on('new channel message')
def new_channel_message(data):
    message = {}
    message["content"] = data["message"]
    message["sender"] = get_username(data["sender"])
    # message["receiver"] =
    print(data)
    namespace = f"/{data['namespace']}"
    channel_id = int(data["channel_id"])
    channel_message = ChannelMessage(sender_user_id = data["sender"], channel_id = channel_id, pub_date = datetime.datetime.now(), message_content = data["message"])
    db.session.add(channel_message)
    db.session.commit()
    emit('add message', message, broadcast=True, namespace = namespace)


def main():
    db.create_all()
    print(get_user_friends(1))
    users = User.query.all()
    for user in users:
        print(user)
    print(get_user_servers(1))
    print(get_server_channels(1))
    print(Server.query.filter_by(id=1).first().id)


if __name__ == "__main__":
    #app.run(debug = True)
    with app.app_context():
        main()
