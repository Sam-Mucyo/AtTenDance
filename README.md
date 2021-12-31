
# AtTenDance
Attendance is a web application that can help mark attendance faster and smoothly using facal recognition.

## Procedure to run the app:
--To run this app, you should have python 3 or later, flask, OpenCV, and face_recognition packages installed on your MAC. 

--To start the app, move to the project directory in terminal. 
Type: 
flask run

--Now, copy-paste http://127.0.0.1:5000/ into your favorite internet browser and that's it.

### Required packages

--OS used: macOS Monterey.

To install the basics (VScode, python3, flask, and cs50 libraries) to set up the environment locally, I followed the instruction from CS50 Seminar:
Name: Developing Your Project Locally with VS Code
Link: https://www.youtube.com/watch?v=TZ6c7y8N64k&feature=youtu.be

Once you done installing the basics——VScode, python3, flask, and cs50 libraries––as shown in video, you can start installing packages needed to run this web app. Open VScode and proceed with the following steps: 

1. Install brew by typing: xcode-select --install
2. Install openCV by typing:  pip3 install opencv-contrib-python or install opencv-python-headless
3. Install dlib and face_recognition by running the following commands:
        pip3 install pillow
        pip3 install imutils
        brew install cmake
        brew install dlib
        pip3 install face_recognition

If something goes wrong and need more detailed explaination on installing these packeges, this video might be helpful: https://www.youtube.com/watch?v=70L3By4pci0