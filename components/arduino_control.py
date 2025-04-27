# Updated function in arduino_control.py
def send_arduino_command(reply, arduino):

    lowered_reply = reply.lower()

    if any(keyword in lowered_reply for keyword in ["turn on", "switch on", "light on", "switches on"]):
        arduino.write(b'on\n')
        print("[Command sent: ON]")

    elif any(keyword in lowered_reply for keyword in ["turn off", "switch off", "light off", "switches off"]):
        arduino.write(b'off\n')
        print("[Command sent: OFF]")
