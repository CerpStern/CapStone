from __future__ import print_function
import os
import sys
import json
import datetime
import operator

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

# Logging class
class Logger:
    @staticmethod
    def log(message):
        print(message, file=sys.stderr)


# Checks if the logged in used is an admin
def is_admin():
    id = current_user.get_id()
    adm = User.query.filter_by(id=id).first()
    if adm is None:
        return False
    return adm.admin

# pull course from DB
def get_courses():
    user = current_user.get_id()
    matches = Course.query.filter_by(user=user)
    num = Course.query.filter_by(user=user).count()
    return matches, num

# Grab user info from DB
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# OAuth Session creation
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

# get oauth url for login button. needed on each route that uses render_template
def get_oauth_url():
    google = get_google_auth()
    auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return auth_url

# quick way to see if something was actually provided.
def is_provided(to_check):
    if to_check is not None and to_check is not "":
        return True
    else:
        return False

class search_obj:
    def __init__(self, sid, oid, course_string, contents, keywords):
        # ids to match against
        self.oid=oid
        self.sid=sid
        self.c_title=course_string
        # Keep a split version and an assigned version around
        self.split_course = course_string.split(" ")
        self.dept = self.split_course[0]
        self.course = self.split_course[1]
        self.section = self.split_course[2]
        self.semester = self.split_course[3]
        self.year = self.split_course[4]
        self.contents=contents
        self.keywords=keywords
        # default to 0
        self.points=0
    # Print all the things!! 
    def guts(self):
        print("SID: " + str(self.sid) + " OID: " + str(self.oid) + ", Course_string: " + self.course_string)

    def get_points(self):
        return self.points

    # First we need to make search functions for each section.
    # We assume that the input has been validated before it reaches this point.
    def match_course(self, course_in):
        if str(self.course)== course_in:
            self.points = self.points + 4
            return True
        else:
            return False
    def match_semester(self, semester_in):
            if self.semester == semester_in:
                self.points = self.points + 3
                return True
            else:
                return False
    def match_year(self, year_in):
        if str(self.year) == year_in:
            self.points = self.points + 2
            return True
        else:
            return False
    def match_dept(self, dept_in):
        if self.dept == dept_in:
            self.points = self.points + 2
            return True
        else:
            return False
    def match_section(self, section_in):
        # The conversion magic does not enjoy receiving an invalid number as a string
        # just fail if that's the case. it's cool. not your thing, I get it.
        try:
            section_in=str(int(section_in))
            if str(self.section) == section_in:
                self.points = self.points + 2
                return True
            else:
                return False
        except:
            return False

    # do not split before!!
    def match_search_text(self, search_text):
        split = search_text.split(" ")
        for s in split:
            if not self.match_course(s):
                self.match_course(s.lower())

            if not self.match_year(s):
                self.match_year(s.lower())

            if not self.match_dept(s):
                self.match_dept(s.lower())

            if not self.match_section(s):
                self.match_section(s.lower())

            if not self.match_semester(s):
                self.match_semester(s.lower())

            temp_points = 0
            if self.keywords != None:
                if len(self.keywords) > 1:
                    if search_text in self.keywords:
                        self.points = self.points + 3
                else:
                    for search_text in self.keywords.split(" "):
                        self.points = self.points + 3
            if s in self.contents:
                self.points = self.points + 2
            elif s.lower() in self.contents:
                self.points = self.points + 2



def find_matches(search_text,course_in,section,semester,year,department):
    # Cache Queries
    courses = Course.query.all()
    # Limits search space to visible sylls only
    officials = Official.query.filter_by(visible=True)
    sylls = Syllabus.query.all()
    # Array of search_obj's
    searchable = []

    # Compile info into easy to manage objects
    for c in courses:
        # grab oid and contents of relevant syllabus
        tmp_oid = [x.official_id for x in sylls if x.id is c.syllabus][0]
        contents = [x for x in sylls if x.id is c.syllabus][0]
        keywords=contents.keywords
        contents = str(contents).lower()
        searchable.append(search_obj(c.syllabus,tmp_oid,str(c),contents,keywords))

    for course in searchable:
        if is_provided(search_text):
            course.match_search_text(search_text)
        if is_provided(course_in):
            course.match_course(course_in)
        if is_provided(year):
            course.match_year(year)
        if is_provided(department):
            course.match_dept(department)
        if is_provided(section):
            course.match_section(section)
        if is_provided(semester):
            match_semester(semester)

    searchable.sort(reverse=True,key=operator.attrgetter('points'))
    return_me = []
    for s in searchable:
        if s.get_points() != 0 and s.oid!=None:
            return_me.append(s)
    print('hello')

    return return_me
