from flask import Flask, request, render_template, send_file
import cv2
from captcha_solver import solve_captcha

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST' and "image" in request.files:
    file = request.files['image']
    img = cv2.imdecode(file.read() ,cv2.IMREAD_COLOR)

    annotated = solve_captcha(img, "traffic light")

    _, buffer = cv2.imencode('.png', annotated)

    image_bytes = buffer.tobytes()

    return send_file(
      filename_or_fp=None,
      mimetype='image/png',
      attachment_filename='annotated_image.png',
      data=image_bytes
      )
  return render_template('index.html')


if __name__ == "__main__":
  app.run(debug=False)