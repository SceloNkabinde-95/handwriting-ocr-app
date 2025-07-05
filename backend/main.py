from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
from pdf2image import convert_from_bytes
from models.trocr_model import extract_text_from_image

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    """
    Receive a file (image or PDF), process with TrOCR, return extracted text.
    """
    contents = await file.read()

    # If PDF, convert each page to image
    if file.filename.lower().endswith(".pdf"):
        images = convert_from_bytes(contents)
        text = "\n\n".join(extract_text_from_image(img) for img in images)
    else:
        image = Image.open(BytesIO(contents)).convert("RGB")
        text = extract_text_from_image(image)

    return {"text": text}
