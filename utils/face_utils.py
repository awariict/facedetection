"""
face_utils.py
Face detection & recognition using OpenCV's Haar Cascade (detection) and
LBPH — Local Binary Patterns Histograms (recognition).

LBPH is used instead of dlib/face_recognition because it has no heavy
compilation requirements, making it far more reliable to deploy on
Streamlit Community Cloud.
"""

import cv2
import numpy as np
import base64
from PIL import Image
import io

FACE_SIZE = (200, 200)
RECOGNITION_THRESHOLD = 75  # Lower LBPH distance = better match; tune as needed

import os
_CASCADE_PATH = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
_face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)

if _face_cascade.empty():
    raise RuntimeError(
        f"Failed to load Haar Cascade from {_CASCADE_PATH}. "
        "Make sure haarcascade_frontalface_default.xml is present in the utils/ folder."
    )


def cv2_image_from_pil(pil_img: Image.Image) -> np.ndarray:
    """Convert a PIL image (from st.camera_input) to an OpenCV BGR image."""
    rgb = np.array(pil_img.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return bgr


def detect_and_crop_face(cv2_img: np.ndarray):
    """
    Detects the largest face in the image, crops, converts to grayscale,
    and resizes to a standard size for LBPH training/recognition.

    Returns (face_image, found: bool)
    """
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    faces = _face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=6, minSize=(80, 80)
    )

    if len(faces) == 0:
        return None, False

    # Pick the largest detected face (closest to camera)
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_crop = gray[y : y + h, x : x + w]
    face_resized = cv2.resize(face_crop, FACE_SIZE)
    return face_resized, True


def image_to_base64(gray_face_img: np.ndarray) -> str:
    """Encode a grayscale numpy face image as a base64 PNG string for MongoDB storage."""
    success, buffer = cv2.imencode(".png", gray_face_img)
    return base64.b64encode(buffer).decode("utf-8")


def base64_to_cv2_image(b64_str: str) -> np.ndarray:
    """Decode a base64 PNG string back into a numpy grayscale image."""
    img_bytes = base64.b64decode(b64_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
    return img


def train_recognizer_from_users(users: list):
    """
    Builds an LBPH recognizer trained on all registered users' face samples.

    Returns (recognizer, label_map) where label_map maps integer label -> user_id
    """
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    faces = []
    labels = []
    label_map = {}

    for idx, user in enumerate(users):
        label_map[idx] = user["user_id"]
        for b64_face in user.get("face_samples", []):
            face_img = base64_to_cv2_image(b64_face)
            faces.append(face_img)
            labels.append(idx)

    if not faces:
        return None, {}

    recognizer.train(faces, np.array(labels))
    return recognizer, label_map


def recognize_face(recognizer, label_map: dict, face_img: np.ndarray):
    """
    Predicts the identity of a given face image.
    Returns (user_id or None, confidence_score)
    Lower confidence = better match in LBPH.
    """
    if recognizer is None:
        return None, None

    label, confidence = recognizer.predict(face_img)

    if confidence <= RECOGNITION_THRESHOLD:
        return label_map.get(label), confidence
    return None, confidence
