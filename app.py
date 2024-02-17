from flask import Flask, request, render_template, send_file
import cv2
from captcha_solver import solve_captcha

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and "image" in request.files:
        image = request.files['image']
        img = cv2.imdecode(image.read(), cv2.IMREAD_COLOR)

        annotated = solve_captcha(img, "traffic light")

        return send_file(annotated, mimetype='image') 
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=False)