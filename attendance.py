import pandas as pd
import smtplib
import pyttsx3
from email.mime.text import MIMEText
from datetime import datetime

# Email Configuration
EMAIL_ADDRESS = "ansh.322chopra@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "yotuzzrxtrmogswb"  # Use an App Password for Gmail

def send_email(name, timeString, dateString):
    """Send an email notification when attendance is marked."""
    recipient_email = f"{name.lower()}@example.com"  # Update logic for real emails
    subject = "Attendance Marked"
    body = f"Hello {name},\nYour attendance has been marked at {timeString} on {dateString}.\n\nThank you!"

    msg = MIMEText(body)
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    msg["Subject"] = subject

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())
        server.quit()
        print(f"📧 Email sent to {recipient_email}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

def announce_attendance(name, timeString):
    """Use text-to-speech to announce attendance."""
    engine = pyttsx3.init()
    engine.say(f"Attendance marked for {name} at {timeString}")
    engine.runAndWait()

def markAttendance(name):
    try:
        df = pd.read_csv("attendance.csv")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=["Name", "Date", "Time"])

    now = datetime.now()
    timeString = now.strftime("%H:%M:%S")
    dateString = now.strftime("%Y-%m-%d")

    if "Name" not in df.columns:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])

    if name not in df["Name"].values:
        new_entry = pd.DataFrame([[name, dateString, timeString]], columns=["Name", "Date", "Time"])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv("attendance.csv", index=False)
        print(f"📝 Attendance marked for {name} at {timeString}")

        # Call email & voice notification functions
        send_email(name, timeString, dateString)
        announce_attendance(name, timeString)
