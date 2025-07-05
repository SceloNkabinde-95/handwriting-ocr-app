from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os
import io
import time

app = FastAPI()

# Allow CORS (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure credentials
AZURE_KEY = "3zFLhu0ydaMwO8nyu6QiH2Jy7aSF2lxDLKvQJ8x8XtaM9O6ed291JQQJ99BGACrIdLPXJ3w3AAAFACOG1lvo"
AZURE_ENDPOINT = "https://stratylens.cognitiveservices.azure.com/"

client = ComputerVisionClient(
    AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_KEY)
)

@app.post("/ocr")
async def ocr_with_azure(file: UploadFile = File(...)):
    image_data = await file.read()

    # Send to Azure Read API
    read_response = client.read_in_stream(io.BytesIO(image_data), raw=True)
    operation_location = read_response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    # Poll until operation completes
    while True:
        result = client.get_read_result(operation_id)
        if result.status not in ["notStarted", "running"]:
            break
        time.sleep(1)

    # Return recognized text
    if result.status == OperationStatusCodes.succeeded:
        lines = []
        for page in result.analyze_result.read_results:
            for line in page.lines:
                lines.append(line.text)
        return {"text": "\n".join(lines)}
    else:
        return {"error": "OCR failed"}
