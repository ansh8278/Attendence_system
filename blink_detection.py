import cv2
import dlib
from scipy.spatial import distance
import numpy as np

# Load Dlib face detector
face_detector = dlib.get_frontal_face_detector()

# Load shape predictor model (with error handling)
try:
    landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks (1).dat")
except RuntimeError:
    print("❌ ERROR: Could not load shape_predictor_68_face_landmarks.dat. Check file path!")
    exit()

# Calculate Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    
    if C == 0:  # Prevent division by zero
        return 0
    
    return (A + B) / (2.0 * C)

# Function to detect blink
def detect_blink(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector(gray)

    if len(faces) == 0:
        print("👀 No face detected. Ensure proper lighting and position.")
        return False

    for face in faces:
        landmarks = landmark_predictor(gray, face)

        # Extract eye coordinates
        left_eye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)])
        right_eye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)])

        left_EAR = eye_aspect_ratio(left_eye)
        right_EAR = eye_aspect_ratio(right_eye)

        avg_EAR = (left_EAR + right_EAR) / 2.0

        print(f"🔍 EAR: {avg_EAR:.3f}")  # Debugging output

        # Blink detected if EAR drops below threshold
        if avg_EAR < 0.22:
            print("👁️ Blink detected!")
            return True

    return False
