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

from app import db

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
