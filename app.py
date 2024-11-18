from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import files  # Custom file handling module
from NoteTakingSystem import NoteTakingSystem  # Note-taking system module

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studyflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize the database
db = SQLAlchemy(app)

# Initialize the note-taking system
note_system = NoteTakingSystem()

# Database model for File uploads
class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)

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

@app.route('/uploadCalendar')
def uploadCalendar():
    return "Upload Calendar functionality coming soon!"

# Upload notes form route
@app.route('/uploadNotes', methods=['GET', 'POST'])
def upload_notes():
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



if __name__ == '__main__':
    # Print all the routes in the app
    print("Registered routes in the application:")
    print(app.url_map)
    
    # Run the Flask app
    app.run(debug=True)
