import os
import face_recognition
import cv2
from face_recognition.api import face_encodings
import numpy as np
import json as j
import datetime
import calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from tensorflow.keras.models import load_model
from scipy.spatial import distance
from PIL import Image as im
import time
from playsound import playsound
# import vext

date_time = datetime.datetime.now()
formatted_date = date_time.strftime("%Y-%m-%d")
formatted_time = date_time.strftime("%H:%M:%S")
formatted_full = formatted_date + f"-{formatted_time}"
stripped_time = formatted_time.replace(":" , "")
stripped_date = formatted_date.replace("-" , "")
stripped_full = stripped_date + f"-{stripped_time}"
my_day = calendar.day_name[date_time.weekday()]

pics = []
known_face_encodings = []

def loadmodel():
    print("processing model ...")
    global model
    model = load_model("./saved_model", compile = True)

def encode_known_pics(pics):
    """
    A function that takes employees pics list and encode them
    """
    for pic in pics:
        known_face = face_recognition.load_image_file(pic)
        known_face_encodings.append(face_recognition.face_encodings(known_face)[0])

def open_files():
    """
    Read json file & append the values to lists
    """

    with open('employees.json', 'r') as jd:
        global json_data
        json_data = j.load(jd)
        for p in json_data:
            pics.append(p["photos"])
        encode_known_pics(pics) 

loadmodel()
open_files()

def employee(index):
    """
    A function that takes an index and return the employee info
    """
    info = json_data[index]
    send_email(info, formatted_full , my_day)

def send_email(info = None, f_full="" , day=""):

    with open(cap_frame_name, 'rb') as f:
        img_data = f.read()
        f.close()
    
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login("pypandas.catcher@gmail.com" , "kzmclxljulmpvaxg")

    calling = "Mr"
    gend = "his"
    msg = MIMEMultipart()
    msg['Subject'] = 'No Mask Warning'
    
    if info != None:

        if info["Gender"] == "female": 
            calling = "Mrs"
            gend = "her"
    
        body = MIMEText(f'''      Dear esteemed security department, 
        Our system detected {calling}. {info["Name"]}
        who is not wearing a mask at {f_full} on {day}, 
        please check {gend} attached photo below''')

    else: 

        body = MIMEText(f'''      Dear esteemed security department, 
    Our system detected a visitor who is not wearing a mask at {f_full}, 
    please check attached photo below.''')
    
    msg.attach(body)
    image = MIMEImage(img_data, name=os.path.basename(cap_frame_name))
    msg.attach(image)
    s.sendmail(
        'pypandas.catcher@gmail.com',
        'pypandas.mask.catcher@gmail.com', 
        msg.as_string()
    )
    s.quit()
    print("EMAIL HAS BEEN SENT!") # should fire when email sent succesfully 

def recognize_face(cap_frame):
    """
    takes a list of encoded pictures and compare them with the incoming frame from the video
    to recognize if he/she was an employee or not.
    """
    # read dataset file, encoding images and append to list 'known_face_encodings'

    face_from_cam = face_recognition.load_image_file(cap_frame)
    try:
        
        face_from_cam_encodings = face_recognition.face_encodings(face_from_cam)[0]
        cout = 0
        for face in known_face_encodings:

            results = face_recognition.compare_faces([face], face_from_cam_encodings)
            if results[0] == True:
                employee(cout)
                break
            cout += 1
        if results[0] == False:
            send_email(None, formatted_full , my_day)
        return "Yes face"

    except IndexError:
        print("No faces found")
        return "No face"

def detect_mask(frame):
    """
    A function to detect if a person is wearing a mask or not
    """
    face_model = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
    faces = face_model.detectMultiScale(frame,scaleFactor=1.1, minNeighbors=4)

    if len(faces) >= 1:

        (top,y,bottom,left) = faces[0]
        crop = frame[y:y+left,top:top+bottom]
        crop = cv2.resize(crop,(128,128), fx=0.5, fy=0.5)
        crop = np.reshape(crop,[1,128,128,3])/255.0
        mask_result = model.predict(crop)

        if mask_result > 0.5 :
            global cap_frame_name
            cap_frame_name = f"./assets/{stripped_full}.jpg"
            cv2.imwrite(cap_frame_name, frame)

            is_face = recognize_face(cap_frame_name)
            if is_face == "Yes face":
                red_alert()
    
            return True

        print('Welcome')
        return False

    else:
        return False

def red_alert():
    try: 

        for i in range (0,3):
            playsound('./sounds/alert.mp3')

    except ModuleNotFoundError: 
        return 'Not wearing a mask alert'

def draw_rectangle(frame,color,label):
    pass

def access_cam():
    try:
        process_this_frame = True
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            raise IOError("Cannot open webcam")

        start = input('do you want to start camera?')
        if start == 'Y' or 'y':            
            while True:
                ret, frame = cap.read()
                frame = cv2.flip(frame,1)
                frame = cv2.resize(frame,(900,700))
                cv2.imshow('Pypandas-live', frame)
                detect_mask(frame) # number 0-1 # True if there's a face and not wearing a mask
                # time.sleep(5)
                c = cv2.waitKey(1)
                if c == ord('b'): ## press b to exit 
                    break

        cap.release()
        cv2.destroyAllWindows()
    except:
        quit()

access_cam()





# def draw_frame(frame,color,label):
#     for (top,right,bottom,left) in frame:
#         top *= 2
#         right *= 2
#         left *= 2
#         bottom *= 2
#         cv2.rectangle(frame,(left,top),(right, bottom),color,1)
#         cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
#         font = cv2.FONT_HERSHEY_DUPLEX
#         cv2.putText(frame, label, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


