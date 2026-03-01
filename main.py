import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.api_core import exceptions

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

def call_gemini_with_fallback(prompt: str):
    # Order of models to try (2.0 is newest but most restricted, lite is most available)
    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-lite"]
    
    for model_name in models_to_try:
        try:
            print(f"Attempting with {model_name}...")
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "429" in str(e):
                print(f"Model {model_name} rate limited. Trying next...")
                continue
            return f"Error: {str(e)}"
    
    return "All AI models are currently busy. Please wait 60 seconds and try again."

@app.post("/api/chat")
async def chat(request: ChatRequest):
    print(f"Received message: {request.message}")
    reply = call_gemini_with_fallback(request.message)
    return {"reply": reply}

@app.get("/")
def home():
    return {"status": "Server is running"}
