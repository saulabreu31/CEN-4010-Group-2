import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_migrate import Migrate
from models import db, UploadedFile, CalendarEvent, Studyflow, User, Note
from datetime import datetime
from forms import LoginForm
from routes import main_bp
from NoteTakingSystem import NoteTakingSystem  # Note-taking system module
from calendar_function import *
from werkzeug.security import generate_password_hash, check_password_hash


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studyflow.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    

    # Initialize database and migration
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(main_bp)

    return app

# Initialize app and database
app = create_app()
note_system = NoteTakingSystem()

# Create tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

# Routes for additional functionality
@app.route('/')
def home():
    return render_template('index.html', title='Study Flow')

@app.route('/database')
def database_page():
    return render_template('database.html')

if __name__ == '__main__':
    # Print all registered routes for debugging
    print("Registered routes:")
    print(app.url_map)

    # Run the application
    app.run(debug=True)

    

