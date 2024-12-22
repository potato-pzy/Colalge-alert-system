from flask import Blueprint, render_template
from pymongo import MongoClient
from urllib.parse import quote_plus

# MongoDB connection setup
password = "mylanchi"  # Replace with your actual password
encoded_password = quote_plus(password)
uri = f"mongodb+srv://tunemusicorg:{encoded_password}@cluster0.3sjfbhk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(uri)
db = client['college_alerts']  # Replace with your database name
events_collection = db['events']  # Replace with your collection name

# Define the blueprint for events
events_bp = Blueprint('events', __name__)

# Route to fetch and display events
@events_bp.route('/events')
def events():
    # Fetch events from MongoDB and sort by date (optional sorting)
    events_cursor = events_collection.find().sort("date", 1)  # Sort by date in ascending order

    # Convert MongoDB cursor to a list
    events_list = list(events_cursor)

    # Render the events template with fetched events
    return render_template('events/events.html', events=events_list)
