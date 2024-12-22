from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, Notice, Event, AcademicCalendar
from pymongo import MongoClient

# Initialize MongoDB client for admin login
uri = "mongodb+srv://tunemusicorg:mylanchi@cluster0.3sjfbhk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
mongo_db = client['campus_alerts']

# Admin blueprint setup
admin_bp = Blueprint('admin_bp', __name__)

# Decorators
def admin_required(f):
    """Decorator to ensure that the user is an admin."""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin_bp.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Routes

# Admin Dashboard
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    notices = Notice.query.all()
    events = Event.query.all()
    calendar_events = AcademicCalendar.query.all()

    return render_template(
        'admin_dashboard.html',
        notices=notices,
        events=events,
        calendar_events=calendar_events
    )

# Add Notice
@admin_bp.route('/add_notice', methods=['POST'])
@admin_required
def add_notice():
    title = request.form['title']
    category = request.form['category']
    description = request.form['description']

    new_notice = Notice(title=title, category=category, content=description)
    db.session.add(new_notice)
    db.session.commit()
    flash('Notice added successfully!', 'success')

    return redirect(url_for('admin_bp.admin_dashboard'))

# Add Event
@admin_bp.route('/add_event', methods=['POST'])
@admin_required
def add_event():
    try:
        title = request.form['title']
        date = request.form['date']
        description = request.form['description']

        new_event = Event(
            title=title,
            date=datetime.strptime(date, '%Y-%m-%d'),
            description=description
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Event added successfully!', 'success')
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')

    return redirect(url_for('admin_bp.admin_dashboard'))

# Add Calendar Event
@admin_bp.route('/add_calendar_event', methods=['POST'])
@admin_required
def add_calendar_event():
    try:
        month = request.form['month']
        date = request.form['date']
        description = request.form['description']

        new_calendar_event = AcademicCalendar(
            month=month,
            date=datetime.strptime(date, '%Y-%m-%d'),
            description=description
        )
        db.session.add(new_calendar_event)
        db.session.commit()
        flash('Calendar event added successfully!', 'success')
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')

    return redirect(url_for('admin_bp.admin_dashboard'))

# Admin Logout
@admin_bp.route('/logout')
@admin_required
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('admin_bp.admin_login'))

# Admin Login Route for MongoDB
@admin_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check MongoDB admin collection
        admin = mongo_db['admins'].find_one({"username": username})

        if admin and check_password_hash(admin['password'], password):
            session['admin_logged_in'] = True
            flash("Logged in successfully!", 'success')
            return redirect(url_for('admin_bp.admin_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/admin.html')

# Initialize the admin user if not exists
def init_admin(app):
    with app.app_context():
        # Add default SQLite admin if not exists
        from app import User
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
            admin_user = User(username='admin', password=hashed_password, role='admin')
            db.session.add(admin_user)
            db.session.commit()

        # Add MongoDB admin if not exists
        if not mongo_db['admins'].find_one({"username": "admin"}):
            hashed_password = generate_password_hash('admin1', method='pbkdf2:sha256')
            admin_data = {
                "username": "admin",
                "password": hashed_password
            }
            mongo_db['admins'].insert_one(admin_data)

