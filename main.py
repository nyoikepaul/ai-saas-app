import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

def call_gemini_with_fallback(prompt: str):
    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
    
    for model_name in models_to_try:
        try:
            print(f"Attempting with {model_name}...")
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "404" in error_msg:
                print(f"Model {model_name} unavailable. Trying next...")
                continue
            return f"AI Error: {error_msg}"
    
    return "All models are currently busy. Please try again in 60 seconds."

@app.post("/api/chat")
async def chat(request: ChatRequest):
    print(f"Received message: {request.message}")
    reply = call_gemini_with_fallback(request.message)
    return {"reply": reply}

@app.get("/")
def home():
    return {"status": "Server is running"}
