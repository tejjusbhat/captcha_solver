from ultralytics import YOLO
import cv2

model = YOLO('yolov8n.pt')  # load a pretrained model (trained on the COCO dataset)

def solve_captcha(image, target):
  results = model(image)  # run inference

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
  
  return image


original = cv2.imread('images/2.png')

annotated = solve_captcha(original, "traffic light")

cv2.imshow('annotated', annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()
