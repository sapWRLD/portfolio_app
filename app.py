from flask import Flask, redirect, render_template, request, url_for, flash
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta

# Initialize Flask app
UPLOAD_FOLDER = "static/images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = "Tessa"   # Secret key for session management
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'portfolio.db')
app.config["SESSION_PERMANENT"] = False  # Ensure the session is not permanent
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)# Shorten the lifetime of a session cookie (expires after inactivity)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allow_file(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# User model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True)   # Unique username
    password_hash = db.Column(db.String(200), nullable=False)  # Hashed password

# Mail model for storing Emails
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120))
    subject = db.Column(db.String(100))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255))  # path/URL to project image
    title = db.Column(db.String(80), nullable=False)
    text = db.Column(db.String(255))
    source_code = db.Column(db.String(255))


# Contact form model
class Contactform(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('subject', validators=[DataRequired(), Length(min=2, max=40)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route("/")
def home():
    all_projects = Projects.query.all()
    return render_template("index.html", projects=all_projects) 

@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No file part', 400
        file = request.files['image']
        if file.filename =="":
            return "No File selected", 400
        if file  and allow_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            return f"File uploaded successfully! Access it <a href='/{save_path}'>here</a>."
        else:
            return "Invalid file type", 400
    return render_template("upload.html")
    

# Login route (GET = show form, POST = authenticate user)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Fetch user from DB by username
        user = User.query.filter_by(user_name=request.form["username"]).first()
        
        # Check if user exists and password matches
        if user and check_password_hash(user.password_hash, request.form["password"]):
            login_user(user, remember=False)
            return redirect(url_for("dashboard"))
    
    return render_template("login.html")

# Protected dashboard route (requires login)
@app.route("/dashboard")
@login_required
def dashboard():
    users = User.query.all()
    projects = Projects.query.all()
    messages = Message.query.all()
    return render_template(
        "dashboard.html",
        name=current_user.user_name,
        users=users,
        projects=projects,
        messages=messages
    )

# Create User
@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("pass")
        if not username or not password:
            flash("Username and password are required!", "error")
            return render_template("create_user.html")
        if User.query.filter_by(user_name=username).first():
            flash("Username already exists!", "error")
            return render_template("create_user.html")
        new_user = User(user_name=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash("User created!", "success")
        return redirect(url_for("login"))
    return render_template("create_user.html")

# Edit User
@app.route("/dashboard/edit_user", methods=["POST"])
@login_required
def edit_user():
    user_id = request.form["user_id"]
    username = request.form["user_name"]
    user = User.query.get(user_id)
    if user:
        user.user_name = username
        db.session.commit()
        flash("User updated!", "success")
    return redirect(url_for("dashboard"))

# Delete User
@app.route("/dashboard/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted!", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard/delete_message/<int:msg_id>")
@login_required
def delete_message(msg_id):
    msg = Message.query.get(msg_id)
    if msg:
        db.session.delete(msg)
        db.session.commit()
        flash("Message deleted!", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard/create_project", methods=["POST"])
@login_required
def create_project():
    new_project = Projects(
        title=request.form["title"],
        text=request.form.get("text"),
        source_code=request.form.get("source_code"),
        image=request.form.get("image")
    )
    db.session.add(new_project)
    db.session.commit()
    flash("Project created!", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard/edit_project", methods=["POST"])
@login_required
def edit_project():
    project = Projects.query.get(request.form["project_id"])
    project.title = request.form["title"]
    project.text = request.form.get("text")
    project.source_code = request.form.get("source_code")
    project.image = request.form.get("image")
    db.session.commit()
    flash("Project updated!", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard/delete_project/<int:project_id>")
@login_required
def delete_project(project_id):
    project = Projects.query.get(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted!", "success")
    return redirect(url_for("dashboard"))


@app.route("/projects")
def projects():
    all_projects = Projects.query.all()
    return render_template("projects.html", projects=all_projects)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = Contactform()
    if form.validate_on_submit():
        new_message = Message(
            name = form.name.data,
            email = form.email.data,
            subject = form.subject.data,
            message = form.message.data
        )
        db.session.add(new_message)
        db.session.commit()
        flash('Thank you for submitting your message!', 'success')
        return redirect(url_for("contact"))
    return render_template("contact.html", form=form)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
