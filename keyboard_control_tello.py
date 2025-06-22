from djitellopy import tello
import KeyPressFunc as kp
from time import sleep, time
import pygame
import cv2


kp.init()
pygame.init()

drone = tello.Tello()
drone.connect()
drone.streamon()

win = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Dron Kontrola i Stream")

# keyboard control function
def getKeyBoardInput():
    ld, nN, gd, yv = 0, 0, 0, 0
    speed = 80  # Brzina kretanja

    if kp.getKey('LEFT'): ld = -speed
    elif kp.getKey('RIGHT'): ld = speed

    if kp.getKey('UP'): nN = speed
    elif kp.getKey('DOWN'): nN = -speed

    if kp.getKey('w'): gd = speed
    elif kp.getKey('s'): gd = -speed

    if kp.getKey('a'): yv = -speed
    elif kp.getKey('d'): yv = speed

    if kp.getKey('l'): drone.land()  
    if kp.getKey('t'): drone.takeoff()

    return [ld, nN, gd, yv]

prev_time = time()  # Initialize time to calculate FPS


while True:
    # get keyboard input
    vals = getKeyBoardInput()
    drone.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)

    # get frame from drone camera
    img = drone.get_frame_read().frame
    if img is None:
        continue

    # Calculate FPS
    curr_time = time()
    fps = int(1 / (curr_time - prev_time))  # FPS = 1 / time taken per frame
    prev_time = curr_time  # Update prev_time for the next frame


    # invert colors because opencv is in BGR
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.resize(img, (600, 600))

    # get battery, temp, height
    battery_level = drone.get_battery()
    temperature = drone.get_temperature()
    #tof_height = drone.get_distance_tof()
    #activeMotorTime = drone.get_flight_time()

    # add text to frame
    cv2.putText(img, f"Baterija: {battery_level}%", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, f"Temperatura: {temperature} C", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    #cv2.putText(img, f"Visina: {tof_height} cm", (10, 90), 
    #            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, f"FPS: {fps}", (10, 120), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    #cv2.putText(img, f"Vrijeme leta: {activeMotorTime}", (10, 150), 
    #           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # show frame
    cv2.imshow("Slika sa drona", img)

    # Add sleep to allow proper video rendering (adjust the value if needed)
    sleep(0.01)

    # stop program with 'q'
    if kp.getKey('q'):
        print("Zaustavljanje drona i prekid programa...")
        drone.land()
        drone.end()
        cv2.destroyAllWindows()
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break