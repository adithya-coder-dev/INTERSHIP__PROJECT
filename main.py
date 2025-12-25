from flask import Flask, render_template, session, redirect, request, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from controller.config import config
from controller.database import db
from controller.models import User, Role, Student, Staff, Subject, Chapter, Quiz, Question, StudentResult

app = Flask(__name__)
app.config.from_object(config)

# REQUIRED for flash & session
app.secret_key = "@12345abc"

db.init_app(app)

# ---------------- CREATE TABLES & DEFAULT DATA ----------------
with app.app_context():
    db.create_all()

    # ----- ROLES -----
    def get_or_create_role(role_name):
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)
        return role

    admin_role = get_or_create_role('admin')
    staff_role = get_or_create_role('staff')
    student_role = get_or_create_role('student')
    db.session.commit()

    # ----- ADMIN USER -----
    admin_user = User.query.filter_by(email='admin@qma.com').first()
    if not admin_user:
        admin_user = User(
            username='ADMIN',
            email='admin@qma.com',
            password_hash=generate_password_hash('123456')
        )
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        db.session.commit()
    else:
        if admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)
            db.session.commit()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template('home.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))

        role = user.roles[0].name if user.roles and len(user.roles) > 0 else None
        session['user_id'] = getattr(user, 'id', getattr(user, 'user_id', None))
        session['role'] = role
        session['user_name'] = user.username

        if role == 'staff':
            return redirect(url_for('staff_dashboard'))
        elif role == 'student':
            return redirect(url_for('student_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            flash('No role assigned', 'warning')
            return redirect(url_for('login'))
    return render_template('login.html')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if not all([role, name, email, password, confirm]):
            flash('Fill all fields', 'warning')
            return redirect(url_for('register'))
        if password != confirm:
            flash('Passwords do not match', 'warning')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=name).first():
            flash('Email or Username already exists', 'warning')
            return redirect(url_for('register'))

        new_user = User(username=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        role_obj = Role.query.filter_by(name=role).first()
        new_user.roles.append(role_obj)
        db.session.commit()

        if role == 'student':
            profile = Student(user_id=new_user.user_id, flag=False)
        elif role == 'staff':
            profile = Staff(user_id=new_user.user_id, flag=False)
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------- DASHBOARDS ----------------
@app.route('/staff-dashboard')
def staff_dashboard():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'staff':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    return render_template('staff_dashboard.html')

@app.route('/student-dashboard')
def student_dashboard():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    return render_template('student_dashboard.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'admin':
        session['user_id'] = 1
        session['role'] = 'admin'
        session['user_name'] = 'ADMIN'
    return render_template('admin_dashboard.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ---------------- API ENDPOINTS FOR QUIZ SYSTEM ----------------

# ---- Subjects ----
@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{'id':s.id,'name':s.name,
                     'chapters':[{'id':c.id,'name':c.name,
                                  'quizzes':[{'id':q.id,'name':q.name} for q in c.quizzes]} for c in s.chapters]} for s in subjects])

@app.route('/api/subjects', methods=['POST'])
def create_subject():
    data = request.json
    sub = Subject(name=data['name'])
    db.session.add(sub)
    db.session.commit()
    return jsonify({'status':'ok','id':sub.id})

@app.route('/api/subjects/<int:id>', methods=['PUT'])
def edit_subject(id):
    sub = Subject.query.get_or_404(id)
    sub.name = request.json['name']
    db.session.commit()
    return jsonify({'status':'ok'})

@app.route('/api/subjects/<int:id>', methods=['DELETE'])
def delete_subject(id):
    sub = Subject.query.get_or_404(id)
    db.session.delete(sub)
    db.session.commit()
    return jsonify({'status':'ok'})

@app.route('/api/subjects/<int:id>', methods=['GET'])
def subject_detail(id):
    sub = Subject.query.get_or_404(id)
    return jsonify({
        'id': sub.id,
        'name': sub.name,
        'chapters': [
            {
                'id': c.id,
                'name': c.name,
                'quizzes': [{'id': q.id, 'name': q.name} for q in c.quizzes]
            } for c in sub.chapters
        ]
    })


# ---- Chapters ----
@app.route('/api/chapters', methods=['POST'])
def create_chapter():
    data = request.json
    chap = Chapter(name=data['name'], subject_id=data['subject_id'])
    db.session.add(chap)
    db.session.commit()
    return jsonify({'status':'ok','id':chap.id})

@app.route('/api/chapters/<int:id>', methods=['PUT'])
def edit_chapter(id):
    chap = Chapter.query.get_or_404(id)
    chap.name = request.json['name']
    db.session.commit()
    return jsonify({'status':'ok'})

@app.route('/api/chapters/<int:id>', methods=['DELETE'])
def delete_chapter(id):
    chap = Chapter.query.get_or_404(id)
    db.session.delete(chap)
    db.session.commit()
    return jsonify({'status':'ok'})
@app.route('/api/chapters/<int:id>', methods=['GET'])
def chapter_detail(id):
    chap = Chapter.query.get_or_404(id)
    return jsonify({
        'id': chap.id,
        'name': chap.name,
        'quizzes': [{'id': q.id, 'name': q.name} for q in chap.quizzes]
    })

# ---- Quizzes ----
@app.route('/api/quizzes', methods=['POST'])
def create_quiz():
    data = request.json
    quiz = Quiz(name=data['name'], chapter_id=data['chapter_id'])
    db.session.add(quiz)
    db.session.commit()
    return jsonify({'status':'ok','id':quiz.id})

@app.route('/api/quizzes/<int:id>', methods=['PUT'])
def edit_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    quiz.name = request.json['name']
    db.session.commit()
    return jsonify({'status':'ok'})

@app.route('/api/quizzes/<int:id>', methods=['DELETE'])
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({'status':'ok'})


# ---- Questions ----
@app.route('/api/questions', methods=['POST'])
def create_question():
    data = request.json
    q = Question(text=data['text'], options=data['options'], answer=data['answer'], quiz_id=data['quiz_id'])
    db.session.add(q)
    db.session.commit()
    return jsonify({'status':'ok','id':q.id})

@app.route('/api/questions/<int:id>', methods=['PUT'])
def edit_question(id):
    q = Question.query.get_or_404(id)
    q.text = request.json['text']
    q.options = request.json['options']
    q.answer = request.json['answer']
    db.session.commit()
    return jsonify({'status':'ok'})

@app.route('/api/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
    q = Question.query.get_or_404(id)
    db.session.delete(q)
    db.session.commit()
    return jsonify({'status':'ok'})

# ---- Student Results ----
@app.route('/api/results', methods=['GET'])
def get_results():
    results = StudentResult.query.all()
    return jsonify([{'student':r.student.user.username,'quiz':r.quiz.name,'score':r.score} for r in results])

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
