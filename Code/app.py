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

queuefile = 'queue.json'

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
    basic = db.Column(db.String, default='<h1>Intro to Blah Blah Blah</h1><p>Meeting Time: XX:XX - XX:XX Day1, Day2</p><p>Meeting Place: Room XXX Foo Hall</p><p>Course Website:</p><p>Intructor Name: Bob Loblaw</p><p>Office Hours: XX:XX - XX:XXX Day1, Day2 Room XXX Building</p><p>Required Materials if any:</p><p>Prerequisites if any:</p>')
    description = db.Column(db.String)
    topics = db.Column(db.String)
    outcomes = db.Column(db.String)
    grading = db.Column(db.String)
    schedule = db.Column(db.String)
    honesty = db.Column(db.String, default='Cheating means to misrepresent the source, nature, or other conditions of your academic work (e.g., tests, papers, projects, assignments) so as to get underserved credit. The use of the intellectual property of others without giving them appropriate credit is a serious academic offense. The University considers cheating and plagiarism very serious offenses and provides for sanctions up to and including dismissal from the University or revocation of a degree. The University&rsquo;s administrative policy and procedures regarding student cheating and plagiarism can be found in the <a href="https://www.kent.edu/policyreg/administrative-policy-regarding-student-cheating-and-plagiarism" target="_blank" rel="noopener noreferrer">Administrative Policy, 3-01.8</a>. By submitting any material in this (or any other class) you are certifying that it is free of plagiarism.')
    deadlines = db.Column(db.String, default='Students have responsibility to ensure they are properly enrolled in classes. You are advised to review your official class schedule (using Student Tools in FlashLine) during the first two weeks of the semester to ensure you are properly enrolled in this class and section. Should you find an error in your class schedule, you have until cut-off date provided by the Undergraduate Office to correct the error with your advising office. If registration errors are not corrected by the cut-off date and you continue to attend and participate in classes for which you are not officially enrolled, you are advised now that you will not receive a grade at the conclusion of the semester for any class in which you are not properly registered.')
    accessibility = db.Column(db.String, default='University policy 3342-3-01.3 requires that students with disabilities be provided reasonable accommodations to ensure their equal access to course content. If you have a documented disability and require accommodations, please contact the instructor at the beginning of the semester to make arrangements for necessary classroom adjustments. Please note, you must first verify your eligibility for these through the Student Accessibility Services (contact 330-672-3391 or visit <a href="http://www.kent.edu/sas" target="_blank" rel="noopener noreferrer">www.kent.edu/sas</a> for more information on registration procedures).')
    keywords = db.Column(db.String)
    official_id = db.Column(db.Integer, db.ForeignKey('official.id'), default=None)
    official = db.relationship('Official', back_populates='syllabi')
    course = db.relationship('Course')


class Official(db.Model):
    __tablename__ = "official"
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
    honesty = db.Column(db.String, default='Cheating means to misrepresent the source, nature, or other conditions of your academic work (e.g., tests, papers, projects, assignments) so as to get underserved credit. The use of the intellectual property of others without giving them appropriate credit is a serious academic offense. The University considers cheating and plagiarism very serious offenses and provides for sanctions up to and including dismissal from the University or revocation of a degree. The University&rsquo;s administrative policy and procedures regarding student cheating and plagiarism can be found in the <a href="https://www.kent.edu/policyreg/administrative-policy-regarding-student-cheating-and-plagiarism" target="_blank" rel="noopener noreferrer">Administrative Policy, 3-01.8</a>. By submitting any material in this (or any other class) you are certifying that it is free of plagiarism.')
    deadlines = db.Column(db.String, default='Students have responsibility to ensure they are properly enrolled in classes. You are advised to review your official class schedule (using Student Tools in FlashLine) during the first two weeks of the semester to ensure you are properly enrolled in this class and section. Should you find an error in your class schedule, you have until cut-off date provided by the Undergraduate Office to correct the error with your advising office. If registration errors are not corrected by the cut-off date and you continue to attend and participate in classes for which you are not officially enrolled, you are advised now that you will not receive a grade at the conclusion of the semester for any class in which you are not properly registered.')
    accessibility = db.Column(db.String, default='University policy 3342-3-01.3 requires that students with disabilities be provided reasonable accommodations to ensure their equal access to course content. If you have a documented disability and require accommodations, please contact the instructor at the beginning of the semester to make arrangements for necessary classroom adjustments. Please note, you must first verify your eligibility for these through the Student Accessibility Services (contact 330-672-3391 or visit <a href="http://www.kent.edu/sas" target="_blank" rel="noopener noreferrer">www.kent.edu/sas</a> for more information on registration procedures).')
    keywords = db.Column(db.String)
    visible = db.Column(db.Boolean, default=True)
    syllabi = db.relationship('Syllabus', back_populates='official', uselist=False)


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

