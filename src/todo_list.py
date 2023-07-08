from flask import Flask, request, jsonify, current_app
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    add_date = db.Column(db.DateTime, default=datetime.datetime.now())
    end_date = db.Column(db.DateTime)
    done = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='tasks', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, content, user):
        self.content = content
        self.user = user
    
    def __repr__(self):
        return '<Task %r>' % self.content

@auth.get_password
def def_pw(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return user.password
    else:
        return None

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    user = User(username=username, password=password, email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'response': 'User ' + username + 'created successfuly'
    })

@app.route('/add_task', methods=['POST'])
@auth.login_required
def add_task():
    content = request.form['content']
    task = Task(content=content, user=User.query.filter_by(username=auth.username()).first())
    db.session.add(task)
    db.session.commit()
    return jsonify({
        'username': auth.username(),
        'task-id': task.id,
        'content': task.content
    })

@app.route('/remove_task', methods=['POST'])
@auth.login_required
def remove_task():
    task_id = request.form['task_id']
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({
            'status' : 'Failed'
        })
    deleted_task = jsonify({
        'status' : 'success',
        'task_id' : task.id,
        'content' : task.content,
        'task_compĺeted' : task.done
    })
    db.session.delete(task)
    db.session.commit()
    return deleted_task

@app.route('/mark_task_as_done', methods=['POST'])
@auth.login_required
def mask_task_as_done():
    task_id = request.form['task_id']
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({
            'status' : 'Failed'
        })
    task.done = True
    task.end_date = datetime.datetime.now()
    db.session.commit()
    return jsonify({
        'content': task.content,
        'add_date': task.add_date,
        'end_date': task.end_date,
        'task_completed': task.done
    })

@app.route('/show_tasks', methods=['GET'])
@auth.login_required
def list_all_task():
    user = User.query.filter_by(username=auth.username()).first()
    print(user)
    if user is None:
        return jsonify({
            'status' : 'failded'
        })
    task_list = {}
    for task in user.tasks:
        task_list[task.id] = {
            'content' : task.content,
            'add_date' : task.add_date,
            'task_completed' : task.done
        }
    return jsonify(task_list)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()

'''
/signup
curl -d "username=rafavg77&password=password&email=rafavg77@gmail.com" -X POST http://127.0.0.1:5000/signup

/add_task
curl -u rafavg77:rubiki77 -d "content=Sacar a los pingos" -X POST http://127.0.0.1:5000/add_task
curl -u rafavg77:rubiki77 -d "content=Tomar Pastillas" -X POST http://127.0.0.1:5000/add_task
curl -u rafavg77:rubiki77 -d "content=Dar un beso a Rubi" -X POST http://127.0.0.1:5000/add_task

/show_tasks
curl -u rafavg77:rubiki77 -X GET http://127.0.0.1:5000/show_tasks | jq

/mark_task_as_done
curl -u rafavg77:rubiki77 -d "task_id=1" -X POST http://127.0.0.1:5000/mark_task_as_done

/remove_task
curl -u rafavg77:rubiki77 -d "task_id=4" -X POST http://127.0.0.1:5000/remove_task
'''