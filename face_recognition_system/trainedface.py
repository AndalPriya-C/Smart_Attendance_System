import cv2
import tkinter as tk
from tkinter import messagebox as mess
from PIL import Image, ImageTk
import numpy as np
import csv
import pandas as pd
import datetime
import os

def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    ids = []
    
    for image_path in image_paths:
        img = Image.open(image_path).convert('L')  # Convert to grayscale
        img_np = np.array(img, 'uint8')
        
        id = int(os.path.split(image_path)[-1].split(".")[1])
        faces.append(img_np)
        ids.append(id)
    
    return faces, ids

def track_attendance(cap):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("TrainingImageLabel/Trainner.yml")

    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    while True:
        ret, frame = cap.read()
        if not ret:
            mess.showerror("Error", "Failed to capture frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_roi = gray[y:y + h, x:x + w]
            label, confidence = recognizer.predict(face_roi)

            if confidence < 50:
                # Fetch student details from CSV
                df = pd.read_csv("StudentDetails/StudentDetails.csv")
                student_info = df[df['SERIAL NO.'] == label]
                student_name = student_info['NAME'].values[0]

                # Record attendance
                record_attendance(label, student_name)
                
                # Draw rectangle around the face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {label} - {student_name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow("Attendance System", frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == 17:  # Ctrl+Q
            break

    cap.release()
    cv2.destroyAllWindows()

def record_attendance(student_id, student_name):
    date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.datetime.now().strftime("%H:%M:%S")

    # Define the start times and end times for each period
    periods = {
        "I": ("09:10:00", "10:00:00"),
        "II": ("10:00:00", "10:50:00"),
        "Break": ("10:50:00", "11:10:00"),
        "III": ("11:10:00", "12:00:00"),
        "IV": ("12:00:00", "12:50:00"),
        "V": ("13:30:00", "14:20:00"),
        "VI": ("14:20:00", "15:10:00"),
        "VII": ("15:10:00", "16:00:00")
    }

    # Map the current time to the corresponding period
    current_period = None
    for period, (start_time, end_time) in periods.items():
        start_time_obj = datetime.datetime.strptime(start_time, "%H:%M:%S")
        end_time_obj = datetime.datetime.strptime(end_time, "%H:%M:%S")
        if start_time_obj <= datetime.datetime.now() <= end_time_obj:
            current_period = period
            break

    attendance_file_path = f"Attendance/Attendance_{date_today}.csv"
    headers = ["ID", "Name", "Date", "Time", "I", "II", "Break", "III", "IV", "V", "VI", "VII"]

    if not os.path.isfile(attendance_file_path):
        with open(attendance_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)

    with open(attendance_file_path, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        attendance_row = [student_id, student_name, date_today, time_now] + [""] * 7  # Initialize columns I to VII
        if current_period:
            attendance_row[headers.index(current_period)] = "Present"
        csvwriter.writerow(attendance_row)


# Tkinter window
window = tk.Tk()
window.title("Attendance System")

# Button to start attendance tracking
start_attendance_button = tk.Button(window, text="Start Attendance", command=lambda: track_attendance(cv2.VideoCapture(0)))
start_attendance_button.pack()

# Run the Tkinter main loop
window.mainloop()
