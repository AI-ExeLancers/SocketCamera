import json
import cv2
import numpy as np
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition


def load_known_faces(image_path):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    
    if len(face_encodings) > 0:
        return face_encodings
    else:
        raise ValueError("No face found in the provided image!")

my_face_encoding = load_known_faces("img.jpg")

known_face_encodings = [my_face_encoding]
known_face_names = ["Keshav"]

def decode_base64_image(photo):
    _, image_data = photo.split(';base64')
    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def frame_processing(frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    return face_locations, face_encodings

def annotate_frame(frame, face_locations, face_encodings, known_face_encodings, known_face_names):
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    return frame

def initialize_video_writer(frame, output_path='video/output.avi'):
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    return cv2.VideoWriter(output_path, fourcc, 30.0, (frame.shape[1], frame.shape[0]))