import serial
import time

arduino = serial.Serial(port = 'COM3', baudrate = 9600, timeout = 1)
time.sleep(2)

while True:
    command = input("Enter 'on' or 'off': ").strip()
    if command in ["on", "off"]:
        arduino.write((command+'\n').encode())
    else:
        print ("Invalid Command")