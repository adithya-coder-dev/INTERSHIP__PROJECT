from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from controller.config import config
from controller.database import db
from controller.models import User

app = Flask(__name__)
app.config.from_object(config)

# Initialize database
db.init_app(app)

# ---------------- CREATE TABLES ----------------
with app.app_context():
    db.create_all()

# ---------------- HOME ----------------
@app.route("/")
def homepage():
    return render_template("homepage.html")

# ---------------- SIGN UP ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        # Auto login after signup
        session["user_id"] = user.user_id
        session["username"] = user.username
        session["role"] = user.role

        return redirect(url_for("login_success"))

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.user_id
            session["username"] = user.username
            session["role"] = user.role
            return redirect(url_for("login_success"))

        return "Invalid credentials"

    return render_template("login.html")

# ---------------- LOGIN SUCCESS ----------------
@app.route("/login-success")
def login_success():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "login_success.html",
        username=session["username"],
        role=session["role"]
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
