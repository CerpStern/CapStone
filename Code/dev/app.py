import os
import json
import datetime

from flask import Flask, url_for, redirect, \
        render_template, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, \
        logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError

from config import config, Auth

basedir = os.path.abspath(os.path.dirname(__file__))

"""APP creation and configuration"""
app = Flask(__name__)
app.config.from_object(config['dev'])
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

""" DB Models """


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    courses = db.relationship('Course')

class Course(db.Model):
    __tablename__ = "courses"
    dept = db.Column(db.String, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String, primary_key=True)
    syllabus = db.Column(db.Integer, db.ForeignKey('syllabi.id'))
    user = db.Column(db.Integer, db.ForeignKey('users.id'))

class Syllabus(db.Model):
    __tablename__ = "syllabi"
    def __str__(self):
        return '<p id="id">{}</p><p id="basic">{}</p><p id="description">{}</p><p id="topics">{}</p><p id="outcomes">{}</p><p id="grading">{}</p><p id="schedule">{}</p><p id="honesty">{}</p><p id="deadlines">{}</p><p id="accessibility">{}</p><p id="keywords">{}</p>'.format(self.id, self.basic, self.description, self.topics, self.outcomes, self.grading, self.schedule, self.honesty, self.deadlines, self.accessibility, self.keywords)
    id = db.Column(db.Integer, primary_key=True)
    basic = db.Column(db.String)
    description = db.Column(db.String)
    topics = db.Column(db.String)
    outcomes = db.Column(db.String)
    grading = db.Column(db.String)
    schedule = db.Column(db.String)
    honesty = db.Column(db.String)
    deadlines = db.Column(db.String)
    accessibility = db.Column(db.String)
    keywords = db.Column(db.String)
    course = db.relationship('Course')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
""" OAuth Session creation """


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
                Auth.CLIENT_ID,
                state=state,
                redirect_uri=Auth.REDIRECT_URI)
        oauth = OAuth2Session(
                Auth.CLIENT_ID,
                redirect_uri=Auth.REDIRECT_URI,
                scope=Auth.SCOPE)
        return oauth


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)


@app.route('/gCallback')
def callback():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                    Auth.TOKEN_URI,
                    client_secret=Auth.CLIENT_SECRET,
                    authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.name = user_data['name']
            print(token)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/syllabus')
def syllabus():
    try:
        syllabus = db.session.query(Syllabus).filter(Syllabus.id == request.args.get('id'))[0]
    except IndexError:
        syllabus = ""
    editable = db.session.query(User,Course,Syllabus).filter(current_user.get_id() == Course.syllabus).filter(Course.user == User.id).first()
    owns = False if editable == None else True
    return render_template('syllabus.html', syllabus=syllabus, owns=owns)

@app.route('/save', methods = ['POST'])
def save():
    vals = []
    for i in range(1,12): #TODO: Better way of doing this?
        vals.append(request.form.get('test'+str(i))[3:][:-4])
    print(vals)
    #TODO: Sanitize, esp wrt id
    #db.session.query().Syllabus.update().where(Syllabus.id == int(vals[0])).values(basic=vals[1],description=vals[2],topics=vals[3],outcomes=vals[4],grading=vals[5],schedule=vals[6],honesty=vals[7],deadlines=vals[8],accessibility=vals[9],keywords=vals[10])
    syllabus = Syllabus.query.filter_by(id=vals[0]).first()
    syllabus.basic = vals[1] 
    syllabus.description = vals[2]
    syllabus.topics = vals[3]
    syllabus.outcomes = vals[4]
    syllabus.grading = vals[5]
    syllabus.schedule = vals[6]
    syllabus.honesty = vals[7]
    syllabus.deadlines = vals[8]
    syllabus.accessibility = vals[9] 
    syllabus.keywords = vals[10] 
    db.session.commit()
    return redirect(url_for('syllabus') + '?id={}'.format(vals[0]))
