import datetime
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Using SQLite for simplicity
app.config['JWT_SECRET_KEY'] = 'sdjosdosdjdmpwonlknjsblsbk22312wdkljdd'  # Replace with a secure key in production

db = SQLAlchemy(app)
jwt = JWTManager(app)

# User model
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class UserLoginHistory(db.Model):
    user_login_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    date_of_login = db.Column(db.DateTime, nullable=False)
    date_of_logout = db.Column(db.DateTime, nullable=True)
    is_logged_in = db.Column(db.Boolean, nullable=False)



class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)


# Initialize database tables
@app.before_request
def create_tables():
    db.create_all()

from flask import Response

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()

@app.route('/')
@cross_origin()
def index():
    return 'Hello,!'

# User signup route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    if User.query.filter_by(username=data['username'].lower()).first():
        return jsonify({'message': 'Username already exists, please choose a different one'}), 409
    new_user = User(username=data['username'].lower(), email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'].lower()).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    if UserLoginHistory.query.filter_by(user_id=user.user_id, is_logged_in=True).first():
        token = UserLoginHistory.query.filter_by(user_id=user.user_id, is_logged_in=True).order_by(UserLoginHistory.date_of_login.desc()).first().token
        return jsonify({'access_token': token }), 200
    access_token = create_access_token(identity={'user_id': user.user_id})
    new_login = UserLoginHistory(token=access_token, user_id=user.user_id, date_of_login=datetime.datetime.now(), is_logged_in=True)
    db.session.add(new_login)
    db.session.commit()
    return jsonify({'access_token': access_token}), 200

# Add task route
@app.route('/add_task', methods=['POST'])
def add_task():
    # current_user = get_jwt_identity()
    task_data = request.get_json()
    token = task_data['token']
    if not UserLoginHistory.query.filter_by(token=token, is_logged_in=True).first():
        return jsonify({'message': 'Invalid token'}), 401
    user_id = UserLoginHistory.query.filter_by(token=token, is_logged_in=True).order_by(UserLoginHistory.date_of_login.desc()).first().user_id
    # Placeholder logic for adding a task
    task_name = task_data['title']
    task_description = task_data['description']
    new_task = Task(title=task_name, description=task_description, user_id=user_id)
    db.session.add(new_task)
    db.session.commit()
    username = User.query.filter_by(user_id=user_id).first().username.lower()
    return jsonify({'message': f"Task added by {username}"}), 200

@app.route('/view_task', methods=['POST'])
def view_task():
    # current_user = get_jwt_identity()
    token = request.get_json()['token']
    user_id = UserLoginHistory.query.filter_by(token=token, is_logged_in=True).order_by(UserLoginHistory.date_of_login.desc()).first().user_id
    user_tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify({'tasks':  [{'title': task.title, 'description': task.description} for task in user_tasks]}), 200


@app.route('/logout', methods=['POST'])
def logout():
    token = request.get_json()['token']
    user_id = UserLoginHistory.query.filter_by(token=token, is_logged_in=True).order_by(UserLoginHistory.date_of_login.desc()).first().user_id
    UserLoginHistory.query.filter_by(user_id=user_id, is_logged_in=True).update({UserLoginHistory.is_logged_in: False, UserLoginHistory.date_of_logout: datetime.datetime.now()})
    db.session.commit()
    return jsonify({'message': 'User logged out successfully'}) , 200


if __name__ == '__main__':
    app.run(debug=True)



    13.201.29.42