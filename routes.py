from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, send_from_directory, current_app
from models import User, db, Note, Studyflow, UploadedFile, CalendarEvent  # Import models and database
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from forms import LoginForm
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)
UPLOAD_FOLDER = 'uploads'

# Home Page
@main_bp.route('/')
def home():
    return render_template('index.html')

# Login Page
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Instantiate the form
    if form.validate_on_submit():
        # Handle login logic
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            flash("Login successful!", "success")
            return redirect(url_for('main.home'))
        flash("Invalid username or password", "error")
    return render_template('login.html', form=form)
# Registration Page
from datetime import datetime

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')  # This is initially a string
        state = request.form.get('state')
        country = request.form.get('country')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')  # Plain text password from form
        age = request.form.get('age')
        gender = request.form.get('gender')

        # Validate required fields
        if not all([first_name, last_name, dob, email, username, password, age, gender]):
            flash("All fields are required!")
            return redirect(url_for('main.register'))

        # Convert dob to a Python date object
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect(url_for('main.register'))

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists!")
            return redirect(url_for('main.register'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Create a new user with the hashed password
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            dob=dob_date,  # Use the converted date object
            state=state,
            country=country,
            email=email,
            username=username,
            password=hashed_password,
            age=int(age),
            gender=gender
        )

        # Add the user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.")
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for('main.register'))

    return render_template('register.html', title="Create Account")


# Calendar Page
@main_bp.route('/calendar')
def calendar_page():
    return render_template('calendar.html', title='Calendar')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('main.uploadFiles'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('main.uploadFiles'))

    # Save the file to the UPLOAD_FOLDER
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Save file details to the database, including content type
    uploaded_file = UploadedFile(
        filename=file.filename,
        content_type=file.content_type,  # This fetches the content type (e.g., 'application/pdf')
        upload_time=datetime.utcnow()
    )
    db.session.add(uploaded_file)
    db.session.commit()

    flash(f'File "{file.filename}" uploaded successfully!', 'success')
    return redirect(url_for('main.uploaded_files'))



# Upload Notes Page
@main_bp.route('/uploadNotes', methods=['GET', 'POST'])
def uploadNotes():
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        note_title = request.form.get('note_title')
        content = request.form.get('content')

        if not all([course_name, note_title, content]):
            flash("All fields are required", "error")
            return redirect(url_for('main.uploadNotes'))

        # Save the note to the database
        new_note = Note(
            course_name=course_name,
            title=note_title,
            content=content,
            timestamp=datetime.utcnow()  # Add a timestamp
        )
        db.session.add(new_note)
        db.session.commit()
        flash("Note uploaded successfully!", "success")

        return redirect(url_for('main.uploadNotes'))

    # Order notes by descending timestamp
    notes = Note.query.order_by(Note.timestamp.desc()).all()  # Adjust this query
    return render_template('upload_notes.html', title='Upload Notes', notes=notes)


# Upload Files Page
@main_bp.route('/uploadFiles', methods=['GET', 'POST'])
def uploadFiles():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash("No file selected!", "error")
            return redirect(url_for('main.uploadFiles'))
        
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        uploaded_file = UploadedFile(
            filename=file.filename,
            content_type=file.content_type,
            upload_time=datetime.utcnow()
        )
        db.session.add(uploaded_file)
        db.session.commit()
        flash(f'File "{file.filename}" uploaded successfully!', "success")
    return render_template("uploadFile.html", title="Upload Files Form")

# Courses Page
@main_bp.route('/courses', methods=['GET', 'POST'])
def courses_page():
    if request.method == 'POST':
        class_name = request.form['class_name']
        time = request.form['time']
        location = request.form['location']

        new_course = Studyflow(class_name=class_name, time=time, location=location)
        db.session.add(new_course)
        db.session.commit()
        flash("Course added successfully!", "success")
    courses = Studyflow.query.all()
    return render_template('courses.html', title='Courses', courses=courses)

# List Uploaded Files
@main_bp.route('/uploadedFiles')
def uploaded_files():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('uploaded_files.html', title='Uploaded Files', files=files)

# Download Uploaded File
@main_bp.route('/uploads/<filename>')
def download_file(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)


# Delete Notes API
@main_bp.route('/deleteNote/<int:note_id>', methods=['POST'])
def deleteNote(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!', "success")
    return redirect(url_for('main.uploadNotes'))

# Logout
@main_bp.route('/logout')
def logout():
    # Logic for logging out the user
    flash("Logged out successfully!", "success")
    return redirect(url_for('main.login'))

@main_bp.route('/calendar/events', methods=['GET'])
def get_events():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        user_id = int(user_id)
        events = CalendarEvent.query.filter_by(user_id=user_id).all()

        events_list = [{
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time.isoformat(),
            'end_time': event.end_time.isoformat()
        } for event in events]

        return jsonify(events_list)

    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/calendar/add', methods=['POST'])
def add_event():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['user_id', 'title', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing {field}'}), 400

        # Convert string times to datetime objects
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])

        new_event = CalendarEvent(
            user_id=data['user_id'],
            title=data['title'],
            description=data.get('description', ''),
            start_time=start_time,
            end_time=end_time
        )

        db.session.add(new_event)
        db.session.commit()

        return jsonify({
            'success': True,
            'event': {
                'id': new_event.id,
                'title': new_event.title,
                'description': new_event.description,
                'start_time': new_event.start_time.isoformat(),
                'end_time': new_event.end_time.isoformat()
            }
        })

    except ValueError as ve:
        logger.error(f"Value error: {str(ve)}")
        return jsonify({'error': 'Invalid datetime format'}), 400

    except Exception as e:
        logger.error(f"Error adding event: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/calendar/delete/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = CalendarEvent.query.get(event_id)

        if not event:
            return jsonify({'error': 'Event not found'}), 404

        db.session.delete(event)
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error deleting event: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500




