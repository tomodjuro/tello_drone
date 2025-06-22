import cv2
from djitellopy import tello
import KeyPressFunc as kp
from time import sleep, time
import pygame
import os

### saves video and all frames as images after takeoff()




kp.init()
pygame.init()

alentello = tello.Tello()
alentello.connect()
alentello.streamon()

win = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Dron Kontrola i Stream")

# Initialize the flag for takeoff
is_taking_off = False

# Initialize VideoWriter for saving video (will start after takeoff)
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for .avi files
video_filename = 'drone_video.avi'   # your future video file name
frame_width = 600
frame_height = 600
out = None  # Initially, we don't create the VideoWriter

# Create a folder to save images (if it doesn't exist)
output_dir = 'drone_frames'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

frame_counter = 0  # For naming images

# keyboard control function
def getKeyBoardInput():
    global is_taking_off  # Declare is_taking_off as global to modify it
    ld, nN, gd, yv = 0, 0, 0, 0
    speed = 100  # drone speed

    if kp.getKey('LEFT'): ld = -speed
    elif kp.getKey('RIGHT'): ld = speed

    if kp.getKey('UP'): nN = speed
    elif kp.getKey('DOWN'): nN = -speed

    if kp.getKey('w'): gd = speed
    elif kp.getKey('s'): gd = -speed

    if kp.getKey('a'): yv = -speed
    elif kp.getKey('d'): yv = speed

    if kp.getKey('l'): alentello.land()  
    if kp.getKey('t'): 
        if not is_taking_off:  # Only take off if not already airborne
            print("Takeoff initiated!")
            alentello.takeoff()
            is_taking_off = True  # Set flag to true when takeoff is complete

    return [ld, nN, gd, yv]

prev_time = time()  # Initialize time to calculate FPS

while True:
    vals = getKeyBoardInput()
    alentello.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)

    # Begin saving video and frames only after takeoff
    if is_taking_off:
        if out is None:  # Initialize the video writer only after takeoff
            out = cv2.VideoWriter(video_filename, fourcc, 20.0, (frame_width, frame_height))

    
        img = alentello.get_frame_read().frame
        if img is None:
            continue

        # Calculate FPS
        curr_time = time()
        fps = int(1 / (curr_time - prev_time))
        prev_time = curr_time

        # change to BGR, because opencv
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = cv2.resize(img, (frame_width, frame_height))

        # Save the frame to video
        out.write(img)

        # Save the frame as an image
        frame_filename = os.path.join(output_dir, f'frame_{frame_counter:03d}.jpg')
        cv2.imwrite(frame_filename, img)
        frame_counter += 1

        # Display flight data on the image
        battery_level = alentello.get_battery()
        temperature = alentello.get_temperature()
        #tof_height = alentello.get_distance_tof()

        cv2.putText(img, f"Baterija: {battery_level}%", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"Temperatura: {temperature} C", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        #cv2.putText(img, f"Visina: {tof_height} cm", (10, 90), 
        #            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"FPS: {fps}", (10, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow("Slika sa drona", img)

    # Sleep to allow proper rendering
    sleep(0.01)

    if kp.getKey('q'):
        print("Zaustavljanje drona i prekid programa...")
        alentello.land()
        alentello.end()
        if out is not None:
            out.release()  # Release the video writer
        cv2.destroyAllWindows()
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if out is not None:
            out.release()  # Release the video writer
        break
