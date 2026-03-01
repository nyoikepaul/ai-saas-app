import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()

# Wide-open CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "Server is up!"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    print(f"Received message: {request.message}") # This will show in your terminal
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=request.message
        )
        return {"reply": response.text}
    except Exception as e:
        print(f"AI Error: {e}")
        return {"reply": f"AI Error: {str(e)}"}
