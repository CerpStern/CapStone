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

from app import app
from app import db
from app import login_manager
from app.models import *

queuefile = 'queue.json'

basedir = os.path.abspath(os.path.dirname(__file__))

"""APP creation and configuration"""
#db = SQLAlchemy(app)
#login_manager = LoginManager(app)
#login_manager.login_view = "login"
#login_manager.session_protection = "strong"

from utils import *

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
    semester, year, department, section, search_text = "","","","",""
    if request.values.get('department') != "":
        department = request.values.get('department').upper()
    print(department)
    return redirect(url_for('index'))

@app.route('/adv_search',methods = ['GET'])
def adv_search():
    departments = []
    for i in Syllabus.query.filter(Syllabus.official_id != None):
        departments.append(Course.query.filter_by(syllabus=i.id).first().dept)
    # unique post query
    depts = list(set(departments))
    auth_url = get_oauth_url()
    return render_template('advanced.html',auth_url=auth_url, depts=depts)

# Custom 404 handler
# Dude sick custom mod bro.
@app.errorhandler(404)
def err404(err):
    return render_template('404.html'), 404

@app.errorhandler(500)
def err500(err):
    return render_template('500.html'), 500