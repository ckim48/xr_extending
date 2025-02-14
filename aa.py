from config import firebaseConfig
import pyrebase
firebase = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()
db = firebase.database()
def insert_mock_firebase_data():
    """Adds a comprehensive set of meaningful mock data, including consultations, into Firebase."""
    users = {
        "user1": {"username": "alice@example.com", "gender": "Female", "age": 25},
        "user2": {"username": "bob@example.com", "gender": "Male", "age": 30},
        "user3": {"username": "carol@example.com", "gender": "Female", "age": 22},
        "user4": {"username": "david@example.com", "gender": "Male", "age": 28}
    }

    sentiments = {
        "user1": {"topic": "AI Ethics", "sentiment": "positive"},
        "user2": {"topic": "AI Accuracy", "sentiment": "negative"},
        "user3": {"topic": "Career Guidance", "sentiment": "neutral"},
        "user4": {"topic": "Work Stress", "sentiment": "positive"}
    }

    consultations = {
        "user1": {"content": "Discussed concerns about AI replacing human jobs."},
        "user2": {"content": "Expressed frustration about inaccurate recommendations from the AI."},
        "user3": {"content": "Sought advice on using AI tools for career growth."},
        "user4": {"content": "Talked about how AI could help reduce workload stress."}
    }

    # Insert mock data into Firebase
    db.child("Users").set(users)
    db.child("Sentiments").set(sentiments)
    db.child("Consultations").set(consultations)

    print("Mock data including consultations successfully inserted into Firebase.")

insert_mock_firebase_data()