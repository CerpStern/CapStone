import os
import json
import datetime

from flask import Flask, url_for, redirect, \
    render_template, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, \
    logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError

basedir = os.path.abspath(os.path.dirname(__file__))

"""App Configuration"""


class Auth:
    """Google Project Credentials"""
    CLIENT_ID = ('486646633132-nc0hlcn0vt7khirhmhkh518d84omqjea'
                 '.apps.googleusercontent.com')
    CLIENT_SECRET = 'NNKF51kaBY-5RIMpOW1S2bjd'
    REDIRECT_URI = 'https://localhost:5000/gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']


class Config:
    """Base config"""
    APP_NAME = "SMS"
    SECRET_KEY = "NNKF51kaBY-5RIMpOW1S2bjd"


class DevConfig(Config):
    """Dev config"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "test.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    """Production config"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "test.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}

class Template():
    basic = '<h3>Intro to Blah Blah Blah</h3><p>Meeting Time: XX:XX - XX:XX Day1, Day2</p><p>Meeting Place: Room XXX Foo Hall</p><p>Course Website:</p><p>Intructor Name: Bob Loblaw</p><p>Office Hours: XX:XX - XX:XXX Day1, Day2 Room XXX Building</p><p>Required Materials if any:</p><p>Prerequisites if any:</p>'
    description = 'Course Description Goes Here'
    topics = 'Topics Covered Go Here'
    outcomes = 'Learning Outcomes Go Here'
    grading = 'Grading Policy Goes Here'
    schedule = 'Planned Schedule Goes Here'
    honesty = 'Cheating means to misrepresent the source, nature, or other conditions of your academic work (e.g., tests, papers, projects, assignments) so as to get underserved credit. The use of the intellectual property of others without giving them appropriate credit is a serious academic offense. The University considers cheating and plagiarism very serious offenses and provides for sanctions up to and including dismissal from the University or revocation of a degree. The University&rsquo;s administrative policy and procedures regarding student cheating and plagiarism can be found in the <a href="https://www.kent.edu/policyreg/administrative-policy-regarding-student-cheating-and-plagiarism" target="_blank" rel="noopener noreferrer">Administrative Policy, 3-01.8</a>. By submitting any material in this (or any other class) you are certifying that it is free of plagiarism.'
    deadlines = 'Students have responsibility to ensure they are properly enrolled in classes. You are advised to review your official class schedule (using Student Tools in FlashLine) during the first two weeks of the semester to ensure you are properly enrolled in this class and section. Should you find an error in your class schedule, you have until cut-off date provided by the Undergraduate Office to correct the error with your advising office. If registration errors are not corrected by the cut-off date and you continue to attend and participate in classes for which you are not officially enrolled, you are advised now that you will not receive a grade at the conclusion of the semester for any class in which you are not properly registered.'
    accessibility = 'University policy 3342-3-01.3 requires that students with disabilities be provided reasonable accommodations to ensure their equal access to course content. If you have a documented disability and require accommodations, please contact the instructor at the beginning of the semester to make arrangements for necessary classroom adjustments. Please note, you must first verify your eligibility for these through the Student Accessibility Services (contact 330-672-3391 or visit <a href="http://www.kent.edu/sas" target="_blank" rel="noopener noreferrer">www.kent.edu/sas</a> for more information on registration procedures).'
    keywords = 'Learning'
