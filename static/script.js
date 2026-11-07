
// -----------------------------------
// 1. GET HTML ELEMENTS
// -----------------------------------

const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");
const welcome = document.getElementById("welcome");


// -----------------------------------
// 2. CONVERSATION MEMORY
// -----------------------------------

let conversationId = sessionStorage.getItem("conversationId");


// -----------------------------------
// 3. ADD MESSAGE TO CHAT
// -----------------------------------

function addMessage(text, sender) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");

    if (sender === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("bot-message");
    }

    const label = document.createElement("div");

    label.classList.add("message-label");

    label.textContent =
        sender === "user" ? "You" : "NeuroNest AI";

    const content = document.createElement("div");

    content.textContent = text;

    messageDiv.appendChild(label);
    messageDiv.appendChild(content);

    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return content;
}


// -----------------------------------
// 4. SCROLL TO LATEST MESSAGE
// -----------------------------------

function scrollToBottom() {

    chatMessages.scrollTop = chatMessages.scrollHeight;

}


// -----------------------------------
// 5. SEND MESSAGE WITH STREAMING
// -----------------------------------

async function sendMessage() {

    const message = userInput.value.trim();

    if (!message || sendButton.disabled) {
        return;
    }

    // Hide welcome screen

    welcome.style.display = "none";

    // Display user's message

    addMessage(message, "user");

    userInput.value = "";

    // Disable input while generating

    sendButton.disabled = true;
    userInput.disabled = true;

    // Create an empty bot message.
    // Incoming chunks will appear inside it.

    const botContent = addMessage("", "bot");

    botContent.textContent = "NeuroNest AI is thinking...";

    let firstChunkReceived = false;
    let streamError = null;
    let completed = false;

    try {

        // Send request to FastAPI

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                conversation_id: conversationId

            })

        });

        if (!response.ok) {

            let errorMessage = "Something went wrong.";

            try {
                const data = await response.json();
                errorMessage = data.detail || errorMessage;
            } catch (e) {
                // Keep default error message
            }

            throw new Error(errorMessage);
        }

        if (!response.body) {
            throw new Error("Streaming is not supported by this browser.");
        }

        // Read streaming response

        const reader = response.body.getReader();

        const decoder = new TextDecoder();

        let buffer = "";

        // Process each incoming JSON line

        function processLine(line) {

            if (!line.trim()) {
                return;
            }

            const data = JSON.parse(line);

            // Receive conversation ID

            if (data.type === "start") {

                conversationId = data.conversation_id;

                sessionStorage.setItem(
                    "conversationId",
                    conversationId
                );

            }

            // Receive response chunks

            else if (data.type === "chunk") {

                if (!firstChunkReceived) {

                    botContent.textContent = "";

                    firstChunkReceived = true;
                }

                botContent.textContent += data.text;

                scrollToBottom();

            }

            // Handle errors

            else if (data.type === "error") {

                streamError = data.message;

            }

            // Generation completed

            else if (data.type === "done") {

                completed = true;

            }

        }

        // Continuously read incoming chunks

        while (true) {

            const { value, done } = await reader.read();

            if (done) {
                break;
            }

            buffer += decoder.decode(
                value,
                { stream: true }
            );

            const lines = buffer.split("\n");

            buffer = lines.pop();

            for (const line of lines) {
                processLine(line);
            }

        }

        // Process any remaining buffered data

        buffer += decoder.decode();

        if (buffer.trim()) {
            processLine(buffer);
        }

        if (streamError) {
            throw new Error(streamError);
        }

        if (!completed) {
            throw new Error("The response ended unexpectedly.");
        }

    } catch (error) {

        console.error("Chat Error:", error);

        if (!firstChunkReceived) {

            botContent.textContent =
                "Sorry! " + error.message;

        } else {

            botContent.textContent +=
                "\n\n[Response interrupted: " + error.message + "]";

        }

    } finally {

        // Enable input again

        sendButton.disabled = false;

        userInput.disabled = false;

        userInput.focus();

        scrollToBottom();

    }

}


// -----------------------------------
// 6. SEND MESSAGE USING ENTER KEY
// -----------------------------------

userInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();

    }

});
