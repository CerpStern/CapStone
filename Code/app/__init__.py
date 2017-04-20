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

#APP creation and configuration
app = Flask(__name__)
app.config.from_object(config['prod'])
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

from app import views, models
