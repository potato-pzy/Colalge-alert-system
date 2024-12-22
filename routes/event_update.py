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
db = client['college_alerts']
events_collection = db['events']

# Define the blueprint for evnts
events_up = Blueprint('event', __name__)

# Events route within the blueprint (view events)
@events_up.route('/events')
def events():
    # Fetch events data from MongoDB
    events_data = events_collection.find().sort("date", 1)  # Sort by date
    
    # Convert MongoDB cursor to list
    events_list = list(events_data)
    
    return render_template('events/events.html', events=events_list)

# Event form route (add new event)
@events_up.route('/events/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        # Get the form data
        title = request.form['title']
        date = request.form['date']
        description = request.form['description']
        link = request.form['link']
        
        # Insert the new event into MongoDB
        new_event = {
            'title': title,
            'date': date,
            'description': description,
            'link': link
        }
        
        # Insert the event
        events_collection.insert_one(new_event)
        
        return redirect(url_for('events.events'))  # Redirect back to the events view
    
    return render_template('updates/event.html')  # Display the form for adding an event

# Register the blueprint with the Flask app
app.register_blueprint(events_up, url_prefix='/events')

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
