import requests
import os

def annotate_image(file_path):
    url = 'http://127.0.0.1:8000/process_image'

    # Extract the original file name without extension
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)

    # Open the image file and send it to the FastAPI server
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the response (annotated image) as name_annotated.jpg
        annotated_file_name = f"{name}_annotated.jpg"
        with open(annotated_file_name, 'wb') as f:
            f.write(response.content)

        # Print success message with the new file name
        print(f"Annotated image saved as {annotated_file_name}")
    else:
        # Print an error message if something went wrong
        print(f"Error: {response.status_code}, {response.json()}")

# Test the function with your image file path
annotate_image('test-images/1.png')