def update_matches(temp_matches,matches):
    temp = []
    if(len(matches)==0):
        for match in temp_matches:
            temp.append(match.syllabus)
        matches=temp
    else:
        for match in temp_matches:
            if match.syllabus in matches:
                temp.append(match.syllabus)
        matches=temp
    return matches

def get_oauth_url():
    google = get_google_auth()
    auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return auth_url


@app.route('/')
@login_required
def index():
    adm = is_admin()
    courses, num = get_courses()
    with open(queuefile, 'r') as qf:
        queue = set(json.load(qf))
    return render_template('index.html', adm=adm, courses=courses, num=num, pending=queue)


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    auth_url = get_oauth_url()
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
        return render_template('404.html'), 404
    editable = db.session.query(User,Course).filter(Course.syllabus == request.args.get('id')).filter(current_user.get_id() == Course.user).count()
    print("{} {}".format(current_user.get_id(),editable))
    owns = False if editable == 0 else True
    auth_url = get_oauth_url()
    return render_template('syllabus.html', id=syllabus.id, syllabus=syllabus, owns=owns, auth_url=auth_url)

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

@app.route('/remove', methods = ['POST'])
def remove():
    year = int(request.form.get('year'))
    semester = request.form.get('semester')
    department = request.form.get('department')
    cid = int(request.form.get('cid'))
    section = int(request.form.get('section'))

    crse = Course.query.filter_by(year=year, semester=semester, dept=department, id=cid, section=section).first()
    if crse is None:
        return jsonify(status=2)
    try:
        syllid = Syllabus.query.filter_by(id=crse.syllabus).first().official_id
        off = Official.query.filter_by(id=syllid).first()
        if off.visible is False:
            return jsonify(status=2)
        Syllabus.query.filter_by(id=crse.syllabus).first().official_id = None
        off.visible = False
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify(status=2)
    return jsonify(status=1)

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
        db.session.commit()
        new_course.syllabus = new_syllabus.id
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify(status=2) # Arbitrarily choose 2 as fail state

    return jsonify(status=1) # And 1 for success

##
#  Approval queue manipulation
#
@app.route('/queue')
def queue():
    if request.args.get('action') == 'approve' and is_admin(): 
        id = request.args.get('id')
        with open(queuefile, 'r') as qf:
            q = set(json.load(qf))
        # If the syllabus hasn't been approved yet, we add it, else we update the existing one
        adding = True if Syllabus.query.filter_by(id=id).first().official_id == None else False
        tmp = Syllabus.query.filter_by(id=id).first()
        try:
            if adding:
                new = Official()
            else:
                new = Official.query.filter_by(id=tmp.official_id).first()
            new.basic = tmp.basic
            new.description = tmp.description
            new.topics = tmp.topics
            new.outcomes = tmp.outcomes
            new.grading = tmp.grading
            new.schedule = tmp.schedule
            new.honesty = tmp.honesty
            new.deadlines = tmp.deadlines
            new.accessibility = tmp.accessibility
            new.keywords = tmp.keywords
            if adding:
                db.session.add(new)
            db.session.commit()
            tmp.official_id = new.id
            db.session.commit()
            with open(queuefile, 'w') as qf:
                q.remove(request.args.get("id"))
                json.dump(list(q), qf)
        except:
            db.session.rollback()
    # Remove the syllabus from the approval queue
    elif request.args.get('action') == 'deny' and is_admin():
        with open(queuefile, 'r') as qf:
            q = set(json.load(qf))
        with open(queuefile, 'w') as qf:
            q.remove(request.args.get('id'))
            json.dump(list(q), qf)
    # Add to the queue
    elif request.args.get('action') == 'add':
        with open(queuefile, 'r') as qf:
            q = set(json.load(qf))
        with open(queuefile, 'w') as qf:
            q.add(request.args.get('id'))
            json.dump(list(q), qf)
    return redirect(url_for('index'))



###  Search

# Things we need to pull
# year, section, course, search_text, department, semester

# Do a query in the appropriate table for each part of the form data.
# Say that there are 3 courses in our db atm.
# #1: 10001 section 1
# #2: 10001 section 2
# #3: 20001 section 1.
# Say you search for course #10001, and section 1.
# for '10001' syll 1 and 2 will get a point.
# for for '1' syll 1 and 3 will get a point.
# End totals:
#    1: 2, 2: 1, 3: 1
# To break the tie we can just sort by syllabus #

@app.route('/search',methods = ['GET','POST'])
def search():
    return redirect(url_for('index'))

@app.route('/adv_search',methods = ['GET'])
def adv_search():
    #.department.query.filter_by()first().admin
    auth_url = get_oauth_url()
    return render_template('advanced.html',auth_url=auth_url)

# Custom 404 handler
# Dude sick custom mod bro. 
@app.errorhandler(404)
def err404(err):
    return render_template('404.html'), 404
