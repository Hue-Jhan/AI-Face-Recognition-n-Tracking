# AI Face Recognition & Tracking
Face recognition for a Arduino Defense System, includes a hostile face tracking and more functionalities. Based on the haarscade model.  

# 💻Code 

The code detects and trains on faces using a locally stored binary pattern histogram called Haarscade model, made by a German professor. This model uses simple features to recognize patterns in grey-scale images (taken previously) to detect faces, and starts tracking them. It also detects hostile faces if they are not associated with a pre-made user, and starts pointing at them in an ominous way :O 

### 1) Data Collect
The first code starts taking 500 pics and inserts them into the datasets folder, the pics are associated to a user. It detects the faces using the haarscade model after putting the pics in a grey-scale form.

### 2) Training Demo
The second code trains on the previously taken images, more precisely it opens all the previously taken pictures, and for every id (user) it tries to fetch the face unique patterns and stores them into a ```Trainer.yml``` file.

### 3) Tracking
The actual code is more complex.
Every second the camera will take various pictures and send them to the system, which will try to detect faces from them. If a face is associated to a user, it keeps getting tracked until it disappears for 1 second (will explain later why), if a face is unknown for over 2.5 seconds, then it's recognized as a hostile face, and a slighly different kind of tracking will begin, this one takes the face coordinates for nefarious purposes... 😈


# 🤖 AI 

The AI works like this: 

- Every second the camera takes various pictures, if a face is found, the system will then check if the patterns of the face match the ones of any of the known users, this "predictment" has a confidence level which tells us how likely a face is an actual known user's face.

- If the confidence level is above a certain level (it is reccomended to raise this level only after training lots of images) then a timer will start, if the confidence remains high for 2.5 seconds straight (without a single failure) then the system will add that face to a ```permanent faces``` list and won't try to recognize it anymore as it highly likely that the person matches the associated user. 

- The face will then be tracked until it disappears for over 1 second (and gets removed from the list), this is done because the algorithm isnt perfect and sometimes for a split second it wont recognize the face, this is due to a slight change in lighting, position, or whatever, therefore if a face isnt recognize for a short moment, for example if the user turns around, the tracking wont be lost and wont have to restart again.

- If the confidence is below a certain level, the face will simply be named "Unknown", if a face is unknown for over 2.5 seconds it's most likely that the person is an intruder, therefore the face is added to a ```permanent hostile``` list and will receive a heavy punishment. The system will start a sniper-like precise head tracking and fetch the exact coordinates of the face. You can do whatever you want with those coordinates, such as a defense system which will """send""" flying """objects""" towards that intruder.

- The hostile face is lost after 1 second of no detection, meaning the intruder is probably gone.

The code ends if u press "q". You can implement more functions such as security checks, for example if a face is recognized as user X, and you press a certain letter, you can send a command to Arduino which will open a door or something, this can be used as a sort of Face activated door or sum like that, i will use it to create a defense system later in the future
