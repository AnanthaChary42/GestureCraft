import cv2
import base64
from camera import Webcam
from tracking import HandTracker, GestureManager, extract_landmarks
from communication import SocketServer
from utils import distance

cam = Webcam()
tracker = HandTracker()
manager = GestureManager()
server = SocketServer() # Initialize the connection

while True:
    frame = cam.read()
    if frame is None:
        break

    result = tracker.process(frame)
    
    # 1. Encode Frame for Streaming (JPEG -> Base64)
    # Optimize: Reduce quality to 50% to speed up transmission (less lag)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    _, buffer = cv2.imencode('.jpg', frame, encode_param)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    
    # Default payload
    payload = {
        "hand_detected": False,
        "gesture": "NONE",
        "landmarks": [],
        "image": jpg_as_text # Send the video frame
    }

    if result.hand_landmarks:
        for hand in result.hand_landmarks:
            tracker.draw(frame, hand)
            landmarks = extract_landmarks(hand)
            
            # Gesture Detection Logic
            state = manager.update(landmarks)
            
            # Draw debug info
            dist = distance(landmarks[4], landmarks[8])
            cv2.putText(frame, f"Dist: {dist:.3f}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"State: {state}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                        (0, 255, 0) if state != "NONE" else (0, 0, 255), 2)
                        
            # Update Payload for streaming
            payload["hand_detected"] = True
            payload["gesture"] = state
            # Convert numpy array to list for JSON serialization
            payload["landmarks"] = landmarks.tolist() 
            
    # Send data to the frontend/hologram
    server.send_data(payload)

    # cv2.imshow("Hand Landmarks", frame) # Disabled: Using Web Frontend

    # if cv2.waitKey(1) & 0xFF == 27:
    #     break
    
    # Add a small sleep to prevent 100% CPU usage since we removed waitKey
    import time
    time.sleep(0.01)

cam.release()
cv2.destroyAllWindows()
