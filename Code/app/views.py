from __future__ import print_function
import os
import sys
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


from app.utils import *

##
#  Index
#
@app.route('/')
@login_required
def index():
    adm = is_admin()
    courses, num = get_courses()

    # FAVORITES
    # well all this got dirty quick
    pairs = []
    favs = None
    has_favs = False
    fav_count = 0
    if current_user.get_id() is not None:
        favs = Favorites.query.filter_by(user=current_user.get_id())
        for item in favs:
            if Syllabus.query.filter_by(official_id=item.official_id).first() is not None:
                tmp_syll = Syllabus.query.filter_by(official_id=item.official_id).first().id
                q = Course.query.filter_by(syllabus=tmp_syll).first()
                atuple = (item,q)
                pairs.append(atuple)
                fav_count=fav_count+1

    if fav_count > 0:
        has_favs = True

    # DEPARTMENTS THING
    departments = []
    for i in Syllabus.query.filter(Syllabus.official_id != None):
        temp = Course.query.filter_by(syllabus=i.id).first().dept
        if temp not in departments:
            departments.append(temp)

    # QUEUE
    with open(queuefile, 'r') as qf:
        queue = set(json.load(qf))
    return render_template('index.html', adm=adm, courses=courses, num=num, pending=queue, favs=pairs,has_favs=has_favs,depts=departments)

##
#  Login Page
#
@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    auth_url = get_oauth_url()
    return render_template('login.html', auth_url=auth_url)

##
#  Callback required by oauth2
#
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


##
#  Force a user to login
#
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

##
#  Route for unapproved sylabuses to be viewed by the instructor.
#    Doubles as private links ( not indexed in search )
@app.route('/syllabus')
def syllabus():
    try:
        syllabus = db.session.query(Syllabus).filter(Syllabus.id == request.args.get('id'))[0]
    except IndexError:
        return render_template('404.html'), 404
    editable = db.session.query(User,Course).filter(Course.syllabus == request.args.get('id')).filter(current_user.get_id() == Course.user).count()
    title = str(Course.query.filter_by(syllabus=syllabus.id).first())
    #print("{} {}".format(current_user.get_id(),editable))
    owns = False if editable == 0 else True
    if current_user.get_id() is None:
        owns = False
    auth_url = get_oauth_url()
    has_prof = True if Course.query.filter_by(syllabus=int(request.args.get('id'))).first().user is not None else False
    return render_template('syllabus.html', id=syllabus.id, syllabus=syllabus, owns=owns, auth_url=auth_url, adm=is_admin(), hasprof = has_prof, title=title)

##
#  Route for official Syllabus (Searchables)
#
@app.route('/official')
def official():
    thesyllabus = db.session.query(Official).filter(Official.id == request.args.get('id')).first()
    #print(thesyllabus)
    if thesyllabus is None or thesyllabus.visible is False:
        return render_template('404.html'), 404
    auth_url = get_oauth_url()
    unoffid = Syllabus.query.filter_by(official_id=thesyllabus.id).first().id
    owner = Course.query.filter_by(syllabus=unoffid).first().user
    title = str(Course.query.filter_by(syllabus=unoffid).first())
    owns = False
    logged_in = False
    user_id = None
    already_favorited = False
    if current_user.get_id() is not None:
        logged_in = True
        user_id=current_user.get_id()
        fav_query = Favorites.query.filter_by(user=user_id,official_id=thesyllabus.id).first()
        if fav_query is not None:
            already_favorited=True

        if int(owner) == int(current_user.get_id()):
            owns = True
    return render_template('official.html', id=thesyllabus.id, syllabus=thesyllabus, owns=owns, auth_url=auth_url, adm=is_admin(), unoffid=unoffid, logged_in=logged_in, user_id=user_id, already_favorited=already_favorited, title=title)

##
#  Remove Professor from course
#
@app.route('/remprof', methods=['POST'])
def remprof():
    if not is_admin():
        Logger.log("User {} attempted to remove instructor privileges".format(current_user.get_id()))
        return jsonify(status=2)
    crse = Course.query.filter_by(syllabus=int(request.form.get('id'))).first()
    if crse is None or crse.user is None:
        return jsonify(status=2)
    try:
        crse.user = None
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify(status=2)
    return jsonify(status=1)

##
#  Assign Professor to course
#
@app.route('/setprof', methods=['POST'])
def setprof():
    if not is_admin():
        Logger.log("User {} attempted to grant instructor privileges".format(current_user.get_id()))
        return jsonify(status=2)
    iid = User.query.filter_by(email=request.form.get('user')).first()
    if iid is None: # Need to add instructor
        newinst = User(email=request.form.get('user'))
        db.session.add(newinst)
        db.session.commit()
    iid = User.query.filter_by(email=request.form.get('user')).first()
    crse = Course.query.filter_by(syllabus=int(request.form.get('id'))).first()
    if crse is None or crse.user is not None:
        return jsonify(status=2)
    try:
        crse.user = iid.id
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify(status=2)
    return jsonify(status=1)
