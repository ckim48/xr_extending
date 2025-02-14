from typing import OrderedDict

from flask import Flask, render_template, request, redirect, url_for, flash, session
import speech_recognition as sr
import sqlite3
from audiototext import audio_to_text, extract_keywords,extract_sentiments,count_word_frequency
import pyrebase
from config import firebaseConfig
from openai import OpenAI




# after login--> session = {"username": "scott@logncoding.com"}
# after logout --> session = {}

app = Flask(__name__)
app.secret_key = "abc"

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

data ={"user1": {"topic":"relationship","sentiment":"positive"} , "user2": {"topic":"academic","sentiment":"negative"}}

def get_firebase_data():
    users = db.child("Users").get().val()
    sentiments = db.child("Sentiments").get().val()
    consultation = db.child("Consultations").get().val()
    from collections import OrderedDict
    final_data = OrderedDict()
    return users, sentiments, consultation


def get_summary():
    data1 , data2, data3 = get_firebase_data()
    prompt = f"""
        Here is the data that we have:
        {data1}, {data2}, and {data3} \n\n
        Focus on \n
        - Common consultation topics \n
        - Sentiment trends (positive, negative, neutral) \n
        - Insights into user experiences and concerns regrading the AI consultatnt \n
        - Recommendation for improvement of VR based AI consulting app 
    """
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages = [{'role': 'user', "content":prompt}],
        temperature = 0
    )
    result = response.choices[0].message.content.strip()
    return result

def retreive_audio(filename,download_path):
    try:
        storage = firebase.storage()
        storage.child("audio_files/{}".format(filename)).download(download_path)
        files = storage.child("audio_files").list_files()
        for file in files:
            file_name = file.name
            download_folder = "audio_files"
            download_path = f"{download_folder}/{filename}"
            file.download(download_path)
        print("Successfully Downloaded")
    except Exception as e:
        print(f"Error while downloading: {e}")

# Helper function
def log_activity(email, activity):
    conn = sqlite3.connect('static/database.db')
    cursor = conn.cursor()
    command = "INSERT INTO UserActivity (email, activity) VALUES (?, ?);"
    cursor.execute(command, (email, activity))
    conn.commit()
    conn.close()


@app.route('/')
def index():
    isLogin = False
    if 'username' in session: # user is logged in
        isLogin = True
    return render_template('index.html', isLogin=isLogin)

@app.route('/database')
def database():
    isLogin = False
    if 'username' in session:
        isLogin = True
    conn = sqlite3.connect('static/database.db')
    cursor = conn.cursor()
    command = "SELECT email, gender, age FROM Users;"
    cursor.execute(command)
    result = cursor.fetchall() #[ (scott, None, None), (test@gmail.com, None, None), .. ]
    users_index = [i for i in range(1, len(result)+1)]
    users_username = [] # [scott, test@gmail.com, ...]
    users_gender = []
    users_age = []
    summary = get_summary()
    for user in result:
        users_username.append(user[0])
        users_gender.append(user[1])
        users_age.append(user[2])

    return render_template('database.html', summary=summary, num_users = len(result), isLogin=isLogin, indices = users_index, usernames =  users_username, genders = users_gender, ages = users_age)

@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["email"] # what user put for his/her username
        password = request.form["password"] # what user put for his/her password
        try:
            user = auth.sign_in_with_email_and_password(username,password)
            session["username"] = username
            return redirect(url_for('index'))
        except Exception as e:
            flash("Invalid email or password")
            return render_template('login.html')
        # print(username)
        # print(password)
        # conn = sqlite3.connect('static/database.db')
        # cursor = conn.cursor()
        # command = "SELECT password FROM Users WHERE email = (?)"
        # cursor.execute(command,(username, ))
        # password_db = cursor.fetchone() # password --> when username is in DB or None --> when username is not in db
        #
        # if password_db is None:
        #     flash("Username or password is wrong")
        #     return render_template('login.html')
        #
        # if password_db[0] != None and password_db[0] == password: # when user put the correct information for login
        #     session["username"] = username
        #     log_activity(username)
        #     return redirect(url_for('index'))
        # else:
        #     flash("Username or password is wrong")
        #     return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/register', methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["email"]
        password = request.form["password"]
        fullname = request.form["fullname"]
        gender = request.form["gender"]
        age = request.form["age"]
        try:
            auth.create_user_with_email_and_password(username, password)
            db.child("Users").push({
                "username":username,
                "fullname":fullname,
                "gender": gender,
                "age": age
            })
            return redirect(url_for('login'))
        except Exception as e:
            flash("Error Creating Account")
            print(e)
            return render_template('register.html')


        # Connect to the database
        # conn = sqlite3.connect('static/database.db')
        # cursor = conn.cursor() # cursor will execute SQL command(code) to the DB
        # command = "SELECT password FROM Users WHERE email = ?;"
        # cursor.execute(command, (username,))
        # result = cursor.fetchone()
        # if result is None:  # when the username is not in our DB
        #     command = "INSERT INTO Users(email, password, fullname, gender, age) VALUES (?,?,?,?,?);"
        #     cursor.execute(command, (username,password, fullname,gender,age,))
        #     conn.commit()
        #     conn.close()
        #     return redirect(url_for('login'))
        # else: # when the username(email) is already existed
        #     flash('Email(usrname) already exists')
        #     return render_template('register.html')



    else:
        return render_template('register.html')
@app.route('/logout', methods = ["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user-login-frequency')
def user_login_frequency():
    conn = sqlite3.connect('static/database.db')
    cursor = conn.cursor()
    command = """
              SELECT email, COUNT(*) as login_count From UserActivity
              WHERE activity = 'login'
              GROUP BY email
              ORDER BY login_count DESC;
              """
    cursor.execute(command)
    login_date = cursor.fetcall()
    conn.close()
    return ""


if __name__ == '__main__':
    # db.child("test").push("test123")
    app.run(debug=True, port = 8000)
    # print(get_summary())