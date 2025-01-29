import cv2
import socket
import pickle
import numpy as np

# Initialize the socket for receiving video frames and sending motion data
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_ip = '192.168.9.12' # Receiver's IP address
receiver_port = 6969
udp_socket.bind((receiver_ip, receiver_port))

# Variables to store the previous position of the red dot
previous_position = None

print("Waiting for streamer")
while True:
    # Receive the video frame
    data, client_address = udp_socket.recvfrom(1000000)

    # Extract frames
    try:
        frame_data = pickle.loads(data)
        frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error decoding frame: {e}")
        continue

    # Process the frame to detect the red dot
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_red1 = np.array([0, 180, 200])  # Adjust these values for red dot
    upper_red1 = np.array([20, 255, 255])
    
    lower_red2 = np.array([155, 180, 200]) 
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)
    
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour, assumed to be the red dot
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(largest_contour)
        center = (int(x), int(y))

        # Draw the red dot on the frame
        cv2.circle(frame, center, int(radius), (0, 255, 0), 2)

        # Calculate motion in x-y directions
        if previous_position is not None:
            dx = int(center[0] - previous_position[0])
            dy = int(center[1] - previous_position[1])
            print(f"Motion: dx={dx}, dy={dy}")
        else:
            print("No motion data yet.")
            dx, dy = 0, 0  # No motion

        previous_position = center
        motion_data = {"X":dx,"Y":dy, "Detect":True}
        
    else:
        motion_data = {"X":0,"Y":0, "Detect": False}
    
    # Send back to the sender
    motion_data = pickle.dumps(motion_data)
    udp_socket.sendto(motion_data, client_address)  

    # Display the processed video on the receiver side
    cv2.imshow('Receiver', frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
udp_socket.close()
