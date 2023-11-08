import pyttsx3

import numpy as np
import cv2
import os
import face_recognition
from datetime import datetime, date, timedelta


studImg = []
studNames = []

path = r"C:\SRP\data"
print(path)
studImageList = os.listdir(path)

for file in studImageList:
    curStudImg = cv2.imread(f'{path}/{file}')
    studImg.append(curStudImg)
    studNames.append(os.path.splitext(file)[0])


def findEncodings(studImg):
    encodeList = []
    print(len(studImg))
    for img in studImg:
        # print(img)
        if (img is not None):
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        if len(encode) > 0:
            encodeList.append(encode)
    return encodeList


def markAttendance(name):
    with open('Attendance/Attendance.csv', 'a+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            today = date.today()
            d2 = today.strftime("%B %d, %Y")
            f.writelines(f'\n{name},{dtString},{d2}')


encodedStudImg = findEncodings(studImg)
Vcap = cv2.VideoCapture(0)
past = ""

while True:
    success, frame = Vcap.read()
    cv2.imshow("show", frame)
    sFrame = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    sFrame = cv2.cvtColor(sFrame, cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(sFrame) #rect
    encodedCurFrame = face_recognition.face_encodings(sFrame, facesCurFrame) #rect faace encodin
    for encodedFace, faceLoc in zip(encodedCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodedStudImg, encodedFace, tolerance=0.3)
        distance = face_recognition.face_distance(encodedStudImg, encodedFace)
        matchIndex = np.argmin(distance)

        if matches[matchIndex]:
            name = studNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 + 4, x2 + 4, y2 + 4, x1 + 4
            cv2.rectangle(frame, (x1*4, y1*4), (x2*4, y2*4), (0, 255, 0), 2)
            cv2.rectangle(frame, (x1*4, (y2 - 3)*4), (x2*4, y2*4), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, ((x1 + 6)*4, (y2 - 6)*4), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            list2 = []
            list1 = []
            with open("Attendance/Attendance.csv") as f:
                if os.path.getsize("Attendance/Attendance.csv") == 0:
                    markAttendance(name)
                else:
                    for row in f:
                        print(row)
                        list2.append(row.split(",")[0])
                        list1.append(row.split(",")[1])
                    if name in list2:
                        index = list2.index(name)
                        t1 = list1[index]
                        t1 = datetime.strptime(t1, "%H:%M:%S")
                        t1 = str(t1)
                        print(t1)
                        now = datetime.now()
                        t2 = now.strftime("%H:%M:%S")
                        t2 = str(t2)
                        print(t1[11: 13])
                        print(t2[0:2])
                        if int(t2[0:2]) - int(t1[11:13]) > 1:
                            markAttendance(name)
                    else:
                        markAttendance(name)
            present = name
            if present != past:
                engine = pyttsx3.init()
                rate = engine.getProperty("rate")
                engine.setProperty("rate", 130)
                engine.say("The person standing in front of you is")
                engine.say(name)
                engine.runAndWait()
                past = present

        cv2.imshow("show", frame)
    if cv2.waitKey(1) == ord("q"):
        exit()
