from fastapi import FastAPI, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from speech.audio_service import handle_file_from_user
from pydantic import BaseModel
from rasa_service import rasa_response
import audioread

app = FastAPI()

# Initialize templates for rendering HTML
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_audio_format(file_content):
    # Check the format of the audio file
    with audioread.audio_open(file_content) as f:
        format_name = f.format_name.lower()
    return format_name


class Message(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    # Load and render the HTML content from the index.html file
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chatbot_response")
async def chatbot_response(message: Message):
    message = message.message
    output_message = await rasa_response(message)
    print("output_message >>", output_message["message"])
    return output_message["message"]

@app.post("/audio_message")
async def handle_receive_audio_data(audio_file:UploadFile):
    file_data = await audio_file.read()
    generated_ai_audio_file_path = await handle_file_from_user(file=file_data)
    return FileResponse(generated_ai_audio_file_path, media_type="audio/wav", filename="ai_output")