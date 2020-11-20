from flask import Flask, request, render_template, jsonify
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_cors import CORS
from models import db, Todo
import json

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db.init_app(app)
Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)

CORS(app)


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/todos/user/", methods=['GET'])
@app.route("/todos/user/<username>", methods=['GET', 'PUT', 'POST', 'DELETE'])
def test(username=None):
    if request.method == 'GET':
        if not username:
            users = Todo.query.all()
            users = list(map(lambda user: user.name, users))

            return jsonify(f"lists names: {users}"), 200
        else:
            user = Todo.query.filter_by(name=username).first()

            if not user:
                return jsonify({"msg": "User does not exist"}), 404
            else:
                response = user.task
                return jsonify(json.loads(response)), 200

    if request.method == 'POST':
        body = request.get_json()

        user = Todo.query.filter_by(name=username).first()

        if not user:
            if body != []:
                return jsonify({"msg": "Invalid body format"}), 422
            else:
                user = Todo()
                user.name = username
                user.task = json.dumps([{"label": "example task", "done": False}])

                db.session.add(user)
                db.session.commit()

                return jsonify({"result": "ok"}), 202
        else:
            return jsonify({"msg": "User already exist"}), 422

    if request.method == 'PUT':
        user = Todo.query.filter_by(name=username).first()

        if not user:
            return jsonify({"msg": "User does not exist"}), 404
        else:
            body = request.get_json()

            if type(body) != list:
                return jsonify({"msg": "Invalid body format"}), 422
            else:
                user.name = username
                user.task = json.dumps(body)

                db.session.commit()
                return jsonify({"result": f"A list with {len(body)} todos was succesfully saved"}), 200

    if request.method == 'DELETE':
        user = Todo.query.filter_by(name=username).first()

        if not user:
            return jsonify({"msg": "Contact not found"}), 404
        else:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"result": "ok"}), 200


if __name__ == "__main__":
    manager.run()