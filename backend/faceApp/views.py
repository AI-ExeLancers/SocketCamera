# views.py

import json
import cv2
import numpy as np
import base64
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
from .utils import load_known_faces,decode_base64_image,frame_processing,annotate_frame, initialize_video_writer

# Global variables to store resources
video_writer = None
my_face_encoding = load_known_faces("img.jpg")

if len(my_face_encoding) > 0:
    my_face_encoding = my_face_encoding[0]
else:
    raise ValueError("No face found in the provided image!")

known_face_encodings = [
    my_face_encoding,
]
known_face_names = [
    "Keshav",
]

@csrf_exempt
def process_frames(request):
    global video_writer,known_face_encodings,known_face_names
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            photo = data.get('image')
            frame = decode_base64_image(photo)
            face_locations, face_encodings = frame_processing(frame)
            annotated_frame = annotate_frame(frame, face_locations, face_encodings, known_face_encodings, known_face_names)

            if video_writer is None:
                video_writer = initialize_video_writer(annotated_frame)

            video_writer.write(annotated_frame)

            _, buffer = cv2.imencode('.jpg', annotate_frame)
            # frame_bytes = base64.b64encode(buffer).decode('utf-8')
            # message = {"image": frame_bytes}
            processed_frame = base64.b64encode(buffer).decode('utf-8')
            def generate():
                while True:
                    # Yield the annotated_frame as bytes
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + processed_frame + b'\r\n')

            return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')



            # return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})

@csrf_exempt
def finalize_video(request):
    global video_writer
    
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image')
        _, str_img = image_data.split(';base64')

        try:
            decoded_file = base64.b64decode(str_img)
            file_to_save = "video/my_image.png"
            with open(file_to_save, "wb") as f:
                    f.write(decoded_file)
            print("last frame saved successfully:", file_to_save)
        
            # Release VideoWriter resources
            if video_writer is not None:
                video_writer.release()
                video_writer = None  # Remove VideoWriter object
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'VideoWriter object not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'})