##
#  Save Syllabus Changes
#
@app.route('/save', methods = ['POST'])
def save():
    vals = []
    for i in range(1,12):
        if request.form.get('test'+str(i))[:3] == '<p>':
            vals.append(request.form.get('test'+str(i))[3:][:-4])
        else:
            vals.append(request.form.get('test'+str(i)))
    if not is_admin() and int(current_user.get_id()) != int(Course.query.filter_by(syllabus=vals[0]).first().user):
        Logger.log("User {} attempted to edit a syllabus".format(current_user.get_id()))
        return redirect(url_for('syllabus') + '?id={}'.format(vals[0]))
    syllabus = Syllabus.query.filter_by(id=vals[0]).first()
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

##
#  Remove A course
#
@app.route('/remove', methods = ['POST'])
def remove():
    if not is_admin():
        Logger.log("User {} attempted to add a course".format(current_user.get_id()))
        return jsonify(status=2)
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
##
#  Add a Course
#
@app.route('/add', methods = ['POST'])
def add():
    if not is_admin():
        Logger.log("User {} attempted to add a course".format(current_user.get_id()))
        return jsonify(status=2)
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
    if request.args.get('action') == 'approve':
        if not is_admin(): 
            Logger.log("User {} attempted to approve a syllabus.".format(current_user.get_id()))
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
            tmp.status = 'Approved'
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
    elif request.args.get('action') == 'deny':
        if not is_admin(): 
            Logger.log("User {} attempted to deny a syllabus.".format(current_user.get_id()))
        with open(queuefile, 'r') as qf:
            q = set(json.load(qf))
        with open(queuefile, 'w') as qf:
            q.remove(request.args.get('id'))
            json.dump(list(q), qf)
        tmp = Syllabus.query.filter_by(id=request.args.get('id')).first()
        if tmp is not None:
            try:
                tmp.status = 'Denied, please contact the administrators'
                db.session.commit()
            except:
                db.session.rollback()
    # Add to the queue
    elif request.args.get('action') == 'add':
        with open(queuefile, 'r') as qf:
            q = set(json.load(qf))
        with open(queuefile, 'w') as qf:
            q.add(request.args.get('id'))
            json.dump(list(q), qf)
        tmp = Syllabus.query.filter_by(id=request.args.get('id')).first()
        if tmp is not None:
            try:
                tmp.status = 'Pending'
                db.session.commit()
            except:
                db.session.rollback()
    return redirect(url_for('index'))
##
#  Give User Admin Privilegess
#
@app.route('/addadmin', methods=['POST'])
def addadmin():
    if not is_admin():
        Logger.log("User {} attempted to add an admin.".format(current_user.get_id()))
        return jsonify(status=2)
    try:
        toadd = request.form.get('addemail')
        addee = User.query.filter_by(email=toadd).first()
        if addee is not None:
            addee.admin = True
        else:
            addee = User(email=toadd, admin=True)
            db.session.add(addee)
        db.session.commit()
        return jsonify(status=1)
    except:
        db.session.rollback()
        return jsonify(status=2)
##
#  Remove User Admin Privilegess
#
@app.route('/remadmin', methods=['POST'])
def remadmin():
    if not is_admin():
        Logger.log("User {} attempted to remove an admin.".format(current_user.get_id()))
        return jsonify(status=2)
    try:
        torem = request.form.get('rememail')
        remee = User.query.filter_by(email=torem).first()
        if remee is not None:
            remee.admin = False
            db.session.commit()
            return jsonify(status=1)
        #print('Was none')
        return jsonify(status=2)
    except:
        #print('exception!')
        db.session.rollback()
        return jsonify(status=2)


##
#  Search destination, and results page.
#
@app.route('/search',methods = ['GET','POST'])
def search():
    # Pull values from request.
    # Validation done later
    semester = request.values.get('semester')
    year = request.values.get('year')
    department = request.values.get('department')
    section = request.values.get('section')
    search_text = request.values.get('search_text')
    course = request.values.get('course')

    sorted_results = find_matches(search_text,course,section,semester,year,department)
    auth_url = get_oauth_url()
    return render_template('search.html',results=sorted_results,auth_url=auth_url)

##
#  Advanced Search Page
#
@app.route('/adv_search',methods = ['GET'])
def adv_search():
    # DEPARTMENTS THING
    departments = []
    for i in Syllabus.query.filter(Syllabus.official_id != None):
        temp = Course.query.filter_by(syllabus=i.id).first().dept
        if temp not in departments:
            departments.append(temp)
    # unique post query
    depts = list(set(departments))
    auth_url = get_oauth_url()
    return render_template('advanced.html',auth_url=auth_url, depts=depts)

# so the goal here is to have only one instance of a user/id combo
# we change the button in jinja depending on if it exists or not.
# same for the create / delete logic
@app.route('/favorite',methods = ['POST','GET'])
def toggle_favorite():
    user_id=request.values.get('fav_user')
    fav_id=request.values.get('fav_id')

    check_me = Favorites.query.filter_by(user=user_id,official_id=fav_id).first()
    if check_me is None:
        new_fav = Favorites(user_id,fav_id)
        db.session.add(new_fav)
        db.session.commit()
    else:
        db.session.delete(check_me)
        db.session.commit()
    # Finished. redirect to the same page to have the button change.
    return redirect(url_for('official') + '?id={}'.format(fav_id))


##
#  Error Handling
#

# Custom 404 handler
@app.errorhandler(404)
def err404(err):
    return render_template('404.html'), 404

# Custom 500 handler
# for internal errors. replaced by debug page when debug server is running.
@app.errorhandler(500)
def err500(err):
    return render_template('500.html'), 500
