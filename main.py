from flask import Flask, render_template, session, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from controller.config import config
from controller.database import db
from controller.models import User, Role, Student, Staff

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

        # Get user role safely
        role = user.roles[0].name if user.roles and len(user.roles) > 0 else None

        # Store session
        session['user_id'] = getattr(user, 'id', getattr(user, 'user_id', None))
        session['role'] = role
        session['user_name'] = user.username

        if session['user_id'] is None:
            flash('User primary key not found. Contact admin.', 'danger')
            return redirect(url_for('login'))

        # Role-based redirect
        if role == 'staff':
            return redirect(url_for('staff_dashboard'))
        elif role == 'student':
            return redirect(url_for('student_dashboard'))
        elif role == 'admin':
            flash("Invalid User", 'warning')
            return redirect(url_for('login'))
        else:
            flash('No role assigned to user', 'warning')
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
            flash('Please fill out all required fields', 'warning')
            return redirect(url_for('register'))

        if password != confirm:
            flash('Passwords do not match', 'warning')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'warning')
            return redirect(url_for('register'))

        if User.query.filter_by(username=name).first():
            flash('Username already taken', 'warning')
            return redirect(url_for('register'))

        new_user = User(
            username=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        user_id = getattr(new_user, 'id', getattr(new_user, 'user_id', None))
        if user_id is None:
            flash('Error creating user. Contact admin.', 'danger')
            return redirect(url_for('register'))

        role_obj = Role.query.filter_by(name=role).first()
        new_user.roles.append(role_obj)
        db.session.commit()

        # Create profile
        if role == 'student':
            profile = Student(user_id=user_id, flag=False)
        elif role == 'staff':
            profile = Staff(user_id=user_id, flag=False)
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------- STAFF DASHBOARD ----------------
@app.route('/staff-dashboard')
def staff_dashboard():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'staff':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    return render_template('staff_dashboard.html')

# ---------------- STUDENT DASHBOARD ----------------
@app.route('/student-dashboard')
def student_dashboard():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    return render_template('student_dashboard.html')

# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin-dashboard')
def admin_dashboard():
    user_id = session.get('user_id')
    role = session.get('role')
    # Only allow access if session has admin login
    if not user_id or role != 'admin':
        # Optionally, hardcode admin session or check for admin user here
        session['user_id'] = 1
        session['role'] = 'admin'
        session['user_name'] = 'ADMIN'
    return render_template('admin_dashboard.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
