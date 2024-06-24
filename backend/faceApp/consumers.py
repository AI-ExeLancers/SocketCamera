
#--------------new consumer-------------------
import json
import cv2
import base64
import face_recognition
import numpy as np
from .utils import decode_base64_image, annotate_frame, load_known_faces
from channels.generic.websocket import AsyncWebsocketConsumer

class FaceDetectionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        # Load known face encodings when a client connects
        known_image = face_recognition.load_image_file("img.jpg")
        self.known_encoding = face_recognition.face_encodings(known_image)[0]
        print("reacted connect method")

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        print("reacted received method")
        data = json.loads(text_data)
        # print("Data",data)
        frame_data = data.get('image')
        # print("frame data ",frame_data)
        # Decode base64 frame data
        try:
            frame = decode_base64_image(frame_data)
        except Exception as e:
            await self.send_json({'success': False, 'error': str(e)})
            return

        if frame is None:
            await self.send_json({'success': False, 'error': 'Failed to decode frame.'})
            return

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces in the frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Check if the detected face matches the known face
        matches = face_recognition.compare_faces([self.known_encoding], face_encodings[0]) if face_encodings else [False]
        face_detected = any(matches)

        # Draw rectangle around faces
        for (top, right, bottom, left) in face_locations:
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Annotate the frame with face names (using utils functions)
        annotated_frame = annotate_frame(frame, face_locations, face_encodings, [self.known_encoding], ["YourName"])

        # Encode annotated frame to send via WebSocket
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        processed_frame = base64.b64encode(buffer).decode('utf-8')

        # Send processed frame and face detection status back to client
        # await self.send_json({
        #     'processedFrame': f'data:image/jpeg;base64,{processed_frame}',
        #     'faceDetected': face_detected
        # })
        await self.send(text_data=json.dumps({
            'processedFrame': f'data:image/jpeg;base64,{processed_frame}',
            'faceDetected': face_detected
        }))





#-------------------old consumer--------------
# import json
# import cv2
# import base64
# import face_recognition
# from channels.generic.websocket import AsyncWebsocketConsumer
# import asyncio
# from .utils import load_known_faces,decode_base64_image,frame_processing,annotate_frame, initialize_video_writer

# import numpy as np

# class FaceDetectionConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         self.known_encoding = None
#         known_image = face_recognition.load_image_file("img.jpg")
#         self.known_encoding = face_recognition.face_encodings(known_image)
    
#     async def disconnect(self, close_code):
#         pass

    
#     async def receive(self,text_data):

#             data = json.loads(text_data)
#             frame_data = data.get('image')
#             print("frame_Data : ",frame_data)

#                     # Decode the base64 frame data
#             frame_bytes = base64.b64decode(frame_data.split(',')[1])  # Split off the header 'data:image/jpeg;base64,'
#                     # Convert bytes to numpy array
#             np_frame = np.frombuffer(frame_bytes, np.uint8)
#                     # Decode frame with OpenCV
#             frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
#             if frame is None:
#                 print("Failed to decode frame.")
#                 return

#             # Decode the frame from base64
#             # frame = base64.b64decode(frame_data.split(';base64'))
#             # np_frame = np.frombuffer(frame, np.uint8)
#             # frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

#             # Resize frame for faster processing
#             small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#             # rgb_small_frame = small_frame[:, :, ::-1]
#             rgb_small_frame = cv2.cvtColor(small_frame,cv2.COLOR_BGR2RGB)

#             # Detect faces in the frame
#             face_locations = face_recognition.face_locations(rgb_small_frame)
#             face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

#             # Check if the detected face matches the known face
#             matches = face_recognition.compare_faces([self.known_encoding], face_encodings[0]) if face_encodings else [False]
#             face_detected = any(matches)

#             # Draw rectangle around faces
#             for (top, right, bottom, left) in face_locations:
#                 top *= 4
#                 right *= 4
#                 bottom *= 4
#                 left *= 4
#                 cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

#             # Encode frame to send via WebSocket
#             _, buffer = cv2.imencode('.jpg', frame)
#             frame_bytes = base64.b64encode(buffer).decode('utf-8')
#             message = {"image": frame_bytes, "face_detected": face_detected}
#             await self.send_json(message)
#             await asyncio.sleep(0.1)

#             processed_frame = base64.b64encode(buffer).decode('utf-8')

#             await self.send(text_data=json.dumps({
#                  'processedFrame': f'data:image/jpeg;base64,{processed_frame}',
#                  'faceDetected': face_detected
#              }))