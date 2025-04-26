import json
import os
import time
import serial

from llama_cpp import Llama
from components.model_setup import llm
from components.memory import memory, save_memory, update_memory, inject_memory, detect_emotion
from components.persona import set_persona_for_current_input
from components.clear_memory import clear_memory_sequence
from components.arduino_control import send_arduino_command
from components.memory_update import user_input_contains_memory_trigger,update_memory_from_response

arduino = None
try:
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
    time.sleep(2)
except serial.SerialException as e:
    print("Failed to Connect to Arduino")


# Main chat loop
print("💖 V.A.L. is online and ready to chat!")
chat_history = []
max_history_length = 5
while True:
    user_input = input("You: ")
    if any(cmd in user_input.lower() for cmd in ["clear memory", "reset memory", "forget everything"]):
        if clear_memory_sequence():
            continue
        else:
            continue

    if user_input.lower() in ["exit", "quit"]:
        save_memory()
        print("V.A.L ❤️: Aww, leaving already? I'll miss you 🥺")
        break

    start_time = time.time()

    update_memory(user_input)
    save_memory()

    val_intro = set_persona_for_current_input()
    memory_context = inject_memory()

    full_context = [
        {"role": "system", "content": f"{val_intro}\n{memory_context}"},
        {"role": "user", "content": user_input}
    ]

    chat_history = full_context[-max_history_length:]

    response = llm.create_chat_completion(
        messages=full_context,
        stream=True,
        max_tokens=250,
        temperature=0.7,
        top_p=0.9
    )

    full_reply = ""
    print("V.A.L ❤️: ", end='', flush=True)
    for chunk in response:
        delta = chunk['choices'][0]['delta'].get('content', '')
        print(delta, end='', flush=True)
        full_reply += delta

    reply = full_reply.strip()

    # Check if the input contains memory update trigger and update memory accordingly
    if user_input_contains_memory_trigger(user_input):
        update_memory_from_response(user_input, full_reply)

    # ARDUINO COMMAND SENDER
    send_arduino_command(reply, arduino)

    response_time = time.time() - start_time
    print(f"Response Time: {response_time:.2f} seconds")

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": reply})

    if len(chat_history) > max_history_length * 2:
        chat_history = chat_history[-max_history_length * 2:]

