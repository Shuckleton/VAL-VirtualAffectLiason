document.addEventListener('DOMContentLoaded', function() {
    const socket = io.connect('http://' + document.domain + ':' + location.port); // Connect to SocketIO

    const sendButton = document.querySelector('.send-button');
    const userInputField = document.querySelector('.chat-input');
    const chatBox = document.querySelector('.chat-box');

    sendButton.addEventListener('click', function() {
        const userInput = userInputField.value.trim();
        if (userInput) {
            displayMessage(userInput, 'user');  // Display user message
            userInputField.value = '';          // Clear input field
            socket.emit('send_message', { message: userInput });  // Emit message to backend
        }
    });

    // Listen for responses from backend
    socket.on('receive_message', function(data) {
        if (data.status === 'typing') {
            // Add each character to the assistant's message as it's received
            appendToMessage(data.message);
        } else if (data.status === 'success') {
            // Once the message is fully received, display the complete response
            displayMessage(data.response, 'assistant');
        }
    });

    // Function to display messages in the chat box
    function displayMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.textContent = message;

        if (sender === 'user') {
            messageDiv.classList.add('user-message');
        } else {
            messageDiv.classList.add('assistant-message');
        }

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Function to append characters to the assistant's message while it's typing
    function appendToMessage(char) {
        const lastMessageDiv = chatBox.lastElementChild;

        if (lastMessageDiv && lastMessageDiv.classList.contains('assistant-message')) {
            lastMessageDiv.textContent += char; // Add each new character to the message
        } else {
            displayMessage(char, 'assistant'); // If there's no message yet, start a new one
        }
        chatBox.scrollTop = chatBox.scrollHeight; // Keep the chat scrolled to the bottom
    }
});
