from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

FACES_FOLDER = "faces"
USER_EMAILS_FILE = "user_emails.json"

# Ensure folder exists
os.makedirs(FACES_FOLDER, exist_ok=True)

# Load user emails from file (or create empty dictionary)
if os.path.exists(USER_EMAILS_FILE):
    with open(USER_EMAILS_FILE, "r") as file:
        USER_EMAILS = json.load(file)
else:
    USER_EMAILS = {}

def save_emails():
    """ Save user emails to file """
    with open(USER_EMAILS_FILE, "w") as file:
        json.dump(USER_EMAILS, file, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name").strip().upper()
    email = request.form.get("email").strip()
    file = request.files["image"]

    if not name or not email or not file:
        return jsonify({"status": "error", "message": "All fields are required!"}), 400

    if name in USER_EMAILS:
        return jsonify({"status": "error", "message": "User already exists!"}), 400

    # Save the uploaded image in "faces" folder
    file_path = os.path.join(FACES_FOLDER, f"{name}.jpg")
    file.save(file_path)

    # Save user details
    USER_EMAILS[name] = email
    save_emails()

    return jsonify({"status": "success", "message": f"User {name} registered successfully!"})

@app.route("/users")
def get_users():
    return jsonify(USER_EMAILS)

if __name__ == "__main__":
    app.run(debug=True)
