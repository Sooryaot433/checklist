from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    task = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(5), nullable=False)  # Format: HH:MM

# Create Tables
with app.app_context():
    db.create_all()

# Front Page
@app.route("/")
def front_page():
    return render_template("front_page.html")

# Home Page (Task List)
@app.route("/tasks")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    tasks = Task.query.filter_by(user_id=session["user_id"]).all()
    return render_template("index.html", tasks=tasks)

# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            return "User already exists! Try logging in."
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("index"))
        return "Invalid credentials!"
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

# Add Task
@app.route("/add_task", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    task = request.form["task"]
    time = request.form["time"]
    new_task = Task(user_id=session["user_id"], task=task, time=time)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("index"))

# Get Notifications
@app.route("/get_notifications")
def get_notifications():
    if "user_id" not in session:
        return jsonify({"tasks": []})

    now = datetime.datetime.now().strftime("%H:%M")
    tasks = Task.query.filter_by(user_id=session["user_id"], time=now).all()
    
    task_list = [{"id": task.id, "task": task.task} for task in tasks]

    # Delete tasks after notification
    for task in tasks:
        db.session.delete(task)
    db.session.commit()

    return jsonify({"tasks": task_list})

if __name__ == "__main__":
    app.run(debug=True)
