from flask import Flask,Blueprint, render_template
from pymongo import MongoClient
from urllib.parse import quote_plus

app = Flask(__name__)

academic = Blueprint('academic', __name__)

password = "mylanchi"  # Replace with your actual password
encoded_password = quote_plus(password)
uri = f"mongodb+srv://tunemusicorg:{encoded_password}@cluster0.3sjfbhk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client['college_alert_system']  #Replace with your desired database name
collection = db['calendar']


@academic.route('/academic-calendar')
def academic_calendar():
    calendar_events = collection.find().sort("month", 1)  # Sort by month alphabetically
    
    # Convert to list
    calendar_list = list(calendar_events)
    
    return render_template('notices/academic_calendar.html', calendar_events=calendar_list)

if __name__ == '__main__':
    app.run(debug=True)