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

from config import config, Auth, Template

queuefile = 'queue.json'

basedir = os.path.abspath(os.path.dirname(__file__))

from app import db

# DB Models


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
    favorites = db.relationship('Favorites')

class Favorites(db.Model):
    __tablename__ = "favorites"
    def __init__(self, user_id, oid):
        self.user = user_id
        self.official_id = oid
    id = db.Column(db.Integer,primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    official_id = db.Column(db.Integer, db.ForeignKey('official.id'))

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
    id = db.Column(db.Integer, primary_key=True)
    basic = db.Column(db.String, default=Template.basic)
    description = db.Column(db.String, default=Template.description)
    topics = db.Column(db.String, default=Template.topics)
    outcomes = db.Column(db.String, default=Template.outcomes)
    grading = db.Column(db.String, default=Template.grading)
    schedule = db.Column(db.String, default=Template.schedule)
    honesty = db.Column(db.String, default=Template.honesty)
    deadlines = db.Column(db.String, default=Template.deadlines)
    accessibility = db.Column(db.String, default=Template.accessibility)
    keywords = db.Column(db.String)
    status = db.Column(db.String, default='Not yet submitted')
    official_id = db.Column(db.Integer, db.ForeignKey('official.id'), default=None)
    official = db.relationship('Official', back_populates='syllabi')
    course = db.relationship('Course')


class Official(db.Model):
    __tablename__ = "official"
    def __str__(self):
        return '<div id="id">{}</div><div id="basic">{}</div><div id="description">{}</div><div id="topics">{}</div><div id="outcomes">{}</div><div id="grading">{}</div><div id="schedule">{}</div><div id="honesty">{}</div><div id="deadlines">{}</div><div id="accessibility">{}</div><div id="keywords">{}</div>'.format(self.id, self.basic, self.description, self.topics, self.outcomes, self.grading, self.schedule, self.honesty, self.deadlines, self.accessibility, self.keywords)
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
    visible = db.Column(db.Boolean, default=True)
    syllabi = db.relationship('Syllabus', back_populates='official', uselist=False)
