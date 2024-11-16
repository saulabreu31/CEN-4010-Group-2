from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import files  # Custom file handling module

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studyflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize the database
db = SQLAlchemy(app)

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




if __name__ == '__main__':
    # Create the database and tables if they don't exist
    with app.app_context():
        db.create_all()

    app.run(debug=True)
