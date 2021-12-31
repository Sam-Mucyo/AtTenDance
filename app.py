from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, Response, jsonify
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

import cv2
import face_recognition
import pickle
from datetime import datetime
from myfunctions import VideoCamera, known_people, who_is_this, apology


app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///attendance.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Declaring global variables
global new_face_id, is_known, attendance, registering
attendance = False
registering = False
is_known = False

@app.route('/')
def index():
    # Get the current time and date
    date = datetime.now().date()
    time = datetime.now().strftime("%H:%M:%S")

    rows = db.execute("SELECT * FROM people, attendance WHERE people.id = attendance.person_id AND date = ? ORDER BY time", date)

    return render_template('index.html', attendees=rows, date=date)

@app.route('/known')
def known():
    # Get the current time and date
    date = datetime.now().date()
    
    rows = db.execute("SELECT * FROM people")

    return render_template('list.html', people=rows, date=date)

@app.route('/remove', methods=["GET", "POST"])
def remove():

    if request.method == "POST":
        # Are inputs empty
        name = request.form.get("name");
        if not name:
            return apology("Missing Name", 400)
        
        f_name = name.split(" ")[0]
        l_name = name.split(" ")[1]

        row = db.execute("SELECT * FROM people WHERE first_name = ? AND last_name = ?", f_name, l_name)
        if not row:
            return apology("Sorry, we couldn't find that person.")

        id = row[0]["id"]

        db.execute("DELETE FROM attendance WHERE person_id = ?", id)
        db.execute("DELETE FROM people WHERE id = ?", id)
    
        return redirect("/")
    
    else:
        rows = db.execute("SELECT * FROM people")
        return render_template('remove.html', people=rows)

# ---------- Registering a person -------

@app.route("/register", methods=["GET", "POST"])
def register():
    global new_face_id, attendance, registering, is_known
    attendance=False
    registering=True
    """Register user"""
    if request.method == "POST":

        f_name = request.form.get("f_name");
        l_name = request.form.get("l_name");
        contact = request.form.get("contact")

        # Ensure username is not blank
        if not f_name or not l_name:
            return apology("First name and Last name are required")

        # Ensure username is not blank
        if not contact:
            return apology("Please input your phone number", 400) 
        
        # Ensure contact has number type
        if not contact.isdigit() or int(contact) < 0 :
            return apology("Check contact format: No parenthesis or dashes", 400)
        
        # Ensure a Face was detected. b'\x80\x04]\x94.' represents an empty BLOB data
        if new_face_id == b'\x80\x04]\x94.':
            return apology("Sorry, No Face was detected ", 400)

        # Ensure the Face is not already in database
        if is_known:
            is_known = False
            return apology ("Sorry, we already know this person (:")

        db.execute("INSERT INTO people (first_name, last_name, contact, face_id) VALUES (?, ?, ?, ?)", f_name, l_name, contact, new_face_id)

        flash("Registration done successfully!")
        return redirect("/")

    else:
        return render_template("register.html")




def known(frame):
    global new_face_id, attendance, registering, is_known

    # Get the facial encodings of the user   
    img = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(img)
    encodesCurFrame = face_recognition.face_encodings(img, facesCurFrame)
        
    # Blob the facial encodings to be saved in the database as BLOB
    new_face_id = pickle.dumps(list(encodesCurFrame))

    # Check if the face is not already in database
    success, ids, facial_encodings = known_people()
    
    # If we don't know anyone yet 
    if not success:
        is_known = False
    else:
    # Check if that person is already known
        for target_face, faceLoc in zip(encodesCurFrame, facesCurFrame):
            # Keep checking if the person is known
            known, id, name = who_is_this(ids, facial_encodings, target_face) 
            is_known = known

# ---------- Attendance -------

@app.route("/attendance", methods=["GET"])
def attendance():
    global new_face_id, attendance, registering
    attendance=True
    registering=False

    return render_template('attendance.html')

             
@app.route('/video_feed')
def video_feed():
    video_stream = VideoCamera()
    return Response(generate_frame(video_stream),
            mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_frame(camera):
    while True:
        frame = camera.get_frame()        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
