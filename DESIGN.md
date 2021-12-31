## Why BLOB instead of saving images? 

The first approach I used making this web app was saving registered user's images in database. And while marking attendance, the program would just get facial enconding from the camera and compares it to the one from database. Since the database would be having images of registered user, the program needed to first manipulate those images and get facial encondings before comparing faces. And this slowed down the performance of web significantly. 

To solve that issue, I decided to store the facial encodings in my database (instead of images) so that the program would not need to find facial encodings of every users (a process that take some time) every time we are marking attendance. Intuitively, this new approach had speed up the performace. But it turned out that facial encodings are stored as a list of important measurements on the face — like the color and size and slant of eyes, the gap between eyebrows, etc. This type couldn't be stored plainly in database table, so I had to first turn those encondings into a BLOB type so that I can store it into my database. 

## pickle 
This is a function that I import in both my python files to help me to solve that problem explained above. It basically helps me to turn the facial encondings into a BLOB type to be stored in my database. 
        By calling pickle.dumps(facial_encondings), I can get the encondings in BLOB type.
        pickle.loads(): this takes a blobled variable and returns the orginal content, in this case facial_encondings. 


## required packages
- OpenCV or cv2 helps to open webcam and manipulate images, videos, or frames from the camera. You can see 
- face_recognition helps to detect where the faces are in a given image or frame (by using function face_locations). Second it helps to get facial encondings of that face which can be used later to compare with other facial encodings to find a match. 
        
        Important functions from face_recognition library, I used in myfunctions.py         
        - face_encodings() returns the encodings of faces in a given frame or image.
        - compare_faces(known_faces, target_face) that takes a list of known encodings and the encodings of the face your want to compare. The function returns a list of boolean with the same length as the list of known_faces. In that returned list, the index of "True" will be the same as the index of the known face from the known_faces list that matches with the target.


## templates/
In templates, basically most tags might look familiar, but I want to point out this one before going to back-end. 

open attendance.html and register.html and see how I am opening user's camera by using image table with the source as src="{{ url_for('video_feed') }}". This will take to the url in app.py, with route /video_feed. This route returns frames from Camera to our html file.


## myfunctions.py
Open up myfunctions.py to take a look at some important functions defined there. 

1. First thing is a class VideoCamera, which will open camera using cv2 and also have a method get_frame() that reads what cv2 sees, line 24, and returns it as bytes to be shown on the html page. The most interesting and cool part of it is how it's calling recognize() function if we are marking attendance and known() function when were registering the user. 

2. Recognize(frame): This is probally one of the functions that was hard for me to implement, as it required understand how all the packages works and combine them in a way that does the integral part of my project. 

First, see how get the ids and facial encodings of known people by calling a function known_people(), which I defined bellow that one on line 79. If that fails, which means no one in database yet, I set the name of person to "unknown".

Secondly, I use cv2 and face_recognition libraries to get the encodes of a person the camera is seeing. Once we have that, we call a function who_is_this() defined bellow that one too. The function basically returns the id and name of the person if there is a match, otherwise the boolean variable "known" as False. 

Thirdly, if known is True, we just mark the attendance into our database in attendance table. 

Lastly, I use cv2 library to draw a rectangle and the name of person on the screen. 


## app.py
Open up app.py. 

# Imports 
The first part is importing a bunch of libraries and modules including CS50's SQL module and others to help me catch some errors as we did in finance pset. The second part of importing, imports the required libraries explained above. But also another python library "pickle", more on this library is explained above.

# Global variables on line 26:
    
1. new_face_id: 
    type: BLOB to store the facial encodings of registered user to be saved in data base. 
This will be updated automatically when the user is being registered. I decided to make it global, because unlike other input we get get from POST method, facial encodings is something, the user doesn't input as text, number, password, etc. And I needed to get it in real time. Additionally, my other functions need to have access to that variable to make sure that the person who is being registered is not already in database.

2. is_known

This is a boolean function that will make the app know if the user is known or not, accord to faces of registered people. I have decided to make it globe because, it needs to be used by more than functions in different routes. For example before registering to make sure the user is new. And also when marking attendance to know if who the camera is seeing is known or not.

    See how on line 122, this variable is updated a function known(frame)
    - This function takes a what camera sees (frame) as input and then, on line 144, calls a function who_is_this() which is defined in myfunctions.py. 

3. and 3. attendante and registering 
These are two boolean variables will help the program know if the camera is being opened to mark attendance or to register a new user. 
