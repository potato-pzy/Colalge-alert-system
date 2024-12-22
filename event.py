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

# Data to insert into MongoDB
events = [
    {
        "title": "Technical Symposium 2024",
        "date": "2024-03-15",
        "description": "Annual technical symposium featuring workshops, competitions, and guest lectures.",
        "link": "#"
    },
    {
        "title": "Cultural Fest",
        "date": "2024-04-05 to 2024-04-07",
        "description": "Three days of music, dance, and cultural celebrations.",
        "link": "#"
    },
    {
        "title": "Workshop on Blockchain",
        "date": "2024-03-20",
        "description": "Learn about blockchain technology and its applications.",
        "link": "#"
    }
]

# Insert the event data into the MongoDB collection
result = events_collection.insert_many(events)

# Output the result of the insertion
print(f"Inserted {len(result.inserted_ids)} documents into the 'events' collection.")
