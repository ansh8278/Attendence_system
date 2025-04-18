import cv2
import face_recognition
import numpy as np
import json
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
import pyttsx3  # 🔊 Text-to-Speech Library
from blink_detection import detect_blink
from face_encoding import knownEncodings, classNames

# File paths
USER_EMAILS_FILE = "user_emails.json"
ATTENDANCE_FILE = "Attendance.csv"
EMAIL_LOG_FILE = "email_log.txt"

# 🎤 Initialize Text-to-Speech engine
engine = pyttsx3.init()

# ✅ Function to load user emails dynamically from JSON
def load_user_emails():
    if not os.path.exists(USER_EMAILS_FILE):
        with open(USER_EMAILS_FILE, "w") as file:
            json.dump({}, file)  # Create empty JSON file
        return {}

    try:
        with open(USER_EMAILS_FILE, "r") as file:
            data = file.read()
            return json.loads(data) if data else {}  # Handle empty file
    except json.JSONDecodeError:
        print("❌ Error: JSON file is corrupted. Resetting data.")
        with open(USER_EMAILS_FILE, "w") as file:
            json.dump({}, file)  # Reset the file
        return {}

# ✅ Load user emails
USER_EMAILS = load_user_emails()

# ✅ Function to save updated user emails
def save_user_emails(user_data):
    with open(USER_EMAILS_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

# ✅ Function to mark attendance
def markAttendance(name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(ATTENDANCE_FILE, "a") as file:
        file.write(f"{name},{now}\n")
        print(f"📝 Attendance marked for {name} at {now}")

    # 🔊 Speak confirmation
    engine.say(f"Attendance marked for {name}.")
    engine.runAndWait()

# ✅ Function to check if email was already sent today
def is_email_sent_today(name):
    today_date = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(EMAIL_LOG_FILE):
        return False  # No emails sent yet

    with open(EMAIL_LOG_FILE, "r") as file:
        for line in file:
            recorded_name, recorded_date = line.strip().split(",")
            if recorded_name == name and recorded_date == today_date:
                return True  # Email already sent

    return False

# ✅ Function to log sent email
def log_email_sent(name):
    today_date = datetime.now().strftime("%Y-%m-%d")
    with open(EMAIL_LOG_FILE, "a") as file:
        file.write(f"{name},{today_date}\n")

# ✅ Function to send email
def send_email(name):
    if name not in USER_EMAILS:
        print(f"🚫 No email found for {name}. Skipping email notification.")
        return

    if is_email_sent_today(name):
        print(f"📧 Email already sent to {name} today. Skipping...")
        return

    sender_email = "aitraffixsolutions@gmail.com"
    sender_password = "tjbtthiuckikwgmw"  # Replace with your app password
    receiver_email = USER_EMAILS[name]

    msg = EmailMessage()
    msg["Subject"] = "Attendance Marked ✅"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(f"Hello {name}, your attendance has been marked today at {datetime.now().strftime('%H:%M:%S')}.")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"📧 Email sent to {receiver_email}")
        log_email_sent(name)  # Log email after sending
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ✅ Start webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Unable to access the webcam.")
    exit()

while True:
    success, img = cap.read()
    if not success:
        print("❌ Error: Could not read frame from webcam.")
        break

    imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    if not encodesCurFrame:
        print("👀 No faces detected. Please adjust your position.")
        cv2.imshow("Attendance System", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(knownEncodings, encodeFace)
        faceDis = face_recognition.face_distance(knownEncodings, encodeFace)

        if not any(matches):
            print("🚫 Unknown face detected.")
            continue

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Blink detection for anti-spoofing
            if detect_blink(img):
                markAttendance(name)
                send_email(name)

                print("✅ Attendance recorded. Closing system...")
                cap.release()
                cv2.destroyAllWindows()
                exit()  # Exit the program

    cv2.imshow("Attendance System", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("📸 Webcam closed. Exiting program.")
