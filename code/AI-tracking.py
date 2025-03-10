import cv2
import time
import serial 

# PORT = "COM3"   these 3 lines are used to connect to arduino, you can then implement sensor n stuff to do whatever you want when a user or an intruder is recognized : ) 
# baud_rate = 57600
# arduino = serial.Serial(PORT, baud_rate)
video = cv2.VideoCapture(0)
cascade_path = "models/haarcascade_frontalface_default.xml"
facedetect = cv2.CascadeClassifier(cascade_path)
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("models/Trainer.yml")
imgBackground = cv2.imread("models/background.png") 
name_list = ["", " User1", " User2"]
# count = 0
# count2 = 0
permanent_faces = {}
permanent_hostile = {}
hostile_timer = {}
face_timer = {}
unrecognized_timer = {}
recognized_timer = {}

def doorAutomate(val):
    if val == 0:
        arduino.write(b"OPEN\n") # response to face recognized
    elif val == 1:
        arduino.write(b"CLOSE\n")

def hostileTracking(x, y, w, h):
    face_center_x, face_center_y = x + w // 2, y + h // 2
    frame_width = frame.shape[1]
    # cv2.rectangle(frame, (x, y), (x + w+10, y + h+10), (0, 0, 255), 2)
    cv2.circle(frame, (face_center_x, face_center_y), 80, (0, 0, 255), 2)
    cv2.circle(frame, (face_center_x, face_center_y), 15, (0, 0, 255), cv2.FILLED)
    cv2.line(frame, (0, face_center_y), (frame.shape[1], face_center_y), (0, 0, 0), 2)
    cv2.line(frame, (face_center_x, frame.shape[0]), (face_center_x, 0), (0, 0, 0), 2)
    cv2.putText(frame, str((face_center_x, face_center_y)), (frame_width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, "   HOSTILE", (x+5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(frame, "TARGET LOCKED", (850, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    print(f"Tracking hostile face at {x}, {y}, {w}, {h}")

def tracking(name, x, y, w, h):
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
    cv2.rectangle(frame, (x, y - 40), (x + w, y), (0, 255, 255), 2)
    cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

def permanentTracking(name, x, y, w, h):
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.rectangle(frame, (x, y - 40), (x + w, y), (0, 255, 0), -1)
    cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    print(f"Tracking {name}'s face...")

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    detected_faces = set()

    if len(faces) == 0:
        print("No face detected")

    for (x, y, w, h) in faces:
        serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
        detected_faces.add(serial)
        name = name_list[serial]

        if serial in permanent_faces:  # Track permanent faces
            permanentTracking(name, x, y, w, h)
            face_timer[serial] = time.time()

        elif serial in permanent_hostile:
            hostileTracking(x, y, w, h)
            hostile_timer[serial] = time.time()

        elif conf > 55:  # If face recognized and confidence is high
            tracking(name, x, y, w, h)
            # print("yessss")
            face_timer[serial] = time.time()
            if serial not in recognized_timer:
                recognized_timer[serial] = time.time()
            if time.time() - recognized_timer[serial] > 2.5:
                if serial not in permanent_faces:
                    permanent_faces[serial] = (x, y, w, h)  # Store face for permanent tracking so if a face inst recognized for a split second it doesnt forget its association witht the user
                    print(f" {name_list[serial]} recognized for more than 2.5 seconds, added to permanent.")

        else:
            tracking("  Unknown", x, y, w, h)
            print("No")
            hostile_timer[serial] = time.time() # updates the time constantly
            if serial not in unrecognized_timer:
                unrecognized_timer[serial] = time.time()  # Start tracking the time
            if time.time() - unrecognized_timer[serial] > 2.5: # Check if the unrecognized face has been in this state for more than 3 seconds
                if serial not in permanent_hostile:
                    permanent_hostile[serial] = (x, y, w, h) # adds it to hostile faces
                    print("Hostile face detected more than 2.5 seconds, started visual tracking")


    for serial in list(unrecognized_timer.keys()):
        if serial not in detected_faces:  # if the unknown face has disappeared, reset timer
            del unrecognized_timer[serial]

    for serial in list(recognized_timer.keys()):
        if serial not in detected_faces:  # if the face is no longer detected, reset recognized timer
            del recognized_timer[serial]

    for serial in list(permanent_faces.keys()):
        if serial not in detected_faces:
            if time.time() - face_timer[serial] > 1:  # 1 second of no detection means the person is most likely gone
                del permanent_faces[serial]
                del face_timer[serial]  # Remove the timer as well
                count = 0
                print(f"Removed {name_list[serial]} from permanent faces due to inactivity.")
    
    for serial in list(permanent_hostile.keys()):
        if serial not in detected_faces:
            if time.time() - hostile_timer[serial] > 1:  # 1 second of no detection
                del permanent_hostile[serial]
                del hostile_timer[serial]  # Remove the timer as well
                count2 = 0
                print(f"Removed hostile from permanent hostile due to inactivity.")

    frame = cv2.resize(frame, (640, 480))
    imgBackground[162:162 + 480, 55:55 + 640] = frame # stolen from an indian guy xd
    cv2.imshow("Frame", imgBackground)
    key = cv2.waitKey(1) # quit by pressing "q", you can implement any function with arduino, for example if a certain user is recognized and u press "x", a door opens
    if key == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
