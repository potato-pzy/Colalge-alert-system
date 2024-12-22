from flask import Flask, render_template, Blueprint, request, redirect, url_for
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection URI with password URL encoding
password = "mylanchi"  # Replace with your actual password
encoded_password = quote_plus(password)
uri = f"mongodb+srv://tunemusicorg:{encoded_password}@cluster0.3sjfbhk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a MongoDB client instance
client = MongoClient(uri)
db = client['campus_alerts']
notices_collection = db['notices']

# Define the blueprint for notices
notices_up = Blueprint('notice', __name__)

# Notices route within the blueprint (view notices)
@notices_up.route('/notices')
def notices():
    # Fetch notices from MongoDB
    notices_data = notices_collection.find().sort("date_posted", -1)  # Sort by date_posted descending
    
    # Convert MongoDB cursor to list
    notices_list = list(notices_data)
    
    return render_template('notices/notices.html', notices=notices_list)

# Notice form route (add new notice)
@notices_up.route('/notices/add', methods=['GET', 'POST'])
def add_notice():
    if request.method == 'POST':
        # Get the form data
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        date_posted = datetime.now()  # Set the current date and time as the posting date
        
        # Insert the new notice into MongoDB
        new_notice = {
            'title': title,
            'category': category,
            'content': content,
            'date_posted': date_posted
        }
        
        # Insert the notice
        notices_collection.insert_one(new_notice)
        
        return redirect(url_for('notices.notices'))  # Redirect back to the notices view
    
    return render_template('updates/notices.html')  # Display the form for adding a notice

# Register the blueprint with the Flask app
app.register_blueprint(notices_up, url_prefix='/notices')

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
