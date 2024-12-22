from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from pymongo import MongoClient
import os

# Initialize SQLAlchemy globally
db = SQLAlchemy()
client = MongoClient(os.getenv('MONGODB_URI'))
# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

class AcademicCalendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def create_app():
    app = Flask(__name__)
    
    # Flask configuration
    app.secret_key = 'your_secret_key'  # Change this to a secure secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # MongoDB configuration
    uri = "mongodb+srv://tunemusicorg:mylanchi@cluster0.3sjfbhk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&ssl=true"
    client = MongoClient(uri)
    mongo_db = client['campus_alerts']
    try:
        client = MongoClient(uri)
        # Test the connection
        client.admin.command('ping')
        mongo_db = client['campus_alerts']
        
        # Make MongoDB collections accessible
        app.mongo_notices = mongo_db['notices']
        app.mongo_admins = mongo_db['admins']
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection failed: {str(e)}")
        raise
    
    # Make MongoDB collections accessible throughout the app
    app.mongo_notices = mongo_db['notices']
    app.mongo_admins = mongo_db['admins']

    with app.app_context():
        # all tables
        db.create_all()
        
        # Register blueprints
        from routes.events import events_bp
        from routes.notices import notices_bp
        from routes.academic import academic
        from routes.event_update import events_up
        from routes.notices_update import notices_up
        from routes.calender_update import calendar_up
        app.register_blueprint(events_bp)
        app.register_blueprint(notices_bp, url_prefix='/notices')
        app.register_blueprint(academic, url_prefix='/academic')
        app.register_blueprint(events_up)
        app.register_blueprint(notices_up)
        app.register_blueprint(calendar_up)

    # User Authentication Routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'danger')

        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('register'))

            if User.query.filter_by(username=username).first():
                flash('Username already exists.', 'danger')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    # Admin Routes
     # Remove the second `@app.route('/admin/login')` and keep the correct one.



    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        notices = Notice.query.all()
        events = Event.query.all()
        calendar_events = AcademicCalendar.query.all()

        return render_template(
            'admin.html',
            notices=notices,
            events=events,
            calendar_events=calendar_events
        )
    
# Admin Login Route for MongoDB
    @app.route('/admin_login', methods=['GET', 'POST'])
    def admin_login():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check MongoDB admin collection
        admin = app.mongo_admins.find_one({"username": username})

        if admin and check_password_hash(admin['password'], password):
            session['admin_logged_in'] = True
            flash("Logged in successfully!", 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

     return render_template('auth/admin.html')

    @app.route('/add_notice', methods=['POST'])
    @admin_required
    def add_notice():
        title = request.form['title']
        category = request.form['category']
        description = request.form['description']

        new_notice = Notice(title=title, category=category, content=description)
        db.session.add(new_notice)
        db.session.commit()
        flash('Notice added successfully!', 'success')

        return redirect(url_for('admin_dashboard'))

    @app.route('/add_event', methods=['POST'])
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

        return redirect(url_for('admin_dashboard'))

    @app.route('/add_calendar_event', methods=['POST'])
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

        return redirect(url_for('admin_dashboard'))

    @app.route('/admin_logout')
    @admin_required
    def admin_logout():
        session.pop('admin_logged_in', None)
        flash('Logged out successfully!', 'info')
        return redirect(url_for('admin_login'))

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    # Global route protection
    @app.before_request
    def restrict_routes():
        public_routes = ['login', 'admin_login', 'register', 'static']
        if request.endpoint and request.endpoint.split('.')[0] not in public_routes:
            if not session.get('user_id') and not session.get('admin_logged_in'):
                flash('You need to log in first.', 'danger')
                return redirect(url_for('login'))

    return app
 

# Make MongoDB collections accessible throughout the app



def init_admin(app):
    with app.app_context():
        # Add default SQLite admin if not exists
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
            admin_user = User(username='admin', password=hashed_password, role='admin')
            db.session.add(admin_user)
            db.session.commit()

        # Add MongoDB admin if not exists
        if not app.mongo_admins.find_one({"username": "admin"}):
            hashed_password = generate_password_hash('admin1', method='pbkdf2:sha256')
            admin_data = {
                "username": "admin",
                "password": hashed_password
            }
            app.mongo_admins.insert_one(admin_data)

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
