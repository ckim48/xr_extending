from click import command
from flask import Flask, render_template, request, redirect, url_for, flash, session
import speech_recognition as sr
import sqlite3
import pyrebase
from config import firebaseConfig

from audiototext import audio_to_text, extract_sentiments, extract_keywords

from pandas.core.apply import reconstruct_func

# session = { "username" : "hongjuwang437@gmail.com" }
# after logout --> session = {}

app = Flask(__name__)
app.secret_key = "abc"

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()



#Helper function
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
    if 'username' in session: #user is logged in
        isLogin = True
    return render_template('index.html', isLogin=isLogin)

@app.route('/database')
def database():
    isLogin = False
    if 'username' in session:
        isLogin = True
    conn = sqlite3.connect('static/database.db')
    cursor = conn.cursor()
    command = "SELECT email, gender, age, country FROM Users;"
    cursor.execute(command)
    result = cursor.fetchall() #{ (Ju-Wang Hong, None, None), (hongjuwang437@gmail.com, None, None)
    users_index = [i for i in range(1, len(result)+1)]
    users_username = []
    users_gender = []
    users_age = []
    users_country = []

    for user in result:
        users_username.append(user[0])
        users_gender.append((user[1]))
        users_age.append((user[2]))
        users_country.append(user[3])

    return render_template('database.html',num_users = len(result) ,isLogin=isLogin, indices = users_index, usernames = users_username, genders = users_gender, ages = users_age, countries = users_country)



@app.route('/login',methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["email"]
        password = request.form["password"]
        print(username)
        print(password)
        conn = sqlite3.connect('static/database.db')
        cursor = conn.cursor()
        command = "SELECT password FROM Users WHERE email = (?)"
        cursor.execute(command, (username, ))
        password_db = cursor.fetchone() # password --> when username is in DB or None --> When username is not in DB
        if password_db is None:
            flash("Username or password is wrong")
            return render_template('login.html')

        if password_db[0] != None and password_db[0] == password:
            session["username"] = username
            log_activity(username)

            return redirect(url_for('index'))
        else:
            flash("Username or password is wrong")
            return render_template('login.html')
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
        country = request.form["country"]

        # Connect to the database
        conn = sqlite3.connect('static/database.db')
        cursor = conn.cursor() # cursor will execute SQL command(code) to the DB

        command = "SELECT password FROM Users WHERE email = ?;"
        cursor.execute(command,(username,))
        result = cursor.fetchone()
        if result is None: # when the username is not in our DB
            command = "INSERT INTO Users(email, password, fullname, gender, age, country) VALUES (?,?,?,?,?,?);"
            cursor.execute(command, (username, password, fullname, gender, age, country))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        else: # when the username(email) is already existed
            flash('Email(username) already exists')
            return render_template('register.html')

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
              ORDER BY login_count DESC
              """
    cursor.execute(command)
    login_date = cursor.fetcall()
    conn.close()
    return ""


if __name__ == '__main__':
    db.child("test").push("test123")
    app.run(debug=True)
