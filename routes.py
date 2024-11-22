from flask import Blueprint, render_template, redirect, url_for, request
from models import User, db  # Import models and database

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic
        return redirect(url_for('main.home'))
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration logic
        user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            dob=request.form['dob'],  # Convert to date if necessary
            email=request.form['email'],
            username=request.form['username'],
            password=request.form['password'],  # Hash this
            age=int(request.form['age']),
            gender=request.form['gender']
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main_bp.route('/calendar')
def calendar_page():
    return render_template('calendar.html', title='Calendar')

@main_bp.route('/uploadNotes', methods=['GET', 'POST'])
def uploadNotes():
    if request.method == 'POST':
        # Handle the form submission logic here
        pass
    return render_template('upload_notes.html', title='Upload Notes')

@main_bp.route('/uploadFiles', methods=['GET', 'POST'])
def uploadFiles():
    return render_template("uploadFile.html", title="Upload Files Form")

@main_bp.route('/courses')
def courses_page():
    return render_template('courses.html', title='Courses')


