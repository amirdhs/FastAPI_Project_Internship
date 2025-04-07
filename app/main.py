from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import app.schemas as schemas
import app.database as database
import app.models as models
import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch API configurations from .env
EMOTION_API_URL = os.getenv("EMOTION_API_URL")
EMOTION_API_KEY = os.getenv("EMOTION_API_KEY")

app = FastAPI()

# Initialize the database tables
models.Base.metadata.create_all(bind=database.engine)


# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Rule-based response generator based on emotion
def generate_response(emotion: str) -> str:
    responses = {
        "happy": "I'm glad to hear that!",
        "sad": "I'm here for you. It’s okay to feel sad sometimes.",
        "angry": "Take a deep breath. Want to talk about it?",
        "neutral": "I see. Tell me more.",
    }
    return responses.get(emotion.lower(), "Thanks for sharing how you feel.")


# External emotion detection (using API from apilayer)
async def detect_emotion(message: str) -> str:
    if not EMOTION_API_URL or not EMOTION_API_KEY:
        raise HTTPException(status_code=500, detail="Emotion API credentials not configured.")

    headers = {"apikey": EMOTION_API_KEY}
    payload = {"text": message}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(EMOTION_API_URL, headers=headers, json=payload)

            # Check if the API returned a successful response
            response.raise_for_status()
            data = response.json()

            # If the API returns an empty or invalid response, raise an error
            if not data or not isinstance(data, dict):
                raise HTTPException(status_code=500, detail="Invalid response from Emotion API.")

            # Find the emotion with the highest score
            emotion = max(data, key=data.get)

            return emotion

    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=500, detail=f"Emotion API returned an error: {http_err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"An error occurred while detecting emotion: {err}")


# Endpoint to handle conversations
@app.post("/conversation", response_model=schemas.ConversationOutput)
async def create_conversation(input_data: schemas.ConversationInput, db: Session = Depends(get_db)):
    # Detect the emotion of the user's message using the external API
    emotion = await detect_emotion(input_data.message)

    # Generate a rule-based response based on the detected emotion
    bot_response = generate_response(emotion)

    # Store the conversation in the database
    conversation = models.Conversation(
        user_message=input_data.message,
        emotion=emotion,
        bot_response=bot_response
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # Return the emotion and the response generated by the bot
    return {"emotion": emotion, "response": bot_response}
