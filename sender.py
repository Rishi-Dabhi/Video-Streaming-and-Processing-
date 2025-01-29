import cv2
import socket
import numpy as np
import pickle

# Initialize UDP socket for streaming video and receiving motion data
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000)
receiver_ip = '192.168.0.38'  # Replace with the receiver's IP
receiver_port = 6969  # Replace with the Port Number

udp_socket.bind(('0.0.0.0',0))
# Video capture setup
cap = cv2.VideoCapture(0)  # Use webcam

print("Streaming and waiting for receiver to connect")

while True:
    
    ret, frame = cap.read()
    if not ret:
        print("No Frame Capture")
        break

    # Encode frame and send it to receiver
    ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
    
    udp_socket.sendto(pickle.dumps(buffer), (receiver_ip, receiver_port))
        
    # Receive motion data from the receiver
    try:
        data, _ = udp_socket.recvfrom(1024)  # Receive x, y data as a string
        data = pickle.loads(data)
        X = data.get('X',0)
        Y = data.get('Y',0)
        detect = data.get('Detect',False)
        if not detect:
            text = "No-Detection"
        else:
            text = f"Motion Data: X:{X}, Y:{Y}"
        print(text)
    except socket.error as e:
        print(f"Error receiving motion data {e}")
        pass
    
    # Display the streamed video
    cv2.putText(frame, text, (frame.shape[1]-400,30),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0),2,cv2.LINE_AA)
    cv2.imshow('Streaming', frame)

    if cv2.waitKey(10) == 13:  # Break on Enter key
        break

cap.release()
cv2.destroyAllWindows()
udp_socket.close()
