from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch
import numpy as np
from PIL import Image, ImageOps
import io
import cv2

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and processor once on startup
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess input PIL image to match TrOCR handwritten model input requirements:
    - Convert to grayscale
    - Resize to 384x384 keeping aspect ratio with padding
    - Enhance contrast
    - Normalize pixel values handled by processor
    """

    # Convert to grayscale
    gray_image = ImageOps.grayscale(image)

    # Resize to 384x384 keeping aspect ratio, add padding if needed
    desired_size = 384
    old_size = gray_image.size  # (width, height)

    ratio = float(desired_size) / max(old_size)
    new_size = tuple([int(x * ratio) for x in old_size])
    resized_image = gray_image.resize(new_size, Image.LANCZOS)

    # Create new image and paste the resized on center to get 384x384
    new_image = Image.new("L", (desired_size, desired_size), color=255)  # white background
    paste_position = ((desired_size - new_size[0]) // 2, (desired_size - new_size[1]) // 2)
    new_image.paste(resized_image, paste_position)

    # Convert PIL image to OpenCV image for further processing
    cv_image = np.array(new_image)

    # Apply adaptive threshold to get sharper text
    cv_image = cv2.adaptiveThreshold(cv_image, 255,
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY,
                                     11,
                                     2)

    # Convert back to PIL Image
    final_image = Image.fromarray(cv_image)

    return final_image

@app.post("/ocr")
async def recognize_handwriting(file: UploadFile = File(...)):
    # Check valid content type
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        # Read uploaded file bytes
        contents = await file.read()

        # Handle PDF separately: convert first page to image
        if file.content_type == "application/pdf":
            import fitz  # PyMuPDF
            pdf_doc = fitz.open(stream=contents, filetype="pdf")
            page = pdf_doc.load_page(0)  # first page
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
        else:
            image = Image.open(io.BytesIO(contents))

        # Preprocess image to enhance handwriting features
        processed_image = preprocess_image(image)

        # Prepare pixel values for model
        pixel_values = processor(images=processed_image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        # Generate text with beam search for better results
        generated_ids = model.generate(pixel_values, num_beams=5, max_length=512, early_stopping=True)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return {"text": generated_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
