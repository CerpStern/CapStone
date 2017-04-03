import os
import json
import datetime

from flask import Flask, url_for, redirect, \
        render_template, session, request, jsonify
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
    admin = db.Column(db.Boolean, default=False)
    courses = db.relationship('Course')

class Course(db.Model):
    __tablename__ = "courses"
    def __str__(self):
        return '{} {} {} {} {}'.format(self.dept, self.id, self.section, self.semester, self.year)
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
        return '<div id="id">{}</div><div id="basic">{}</div><div id="description">{}</div><div id="topics">{}</div><div id="outcomes">{}</div><div id="grading">{}</div><div id="schedule">{}</div><div id="honesty">{}</div><div id="deadlines">{}</div><div id="accessibility">{}</div><div id="keywords">{}</div>'.format(self.id, self.basic, self.description, self.topics, self.outcomes, self.grading, self.schedule, self.honesty, self.deadlines, self.accessibility, self.keywords)
        #return '<p id="id">{}</p><p id="basic">{}</p><p id="description">{}</p><p id="topics">{}</p><p id="outcomes">{}</p><p id="grading">{}</p><p id="schedule">{}</p><p id="honesty">{}</p><p id="deadlines">{}</p><p id="accessibility">{}</p><p id="keywords">{}</p>'.format(self.id, self.basic, self.description, self.topics, self.outcomes, self.grading, self.schedule, self.honesty, self.deadlines, self.accessibility, self.keywords)
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


def is_admin():
    id = current_user.get_id()
    return User.query.filter_by(id=id).first().admin

def get_courses():
    user = current_user.get_id()
    matches = Course.query.filter_by(user=user)
    num = Course.query.filter_by(user=user).count()
    return matches, num

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
    adm = is_admin()
    courses, num = get_courses()
    return render_template('index.html', adm=adm, courses=courses, num=num)


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
        google = get_google_auth(state=session.get('oauth_state'))
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
    editable = db.session.query(User,Course).filter(Course.syllabus == request.args.get('id')).filter(current_user.get_id() == Course.user).count()
    print("{} {}".format(current_user.get_id(),editable))
    owns = False if editable == 0 else True
    return render_template('syllabus.html', syllabus=syllabus, owns=owns)

@app.route('/save', methods = ['POST'])
def save():
    vals = []
    for i in range(1,12): #TODO: Better way of doing this?
        if request.form.get('test'+str(i))[:3] == '<p>': # Holy shit nesting <p>s breaks everything, remove them
            vals.append(request.form.get('test'+str(i))[3:][:-4])
        else:
            vals.append(request.form.get('test'+str(i)))
    #TODO: Sanitize, esp wrt id
    #db.session.query().Syllabus.update().where(Syllabus.id == int(vals[0])).values(basic=vals[1],description=vals[2],topics=vals[3],outcomes=vals[4],grading=vals[5],schedule=vals[6],honesty=vals[7],deadlines=vals[8],accessibility=vals[9],keywords=vals[10])
    syllabus = Syllabus.query.filter_by(id=vals[0]).first()
    #syllabus = Syllabus.query.filter_by(id=vals[0][3:][:-4]).first()
    syllabus.basic = vals[1] 
    syllabus.description = vals[2]
    syllabus.topics = vals[3]
    syllabus.outcomes = vals[4]
    syllabus.grading = vals[5]
    syllabus.schedule = vals[6]
    syllabus.honesty = vals[7]
    syllabus.deadlines = vals[8]
    syllabus.accessibility =  vals[9] 
    syllabus.keywords = vals[10] 
    db.session.commit()
    return redirect(url_for('syllabus') + '?id={}'.format(vals[0]))
    #return redirect(url_for('syllabus') + '?id={}'.format(vals[0][3:][:-4]))

@app.route('/add', methods = ['POST'])
def add():
    year = int(request.form.get('year'))
    semester = request.form.get('semester')
    department = request.form.get('department')
    cid = int(request.form.get('cid'))
    section = int(request.form.get('section'))
    instructor = request.form.get('instructor')

    iid = User.query.filter_by(email=instructor).first()
    if iid == None: # Need to add instructor
        newinst = User(email=instructor)
        db.session.add(newinst)
        db.session.commit()
        iid = User.query.filter_by(email=instructor).first()

    try:
        new_course = Course(year=year, semester=semester, dept=department, id=cid, section=section, user=iid.id, syllabus=None)
        db.session.add(new_course)
        db.session.commit()
        new_syllabus = Syllabus()
        db.session.add(new_syllabus)
        new_course.syllabus = new_syllabus.id
        db.session.commit()
    except:
        db.session.rollback()

    return redirect(url_for('index'))


# if a search is done, and the autocomplete is not used / navigated to
# this will open another page with search results, and the ability to refine the results

@app.route('/search',methods = ['GET','POST'])
def search():
    inward_bits = request.values.get('in')
    print(inward_bits)
    #inward_bits=int(inward_bits)
    #syllabus = db.session.query(Syllabus).filter(Syllabus.id == inward_bits)

    return redirect(url_for('syllabus') + '?id=inward_bits')

# this will return packaged data with autocompleted searches.
@app.route('/search_results',methods=['GET'])
def search_results():
    # can I do that? 
    return jsonify(db.session.query(Course)[1].syllabus)
