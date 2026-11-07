
import os
import uuid
import json
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types


# -----------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# -----------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")


# -----------------------------------
# 2. INITIALIZE GEMINI
# -----------------------------------

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.8-flash"


# -----------------------------------
# 3. CREATE FASTAPI APPLICATION
# -----------------------------------

app = FastAPI(
    title="NeuroNest AI Chatbot",
    description="Streaming AI chatbot powered by Google Gemini",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# -----------------------------------
# 4. SYSTEM PROMPT
# -----------------------------------

SYSTEM_PROMPT = """
You are NeuroNest AI, a friendly and intelligent AI assistant.

Your responsibilities:

1. Answer questions clearly and accurately.
2. Help users understand technical and general topics.
3. Explain complicated concepts in simple language.
4. Maintain a friendly and professional personality.
5. Remember information from earlier messages.
6. Keep answers concise and avoid unnecessary explanations.
7. Give direct answers unless the user requests details.

Always be helpful, respectful and concise.
"""


# -----------------------------------
# 5. CONVERSATION MEMORY
# -----------------------------------

conversations = {}


# -----------------------------------
# 6. REQUEST MODEL
# -----------------------------------

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


# -----------------------------------
# 7. HOME PAGE
# -----------------------------------

@app.get("/")
async def home():
    return FileResponse("templates/index.html")


# -----------------------------------
# 8. STREAMING CHAT FUNCTION
# -----------------------------------

async def stream_chat_response(history, conversation_id):

    # Send conversation ID to frontend

    yield json.dumps({
        "type": "start",
        "conversation_id": conversation_id
    }) + "\n"

    stream = None

    # Retry temporary API errors

    for attempt in range(3):

        try:

            stream = await client.aio.models.generate_content_stream(

                model=MODEL_NAME,

                contents=history,

                config=types.GenerateContentConfig(

                    system_instruction=SYSTEM_PROMPT,

                    thinking_config=types.ThinkingConfig(
                        thinking_level="LOW"
                    ),

                    max_output_tokens=512
                )
            )

            break

        except Exception as error:

            error_message = str(error).upper()

            retryable = any(
                code in error_message
                for code in [
                    "503",
                    "UNAVAILABLE",
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "500",
                    "INTERNAL",
                    "502",
                    "504",
                    "TIMEOUT"
                ]
            )

            if retryable and attempt < 2:

                delay = 2 ** (attempt + 1)

                print(
                    f"Gemini busy. Retrying in {delay} seconds..."
                )

                await asyncio.sleep(delay)

            else:

                print("Gemini API Error:", str(error))

                if retryable:
                    message = (
                        "Gemini is temporarily busy. "
                        "Please try again shortly."
                    )
                else:
                    message = (
                        "Unable to connect to Gemini. "
                        "Please check your API configuration."
                    )

                yield json.dumps({
                    "type": "error",
                    "message": message
                }) + "\n"

                return

    # Receive and forward response chunks

    full_response = []

    try:

        async for chunk in stream:

            text = chunk.text

            if text:

                full_response.append(text)

                yield json.dumps({
                    "type": "chunk",
                    "text": text
                }) + "\n"

        bot_reply = "".join(full_response)

        if not bot_reply:
            yield json.dumps({
                "type": "error",
                "message": "Gemini returned an empty response."
            }) + "\n"

            return

        # Save complete conversation after generation

        conversations[conversation_id] = (
            history + [
                {
                    "role": "model",
                    "parts": [{"text": bot_reply}]
                }
            ]
        )[-10:]

        # Tell frontend generation is complete

        yield json.dumps({
            "type": "done"
        }) + "\n"

    except Exception as error:

        print("Streaming Error:", str(error))

        yield json.dumps({
            "type": "error",
            "message": (
                "The response was interrupted. Please try again."
            )
        }) + "\n"


# -----------------------------------
# 9. CHAT ENDPOINT
# -----------------------------------

@app.post("/chat")
async def chat(request: ChatRequest):

    if not request.message.strip():

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    conversation_id = (
        request.conversation_id or str(uuid.uuid4())
    )

    # Get previous conversation history

    history = conversations.get(
        conversation_id, []
    ).copy()

    # Add current user message

    history.append({
        "role": "user",
        "parts": [
            {"text": request.message}
        ]
    })

    # Context window management:
    # Keep the latest 10 messages

    history = history[-10:]

    # Return streaming response

    return StreamingResponse(

        stream_chat_response(
            history,
            conversation_id
        ),

        media_type="application/x-ndjson",

        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# -----------------------------------
# 10. HEALTH CHECK
# -----------------------------------

@app.get("/health")
async def health():

    return {
        "status": "NeuroNest AI is running!",
        "model": MODEL_NAME,
        "streaming": True
    }


# -----------------------------------
# 11. ABOUT ENDPOINT
# -----------------------------------

@app.get("/about")
async def about():

    return {
        "name": "NeuroNest AI",
        "powered_by": "Google Gemini",
        "framework": "FastAPI",
        "streaming": True,
        "version": "1.0.0"
    }
