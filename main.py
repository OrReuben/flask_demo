from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:oriz125467@localhost/todo-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    userid = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'content': self.content,
            'completed': self.completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'userid': self.userid
        }


@app.get('/')
def get_all_todos():
    todos = db.session.query(Todo).all()
    todo_list = [todo.serialize() for todo in todos]
    return jsonify(todo_list), 200


@app.patch('/update-todo')
def update_todo_status():
    try:
        todo_id = request.json.get('id')
        todo = Todo.query.get(todo_id)

        if todo is None:
            return jsonify({'message': 'No todo was found!'}), 404

        todo.completed = not todo.completed
        todo.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Todo has been successfully changed!', 'todo': todo.serialize()}), 200

    except Exception as err:
        error_message = err.args[0] if err.args else 'An error occurred'
        return jsonify({'message': error_message}), 500


@app.post('/add-todo')
def add_todo():
    try:
        content = request.json.get('content')
        user_id = request.json.get('user_id')

        if not content or not user_id:
            return jsonify({'message': 'No content were provided!'}), 404

        todo = Todo(content=content, userid=user_id)
        db.session.add(todo)
        db.session.commit()

        return jsonify({'message': 'Todo has been successfully added', 'todo': todo.serialize()}), 200

    except Exception as err:
        error_message = err.args[0] if err.args else 'An error occurred'
        return jsonify({'message': error_message}), 500


@app.delete('/remove-todo')
def delete_todo():
    try:
        todo_id = request.json.get('id')

        if todo_id is None:
            return jsonify({'message': 'No todo id was found'}), 404

        deleted_todo = Todo.query.get(todo_id)
        db.session.delete(deleted_todo)
        db.session.commit()

        return jsonify({'message': 'Todo was successfully deleted!', 'todo': deleted_todo.serialize()})

    except Exception as err:
        error_message = err.args[0] if err.args else 'An error occurred'
        return jsonify({'message': error_message}), 500


@app.get('/user-todos')
def get_user_todos():
    try:
        user_id = request.json.get('user_id')

        if user_id is None:
            return jsonify({'message': 'Must provide a valid user id'}), 404

        todos = Todo.query.filter(Todo.userid == user_id).all()
        todo_list = [todo.serialize() for todo in todos]

        return jsonify({'message': 'Successfully fetched all todos for the user!', 'todos': todo_list}), 200

    except Exception as err:
        error_message = err.args[0] if err.args else 'An error occurred'
        return jsonify({'message': error_message}), 500


if __name__ == '__main__':
    app.run(debug=True)