from controller.database import db
from datetime import datetime

# ---------------- User Models ----------------
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    roles = db.relationship(
        'Role',
        secondary='user_role',
        backref=db.backref('users', lazy='dynamic')
    )
    student_details = db.relationship('Student', backref='user', lazy=True, uselist=False)
    staff_details = db.relationship('Staff', backref='user', lazy=True, uselist=False)

class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id', ondelete='CASCADE'), nullable=False)

class Staff(db.Model):
    __tablename__ = 'staff'
    staff_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    flag = db.Column(db.Boolean, default=False)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    flag = db.Column(db.Boolean, default=False)

# ---------------- Quiz Models ----------------
class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    chapters = db.relationship(
        'Chapter',
        backref='subject',
        cascade="all, delete-orphan",
        lazy=True,
        order_by='Chapter.order_index'
    )
    order_index = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
    quizzes = db.relationship(
        'Quiz',
        backref='chapter',
        cascade="all, delete-orphan",
        lazy=True,
        order_by='Quiz.order_index'
    )
    order_index = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    questions = db.relationship(
        'Question',
        backref='quiz',
        cascade="all, delete-orphan",
        lazy=True,
        order_by='Question.order_index'
    )
    results = db.relationship('StudentResult', backref='quiz', cascade="all, delete-orphan", lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.PickleType, nullable=False)  # List of 4 options
    answer = db.Column(db.Integer, nullable=False)      # 1-4 for correct option
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudentResult(db.Model):
    __tablename__ = 'student_result'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id', ondelete='CASCADE'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    student = db.relationship('Student', backref='results')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)