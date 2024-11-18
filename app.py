from flask import Flask, render_template, request, jsonify
from models import db, UploadedFile, CalendarEvent
from datetime import datetime
import files  # Custom file handling module
#<<<<<<< Updated upstream
from NoteTakingSystem import NoteTakingSystem  # Note-taking system module
#=======
from calendar_function import *


#>>>>>>> Stashed changes

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studyflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize database with the Flask app
db.init_app(app)



#<<<<<<< Updated upstream
# Initialize the note-taking system
note_system = NoteTakingSystem()


#=======
#>>>>>>> Stashed changes

@app.route('/')
def home():
    return render_template('index.html', title='Study Flow')

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
    return files.handle_file_upload(file)

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
    """
    Display the notes upload form (GET) or handle note uploads (POST).
    """
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        note_title = request.form.get('note_title')
        content = request.form.get('content')
        if not course_name or not note_title or not content:
            return jsonify({"error": "All fields are required"}), 400
        
        response = note_system.create_note(
            course_name=course_name,
            note_title=note_title,
            content=content
        )
        return jsonify(response)

    # Render the form for GET requests
    return render_template('upload_notes.html', title='Upload Notes')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html', title='Register')

@app.route('/calendar/events', methods=['GET'])
def get_user_events():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        events = get_events(user_id)
        return jsonify([{
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time.isoformat(),
            'end_time': event.end_time.isoformat()
        } for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calendar/add', methods=['POST'])
def add_calendar_event():
    try:
        data = request.json
        if not all(k in data for k in ['user_id', 'title', 'start_time', 'end_time']):
            return jsonify({'error': 'Missing required fields'}), 400

        result = add_event(
            user_id=data['user_id'],
            title=data['title'],
            description=data.get('description', ''),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time'])
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calendar/update/<int:event_id>', methods=['PUT'])
def update_calendar_event(event_id):
    data = request.json
    result = update_event(
        event_id=event_id,
        title=data.get('title'),
        description=data.get('description'),
        start_time=datetime.fromisoformat(data.get('start_time')) if 'start_time' in data else None,
        end_time=datetime.fromisoformat(data.get('end_time')) if 'end_time' in data else None
    )
    return jsonify(result)

@app.route('/calendar/delete/<int:event_id>', methods=['DELETE'])
def delete_calendar_event(event_id):
    result = delete_event(event_id)
    return jsonify(result)




if __name__ == '__main__':
    # Print all the routes in the app
    print("Registered routes in the application:")
    print(app.url_map)
    
    # Run the Flask app
    app.run(debug=True)
