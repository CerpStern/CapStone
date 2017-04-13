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


