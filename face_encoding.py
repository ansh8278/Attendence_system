import os
import cv2
import face_recognition
import pickle

# Path to folder containing face images
path = "faces"
images = []
classNames = []

# Loop through all images
for imgName in os.listdir(path):
    if imgName.startswith("."):
        continue  # Ignore system/hidden files

    imgPath = os.path.join(path, imgName)
    img = cv2.imread(imgPath)

    if img is None:
        print(f"❌ Error: Could not read image {imgPath}")
        continue

    # High-accuracy: Don't resize image
    images.append(img)
    classNames.append(os.path.splitext(imgName)[0])  # Remove .jpg/.png

# Encoding function
def findEncodings(images):
    encodeList = []
    for i, img in enumerate(images):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(imgRGB)

        if encodes:
            encodeList.append(encodes[0])
            print(f"✅ Encoded: {classNames[i]}")
        else:
            print(f"⚠️ Warning: No face found in {classNames[i]}")
    return encodeList

print("🔍 Starting High-Accuracy Face Encoding...")

# Perform encoding
knownEncodings = findEncodings(images)
data = {"encodings": knownEncodings, "names": classNames}

# Save encodings to a pickle file
with open("encodings.pkl", "wb") as f:
    pickle.dump(data, f)

print(f"\n✅ Encoding Complete! Total encoded faces: {len(knownEncodings)}")
