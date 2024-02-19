from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
from ultralytics import YOLO
import numpy as np
import base64

app = Flask(__name__)
CORS(app)

model = YOLO('yolov8n.pt')

def solve_captcha(image_data, target):
  nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
  image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

  results = model(image)

  boxes = results[0].boxes.cpu().numpy()

  xyxys = boxes.xyxy
  classes = boxes.cls
  confs = boxes.conf

  for xyxy, cls, conf in zip(xyxys, classes, confs):
    x1, y1, x2, y2 = xyxy
    if model.names[int(cls)] != target or conf < 0.5:
      continue
    label = f'{model.names[int(cls)]} {conf:.2f}'
    image = cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
    image = cv2.putText(image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36,255,12), 2)

  _, img_encoded = cv2.imencode('.jpg', image)
  img_base64 = base64.b64encode(img_encoded).decode('utf-8')

  return img_base64

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    image_data = data['image']
    target = data['target']
    annotated_image = solve_captcha(image_data, target)
    return jsonify({'annotated_image': annotated_image})

@app.route('/')
def index():
    target_options = model.names
    return render_template('index.html', target_options=target_options)


if __name__ == '__main__':
    app.run(debug=True)