# code to test 

import os
import csv
import cv2
import face_recognition
import numpy as np
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE
from email import encoders

# Function to encode faces in the given directory
def encode_faces(directory):
    known_faces = []
    known_names = []
    for filename in os.listdir(directory):
        image = cv2.imread(os.path.join(directory, filename))
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image, model='cnn')
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations, num_jitters=5)
        if len(face_encodings) > 0:
            known_faces.append(face_encodings[0])
            known_names.append(os.path.splitext(filename)[0])
    return known_faces, known_names

# Encode known faces and names
known_faces, known_names = encode_faces("C:/Users/gunja/OneDrive/Desktop/Pro/known_faces")

print("Encoding complete.")

# Attendance file path and header
attendance_file = "C:/Users/gunja/OneDrive/Desktop/Pro/attendance.csv"
header = ['Name', 'Time']

# Create attendance file if it does not exist
if not os.path.isfile(attendance_file):
    with open(attendance_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

# Now that we have the known faces and their names, we can perform face recognition on the webcam feed
video_capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)

# List to store attendance data
attendance_data = []

# Start time of video capture
start_time = datetime.now()

# Capture video for 2 minutes
while (datetime.now() - start_time).seconds < 120:
    ret, frame = video_capture.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame, model='cnn')
    encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=5)
    for face_encoding, face_location in zip(encodings, face_locations):
        matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.5)
        name = "Unknown"
        if True in matches:
            matched_index = matches.index(True)
            name = known_names[matched_index]

            # Add attendance data
            attendance_data.append([name, datetime.now().strftime('%Y-%m-%d %H:%M:%S %p')])

        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
video_capture.release()
cv2.destroyAllWindows()

# Write attendance data to file
with open(attendance_file, 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(attendance_data)

# Sender and receiver email addresses
sender_email = "senders mail id"
receiver_email = "receivers mail id"

# Login credentials for sender email account
username = "your email id"
password = "Your password"

# Create a multipart message object and add email headers
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "Attendance CSV File"

# Read the CSV file
csv_file_path = "C:/Users/gunja/OneDrive/Desktop/Pro/attendance.csv"
with open(csv_file_path, 'r') as file:
    data = file.read()

# Add the CSV file as an attachment to the email
attachment = MIMEApplication(data, _subtype="csv")
attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(csv_file_path))
msg.attach(attachment)


# Send the email
with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(sender_email, receiver_email, msg.as_string())
    smtp.quit()
    
print("Email sent successfully!")