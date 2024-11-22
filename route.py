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
        # Retrieve form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')  # Format: 'YYYY-MM-DD'
        state = request.form.get('state')
        country = request.form.get('country')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        age = request.form.get('age')
        gender = request.form.get('gender')

        # Validate required fields
        if not all([first_name, last_name, dob, state, email, username, password, age, gender]):
            flash("All fields are required!", "error")
            return redirect(url_for('register'))

        # Convert DOB to date object
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Create the new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            dob=dob_date,  # Use the converted date
            state=state,
            country=country,
            email=email,
            username=username,
            password=hashed_password,
            age=int(age),
            gender=gender
        )

        # Add to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('register'))

    return render_template('register.html', title="Create Account")

