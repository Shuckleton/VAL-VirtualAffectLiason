import json
import os
import time
import serial
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from llama_cpp import Llama
from components.model_setup import llm
from components.memory import memory, save_memory, update_memory, inject_memory
from components.persona import set_persona_for_current_input
from components.clear_memory import clear_memory_sequence
from components.memory_update import user_input_contains_memory_trigger, update_memory_from_response

app = Flask(__name__)
socketio = SocketIO(app)  # Initialize SocketIO

chat_history = []
max_history_length = 5


@app.route('/')
def home():
    return render_template('index.html')


# WebSocket event for handling user input and generating responses in real-time
@socketio.on('send_message')
def handle_message(data):
    user_input = data['message']  # User input is sent via the socket

    # Handle memory clearing commands
    if any(cmd in user_input.lower() for cmd in ["clear memory", "reset memory", "forget everything"]):
        if clear_memory_sequence():
            emit('receive_message', {"status": "memory cleared"})
            return

    # Handle exit or quit command
    if user_input.lower() in ["exit", "quit"]:
        save_memory()
        emit('receive_message', {"status": "exit", "message": "V.A.L ❤️: Aww, leaving already? I'll miss you 🥺"})
        return

    start_time = time.time()

    # Update memory and save it
    update_memory(user_input)
    save_memory()

    val_intro = set_persona_for_current_input()
    memory_context = inject_memory()

    full_context = [
        {"role": "system", "content": f"{val_intro}\n{memory_context}"},
        {"role": "user", "content": user_input}
    ]

    chat_history = full_context[-max_history_length:]

    # Call the model to generate a response
    response = llm.create_chat_completion(
        messages=full_context,
        stream=True,
        max_tokens=250,
        temperature=0.7,
        top_p=0.9
    )

    full_reply = ""
    # Emit each character one by one
    for chunk in response:
        delta = chunk['choices'][0]['delta'].get('content', '')
        full_reply += delta

        # Emit each character separately to simulate typing effect
        for char in delta:
            socketio.emit('receive_message', {"status": "typing", "message": char})
            time.sleep(0.05)  # Delay for typing effect (you can adjust the timing)

    reply = full_reply.strip()

    # Check if the input contains memory update trigger and update memory accordingly
    if user_input_contains_memory_trigger(user_input):
        update_memory_from_response(user_input, full_reply)

    response_time = time.time() - start_time

    # Append the conversation to the chat history
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": reply})

    if len(chat_history) > max_history_length * 2:
        chat_history = chat_history[-max_history_length * 2:]

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
