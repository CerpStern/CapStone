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
    course = db.relationship('Course')
