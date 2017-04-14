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
#                WIP,        done,  done,   done,    WIP, WIP
def find_matches(search_text,course,section,semester,year,department):
    # we need to know how many syllabuses we have.
    # preset point counter to that size +1
    syll_count = 0
    for thing in Syllabus.query.filter(id!=0):
        syll_count = syll_count + 1
    # syllabus 1 at index 0, 2 at 1 etc, contents are current pointage.
    # auto expand to size of syll_count
    point_counter = [0] * syll_count

    # Just do this a few more times, in slightly different ways.
    #if is_provided(search_text):
    #    for match in Course.query.filter_by(semester=semester):
    #        point_counter[match.syllabus-1] = point_counter[match.syllabus-1] + 1

    if is_provided(course):
        for match in Course.query.filter_by(id=course ):
            point_counter[match.syllabus-1] = point_counter[match.syllabus-1] + 1

    if is_provided(section):
        for match in Course.query.filter_by(section=section):
            point_counter[match.syllabus-1] = point_counter[match.syllabus-1] + 1

    if is_provided(semester):
        for match in Course.query.filter_by(semester=semester):
            point_counter[match.syllabus-1] = point_counter[match.syllabus-1] + 1

    if is_provided(year):
        for match in Course.query.filter_by(year=year):
            point_counter[match.syllabus-1] = point_counter[match.syllabus-1] + 1

    if is_provided(department):
        for match in Course.query.filter_by(dept=department):
            point_counter[match.syllabus-1] = point_counter[match.syllabus-1] + 1


    return point_counter
