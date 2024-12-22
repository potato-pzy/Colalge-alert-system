from flask import Flask, render_template, Blueprint, request, redirect, url_for
from pymongo import MongoClient
from urllib.parse import quote_plus

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection URI with password URL encoding
password = "mylanchi"  # Replace with your actual password
encoded_password = quote_plus(password)
uri = f"mongodb+srv://tunemusicorg:{encoded_password}@cluster0.3sjfbhk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a MongoDB client instance
client = MongoClient(uri)
db = client['college_alert_system']
calendar_collection = db['calendar']

# Define the blueprint for calendar
calendar_up = Blueprint('calendar', __name__)

# Calendar route within the blueprint (view calendar events)
@calendar_up.route('/calendar')
def calendar():
    # Fetch calendar data from MongoDB
    calendar_events = calendar_collection.find().sort("month", 1)  # Sort by month
    
    # Convert MongoDB cursor to list
    events_list = list(calendar_events)
    
    return render_template('notices/academic_calendar.html', events=events_list)

# Calendar form route (add new calendar event)
@calendar_up.route('/calendar/add', methods=['GET', 'POST'])
def add_calendar_event():
    if request.method == 'POST':
        # Get the form data
        month = request.form['month']
        date = request.form['date']
        description = request.form['description']
        
        # Insert the new calendar event into MongoDB
        new_event = {
            'month': month,
            'events': [{'date': date, 'description': description}]
        }
        
        # Insert the event
        calendar_collection.insert_one(new_event)
        
        return redirect(url_for('calendar.calendar'))  # Redirect back to the calendar view
    
    return render_template('updates/calender.html')  # Display the form for adding an event

# Register the blueprint with the Flask app
app.register_blueprint(calendar_up, url_prefix='/academic/academic-calendar')

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
