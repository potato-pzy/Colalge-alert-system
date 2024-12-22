from flask import Flask, render_template, Blueprint
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
db = client['campus_alerts']
notices_collection = db['notices']

# Define the blueprint for notices
notices_bp = Blueprint('notices', __name__)

# Notice route within the blueprint
@notices_bp.route('/notices')
def notices():
    # Fetch notices from MongoDB
    notices = notices_collection.find().sort("date_posted", -1)  # Sort by date_posted in descending order
    
    # Convert MongoDB cursor to list
    notices_list = list(notices)
    
    return render_template('notices/notices.html', notices=notices_list)

# Register the blueprint with the Flask app
app.register_blueprint(notices_bp, url_prefix='/notices')

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
