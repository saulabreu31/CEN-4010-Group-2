import os
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, render_template, request, redirect, url_for
from models import db, UploadedFile, CalendarEvent, Studyflow, User, Note
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import files  # Custom file handling module
from NoteTakingSystem import NoteTakingSystem  # Note-taking system module
from calendar_function import *
from werkzeug.security import generate_password_hash
from forms import LoginForm
from routes import main_bp





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
@app.route('/deleteNote/<int:note_id>', methods=['POST'])
def deleteNote(note_id):
    try:
        # Find the note by ID
        note = Note.query.get_or_404(note_id)

        # Delete the note
        db.session.delete(note)
        db.session.commit()

        flash('Note deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting note: {str(e)}', 'error')

    return redirect(url_for('uploadNotes'))



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
    if form.validate_on_submit():  # This checks if the form was submitted and is valid
        # Retrieve login form data
        username = form.username.data
        password = form.password.data  # Plain text password from form

        # Fetch user from the database
        user = User.query.filter_by(username=username).first()

        if user:
            # Check if the password matches
            if check_password_hash(user.password, password):
                # Password is correct
                flash("Login successful!", "success")
                # You can set up a session or redirect to a protected route
                return redirect(url_for('dashboard'))  # Replace 'dashboard' with your target route
            else:
                # Password does not match
                flash("Invalid password. Please try again.", "error")
        else:
            # User not found
            flash("Username does not exist. Please register first.", "error")

        return redirect(url_for('login'))

    # Render the login form
    return render_template('login.html', title="Login", form=form)

@app.route('/users', methods=['GET'])
def show_users():
    users = User.query.all()
    user_data = [{"username": user.username, "email": user.email} for user in users]
    return render_template('users.html', users=user_data)




@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')
        state = request.form.get('state')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')  # Plain text password from form
        age = request.form.get('age')
        gender = request.form.get('gender')

        # Validate required fields
        if not all([first_name, last_name, dob, state, email, username, password, age, gender]):
            flash("All fields are required!")
            return redirect(url_for('register'))

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists!")
            return redirect(url_for('register'))

        # **Hash the password here**
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Create a new user with the hashed password
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            state=state,
            email=email,
            username=username,
            password=hashed_password,  # Save the hashed password
            age=int(age),
            gender=gender
        )

        # Add the user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for('register'))

    # Render the registration form
    return render_template('register.html', title="Create Account")




@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')
        state = request.form.get('state')
        country = request.form.get('country')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        age = request.form.get('age')
        gender = request.form.get('gender')

        # Validate required fields
        if not all([first_name, last_name, dob, state, country, email, username, password, age, gender]):
            flash("All fields are required!")
            return redirect(url_for('register'))

        # Create user object and save to database
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            state=state,
            country=country,
            email=email,
            username=username,
            password=password,
            age=age,
            gender=gender
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    pass





@app.route('/calendar/delete/<int:event_id>', methods=['DELETE'])
def delete_calendar_event(event_id):
    result = delete_event(event_id)
    return jsonify(result)

@app.route('/database')
def database_page():
    return render_template('database.html')




if __name__ == '__main__':
    # Print all the routes in the app
    print("Registered routes in the application:")
    print(app.url_map)
    

    # Create the database tables
    with app.app_context():
        db.create_all()  # Ensures tables are created
        print("Tables created successfully!")
    app.run(debug=True)
    

