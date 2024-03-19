from flask import Flask,send_from_directory,request,jsonify,send_file,render_template,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,LoginManager,login_required,current_user
from flask_login import login_user,logout_user
from hashlib import sha256
import os
import json
from hashlib import sha256
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy()
db.init_app(app)
 

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    code = db.Column(db.String(1000))

class Post(db.Model):
    inhalt = db.Column(db.String, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    vote = db.Column(db.Integer)
    id=db.Column(db.Integer, primary_key=True)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect("/")

@app.route('/signup')
def signup():
    return send_from_directory("ui",'reg.html')
    
@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    code = request.form.get('code')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
    
    name=name.replace(" ","")
    
    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('signup'))

    valid_code=sha256(email.encode('utf-8')).hexdigest()
    print(email, name, password, code)

    #if valid_code == code:
    if name == "ma":
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='scrypt:32768:8:1'),code=code)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    #else:
        #flash('Invalid signup code!')
        #return redirect(url_for('signup'))

@app.route('/post',methods=["POST"])
@login_required
def post():
    
    inhalt = request.form.get('inhalt')
    name=current_user.name
    id=random.randrange(0,9999999999999)

    post=Post(inhalt=inhalt,username=name,vote=0,id=id)

    db.session.add(post)
    db.session.commit()

    return jsonify({"message: ":"Post added successfully"}),201

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signup'))

@app.route('/profile',methods=["GET"])
@login_required
def profile():
    return send_from_directory("ui","profile.html")

@app.route('/profile',methods=["POST"])
@login_required
def profile_post():
    return jsonify({"name":current_user.name,"email":current_user.email,"password":current_user.password,"code":current_user.code}),201


@app.route('/',methods=["GET"])
@login_required
def home():
    return send_from_directory("ui","home.html")

@app.route('/test',methods=["GET"])
@login_required
def test():
    return send_from_directory("ui","reg.html")

app.run(debug=True)