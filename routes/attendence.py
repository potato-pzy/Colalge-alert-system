from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
from functools import wraps

# Create a Blueprint for attendance
attendance_bp = Blueprint('attendance', __name__)

# MongoDB connection
password = "mylanchi"  # Replace with your actual password
encoded_password = quote_plus(password)
uri = f"mongodb+srv://tunemusicorg:{encoded_password}@cluster0.3sjfbhk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client['college_alert_system']  # Replace with your desired database name
attendance_collection = db['attendance']  # Collection for attendance records
users_collection = db['users']  # Collection for user data (students)
admins_collection = db['admins']  # Collection for admin data

# Decorator to check if the user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin access required. Please log in as an admin.', 'danger')
            return redirect(url_for('admin_login'))  # Redirect to the admin login page
        return f(*args, **kwargs)
    return decorated_function

# Route for students to mark attendance
@attendance_bp.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        print("ivde aanu ")
        return redirect(url_for('login'))

    if request.method == 'POST':
        course = request.form.get('course')
        status = request.form.get('status')  # 'Present' or 'Absent'
        student_id = session['user_id']

        # Validate form data
        if not course or not status:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('attendance.mark_attendance'))

        if status not in ['Present', 'Absent']:
            flash('Invalid status. Please select "Present" or "Absent".', 'danger')
            return redirect(url_for('attendance.mark_attendance'))

        # Get student details from MongoDB
        student = users_collection.find_one({"_id": student_id})
        if not student:
            flash('Student not found.', 'danger')
            return redirect(url_for('attendance.mark_attendance'))

        # Save attendance record to MongoDB
        try:
            attendance_record = {
                "student_id": student_id,
                "student_name": student['username'],
                "course": course,
                "status": status,
                "date": datetime.utcnow()
            }
            attendance_collection.insert_one(attendance_record)
            flash('Attendance marked successfully!', 'success')
        except Exception as e:
            flash('An error occurred while marking attendance. Please try again.', 'danger')
            print(f"Error: {e}")

        return redirect(url_for('attendance.mark_attendance'))

    # Render the form for marking attendance
    return render_template('attendance/mark_attendance.html')

# Route for admins to view attendance
@attendance_bp.route('/view_attendance', methods=['GET'])
@admin_required
def view_attendance():
    course = request.args.get('course', default='Subject 1')  # Default to Subject 1
    attendance_records = attendance_collection.find({"course": course}).sort("date", -1)  # Sort by date descending

    # Convert to list
    attendance_list = list(attendance_records)

    return render_template('attendance/view_attendance.html', attendance_records=attendance_list, course=course)