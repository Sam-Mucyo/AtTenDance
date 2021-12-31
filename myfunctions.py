import cv2
import face_recognition
import pickle
import numpy as np
from datetime import datetime
from flask import render_template
import app

from cs50 import SQL


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///attendance.db")


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()        

    def get_frame(self):
        success, frame = self.video.read()

        if app.attendance:
            recognize(frame)

        if app.registering:
            # call known function that would make global variable is_known True or False. 
            # This will help us not save same person twice in a database. 
            app.known(frame)

        ret, jpeg = cv2.imencode('.jpg', frame)

        return jpeg.tobytes()


def recognize(frame):

    # Get the ids and facial encodings of known people
    success, ids, encoded_faces = known_people()
    
    if not success:
        name = "unknown"

    # Encode the face from webcam
    imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        # Get the location of the face in a webcam
        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

        # If we already know some people, try finding a match
        if success:
            known, person_id, name = who_is_this(ids, encoded_faces, encodeFace)
            
            #----- Marking Attendance, if the person is known
            if known:
                # Get the current time and date
                date = datetime.now().date()
                time = datetime.now().strftime("%I:%M %p")

                # Avoid saving duplicates on the same day
                db.execute("DELETE FROM attendance WHERE person_id = ? AND date = ?", person_id, date)
                # Record the attendance
                db.execute("INSERT INTO attendance (person_id, date, time) VALUES (?, ?, ?)", person_id, date, time)

        # Draw a rectangle on a face, showing the name of a person. If there is none, name would be "Unknown"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name.upper(), (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)


def known_people():
    ids = []
    encoded_faces = []
    success = False
    # Query people table to get ids and facial encodings of known people.
    rows = db.execute("SELECT id, face_id FROM people")

    # If there are no known people, 
    if not rows:
        pass
    
    else:
        success = True
        for row in rows:
            ids.append(row["id"])
            facial_encoding = pickle.loads(row["face_id"])
            encoded_faces.append(facial_encoding[0])

    return(success, ids, encoded_faces)


def who_is_this(ids, known_faces, target_face):

    # Compare the new face to the current known faces. This gives a list of boolean (True or False), where True means a match
    matches = face_recognition.compare_faces(known_faces, target_face, tolerance=0.45)

    # Get the index of someone from database with a matching face. 
    try:
        index = matches.index(True)
        person_id = ids[index]

    # if there is none
    except:
        known = False
        person_id = 0
        name = "Unknown"
    
    if person_id:
        known = True
        row = db.execute("SELECT * FROM people WHERE id = ?", person_id)
        if not row:
            pass
        name = row[0]["last_name"] + " " + row[0]["first_name"]

    return (known, person_id, name)



def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

