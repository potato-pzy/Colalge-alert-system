from pymongo import MongoClient
from urllib.parse import quote_plus

# Encode the password to handle special characters
password = "mylanchi"  # Replace with your actual password
encoded_password = quote_plus(password)

# MongoDB connection URI
uri = f"mongodb+srv://tunemusicorg:{encoded_password}@cluster0.3sjfbhk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a client to connect to MongoDB
client = MongoClient(uri)

# Define the database and collection
db = client['college_alert_system']  #Replace with your desired database name
collection = db['calendar']  # Replace with your desired collection name

# Academic calendar data
calendar_events = [
    {
        'month': 'January',
        'events': [
            {'date': '5th', 'description': 'Spring Semester Begins'},
            {'date': '15th', 'description': 'Last Day for Course Add/Drop'},
            {'date': '20th', 'description': 'Mid-term Exam Registration Opens'}
        ]
    },
    {
        'month': 'February',
        'events': [
            {'date': '10th', 'description': 'Midterm Examinations'},
            {'date': '14th', 'description': 'College Cultural Festival'},
            {'date': '28th', 'description': 'Research Paper Submission Deadline'}
        ]
    },
    {
        'month': 'March',
        'events': [
            {'date': '5th', 'description': 'Annual Sports Meet'},
            {'date': '15th', 'description': 'Internship Fair'},
            {'date': '25th', 'description': 'Final Semester Project Presentations'}
        ]
    }
]

# Insert data into the collection
try:
    # Insert the calendar events into the collection
    result = collection.insert_many(calendar_events)
    print(f"Inserted {len(result.inserted_ids)} documents into the collection.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the MongoDB connection
    client.close()
