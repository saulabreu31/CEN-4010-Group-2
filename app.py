import os
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, render_template, request, redirect, url_for
from models import db, UploadedFile, CalendarEvent, Studyflow, User, Note
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import files  # Custom file handling module
from NoteTakingSystem import NoteTakingSystem  # Note-taking system module
from calendar_function import *




app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studyflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize database with the Flask app
db.init_app(app)

migrate = Migrate(app, db)

courses = []




# Initialize the note-taking system
note_system = NoteTakingSystem()


@app.route('/')
def home():
    return render_template('index.html', title='Study Flow')

@app.route('/courses')
def courses_page():
    return render_template('courses.html')


@app.route('/courses', methods=['GET', 'POST'])
def managing_courses():
    if request.method == 'POST':
        # Get form data
        class_name = request.form['class_name']
        time = request.form['time']
        location = request.form['location']
        
        # Create a new course entry
        new_course = Studyflow(class_name=class_name, time=time, location=location)
        db.session.add(new_course)
        db.session.commit()

    # Query all courses
    courses = Studyflow.query.all()
    return render_template('courses.html', title='Courses', courses=courses)

@app.route('/uploadForm', methods=['GET', 'POST'])
def uploadFiles():
    return render_template("uploadFile.html", title="Upload Files Form")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']

    # Save file details to the database
    uploaded_file = UploadedFile(
        filename=file.filename,
        content_type=file.content_type,
        upload_time=db.func.now()
    )
    db.session.add(uploaded_file)
    db.session.commit()

    # Process the file using custom logic
    #return files.handle_file_upload(file)
    flash(f'File "{file.filename}" uploaded successfully!', 'success')
    return redirect(url_for('uploaded_files'))

@app.route('/uploadedFiles')
def uploaded_files():
    # List files in the upload folder
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('uploaded_files.html', title='Uploaded Files', files=files)

@app.route('/uploads/<filename>')
def download_file(filename):
    # Serve files from the upload folder
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/users')
def users_view():
    # Query all registered users from the database
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/pageReplacement')
def pageReplacement():
    return "Page Replacement Simulator"

@app.route('/calendar')
def calendar_page():
    return render_template('calendar.html', title='Calendar')


# Upload notes form route
@app.route('/uploadNotes', methods=['GET', 'POST'])
def uploadNotes():
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        note_title = request.form.get('note_title')
        content = request.form.get('content')

        if not all([course_name, note_title, content]):
            flash("All fields are required", "error")
            return redirect(url_for('uploadNotes'))

        # Save the note to the database
        new_note = Note(course_name=course_name, title=note_title, content=content)
        db.session.add(new_note)
        db.session.commit()
        flash("Note uploaded successfully!", "success")

        return redirect(url_for('uploadNotes'))

    # Query all saved notes
    notes = Note.query.order_by(Note.timestamp.desc()).all()
    return render_template('upload_notes.html', title='Upload Notes', notes=notes)


# Notes API: Create a note
@app.route('/notes/create', methods=['POST'])
def create_note():
    """
    Endpoint to create a new note.
    Request JSON should include 'course_name', 'note_title', and 'content'.
    """
    data = request.json
    if not data or not all(key in data for key in ['course_name', 'note_title', 'content']):
        return jsonify({"error": "Missing required fields"}), 400

    response = note_system.create_note(
        course_name=data['course_name'],
        note_title=data['note_title'],
        content=data['content']
    )
    return jsonify(response)

# Notes API: View notes for a course
@app.route('/notes/<course_name>', methods=['GET'])
def view_notes(course_name):
    """
    Endpoint to view all notes for a specific course.
    """
    response = note_system.view_notes(course_name)
    return jsonify(response)

# Notes API: Read a specific note
@app.route('/notes/read', methods=['POST'])
def read_note():
    """
    Endpoint to read the content of a specific note.
    Request JSON should include 'note_path'.
    """
    data = request.json
    if not data or 'note_path' not in data:
        return jsonify({"error": "Missing 'note_path' field"}), 400

    response = note_system.read_note_content(data['note_path'])
    return jsonify(response)

# Notes API: Delete a specific note
@app.route('/notes/delete', methods=['POST'])
def delete_note():
    """
    Endpoint to delete a specific note.
    Request JSON should include 'note_path'.
    """
    data = request.json
    if not data or 'note_path' not in data:
        return jsonify({"error": "Missing 'note_path' field"}), 400

    response = note_system.delete_note(data['note_path'])
    return jsonify(response)



@app.route('/calendar/events', methods=['GET'])
def get_user_events():
    try:
        user_id = request.args.get('user_id')
        print(f"Received request for user_id: {user_id}")  # Debug print


        if not user_id:
            print("No user_id provided")  # Debug print
            return jsonify({'error': 'User ID is required'}), 400


        events = get_events(user_id)
        print(f"Retrieved events: {events}")  # Debug print


        # Check if we got an error
        if isinstance(events, dict) and 'error' in events:
            return jsonify(events), 500


        # If events is a list, return it
        return jsonify(events)


    except Exception as e:
        print(f"Error in get_user_events: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500

@app.route('/calendar/add', methods=['POST'])
def add_calendar_event():
    try:
        data = request.json
        print(f"Received event data: {data}")  # Debug print


        if not all(k in data for k in ['user_id', 'title', 'start_time', 'end_time']):
            return jsonify({'error': 'Missing required fields'}), 400


        result = add_event(
            user_id=data['user_id'],
            title=data['title'],
            description=data.get('description', ''),
            start_time=datetime.fromisoformat(data['start_time'].replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        )


        print(f"Add event result: {result}")  # Debug print


        # Check if we got an error
        if isinstance(result, dict) and 'error' in result:
            return jsonify(result), 500


        return jsonify(result)


    except Exception as e:
        print(f"Error in add_calendar_event: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500


@app.route('/debug/events')
def debug_events():
    try:
        events = CalendarEvent.query.all()
        return jsonify([{
            'id': e.id,
            'user_id': e.user_id,
            'title': e.title,
            'description': e.description,
            'start_time': e.start_time.isoformat() if e.start_time else None,
            'end_time': e.end_time.isoformat() if e.end_time else None
        } for e in events])
    except Exception as e:
        return jsonify({'error': str(e)})

from forms import LoginForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Authenticate user
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):  # Assuming check_password verifies the password
            session['user_id'] = user.id  # Save user ID in session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))

        # If authentication fails
        flash('Invalid username or password.', 'error')

    return render_template('login.html', title='Login', form=form)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')  # Hash this before saving
        # (other fields)

        # Check if username or email is already registered
        if User.query.filter_by(username=username).first():
            flash('Username is already taken', 'error')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(
            username=username,
            password=password,  # Hash this before saving
            # (other fields)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    pass

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    pass





@app.route('/calendar/delete/<int:event_id>', methods=['DELETE'])
def delete_calendar_event(event_id):
    result = delete_event(event_id)
    return jsonify(result)




if __name__ == '__main__':
    # Print all the routes in the app
    print("Registered routes in the application:")
    print(app.url_map)
    

    # Create the database tables
    with app.app_context():
        db.create_all()  # Ensures tables are created
    app.run(debug=True)
