from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
from ultralytics import YOLO
import numpy as np
import easyocr
import io
import os

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add logging to the API key check function
def check_api_key(api_key: str):
    if api_key.strip() != API_KEY.strip():
        logger.warning("Invalid API key provided")
        raise HTTPException(status_code=401, detail="Invalid API Key")


# Create FastAPI app instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin during development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers, including authorization headers if needed
)

# Initialize the YOLO model
model = YOLO('static/models/yolov8n.pt')

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])  # You can specify more languages if needed

# Retrieve API key from environment variable
API_KEY = os.getenv("API_KEY")

if API_KEY is None:
    raise ValueError("API_KEY environment variable is not set.")

# Define the captcha solving and object detection logic
def find_target(image):
    # Convert image to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = image[0:image.shape[0] // 4, 0:image.shape[1]]  # Use only the top portion of the image
    image = cv2.bitwise_not(image)

    # Use EasyOCR to detect text
    results = reader.readtext(image)

    full_text = " ".join([result[1] for result in results])

    target = ""
    for option in model.names.values():
        if option in full_text:
            target = option
            break

    return target

def solve_captcha(image):
    # Find the target object from the text
    target = find_target(image)

    if target == "":
        return None  # No target found

    # Run YOLO object detection
    results = model(image)

    # Extract bounding boxes, class labels, and confidence scores
    boxes = results[0].boxes.cpu().numpy()
    xyxys = boxes.xyxy
    classes = boxes.cls
    confs = boxes.conf

    # Annotate the image with bounding boxes and labels
    for xyxy, cls, conf in zip(xyxys, classes, confs):
        x1, y1, x2, y2 = xyxy
        if model.names[int(cls)] != target or conf < 0.5:
            continue
        label = f'{model.names[int(cls)]} {conf:.2f}'
        # Draw the bounding box and label on the image
        image = cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        image = cv2.putText(image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 2)

    return image

# Define the route to process the image directly uploaded by the user, with API key in query param
@app.post('/process_image')
async def process_image(file: UploadFile = File(...), api_key: str = Query(...)):
    # Check API key from query parameters
    check_api_key(api_key)

    try:
        # Read the uploaded image file
        file_bytes = await file.read()
        
        # Convert the image bytes to a NumPy array and decode it using OpenCV
        nparr = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError(f"Unable to load image from uploaded file")

        # Solve the captcha and annotate the image
        annotated_image = solve_captcha(image)

        if annotated_image is None:
            raise HTTPException(status_code=400, detail="No target found in the image")

        # Convert the annotated image to a byte stream
        _, img_encoded = cv2.imencode('.jpg', annotated_image)
        img_bytes = img_encoded.tobytes()

        # Return the image as a StreamingResponse
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/jpeg")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Define a test route to check if the API is running successfully, with API key in query param
@app.get('/test')
async def test(api_key: str = Query(...)):
    # Check API key from query parameters
    check_api_key(api_key)

    return {"message": "API is running successfully!"}

# Run the server using uvicorn if needed
if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8080))  # Use the PORT environment variable
    uvicorn.run(app, host="0.0.0.0", port=port)
