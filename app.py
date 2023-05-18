from flask import Flask, request, jsonify
from flask_cors import CORS
from  flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from uuid import uuid4
import os

app = Flask(__name__)
cors = CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
# db.create_all()
ma = Marshmallow(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(26), unique=False)
    hashed_password = db.Column(db.String(100), unique=True)
    first_name = db.Column(db.String(26), unique=False)
    last_name = db.Column(db.String(26), unique=False)

    def __init__(self, username, hashed_password, first_name, last_name ):
        self.username = username
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        first_name = data["firstName"]
        last_name = data["lastName"]
        username = data["username"]
        password = data["password"]
        user_id = str(uuid4())
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = User(
            username=username, 
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)
        db.session.commit()

        #TODO - SAVE DATA TO SQL BEFORE SENDING RESPONSE
        response = {
            "userId": user_id,
            "firstName": first_name,
            "lastName": last_name,
            "username": username,
            "hashedPassword": hashed_password.decode("utf-8")
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        users = User.query.all()
        for user in users:
            if user["username"] == username:
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), user["hashedPassword"].encode("utf-8"))
                if hashed_password == user.hashed_password.encode("utf-8"):
                    response = {
                        "userId": user.user_id,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "username": username
                    }
                    return jsonify(response)
        return jsonify({"message": "Incorrect username or password"}), 401
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=3001)