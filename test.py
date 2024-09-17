import requests
import os

# Set your API key (make sure it's the same as the one used in your FastAPI server)
API_KEY = os.getenv("API_KEY")

def annotate_image(file_path):
    # Define the URL with the API key as a query parameter
    url = f'http://127.0.0.1:8000/process_image?api_key={API_KEY}'

    # Extract the original file name without extension
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)

    # Open the image file and send it to the FastAPI server
    with open(file_path, 'rb') as f:
        files = {'file': f}
        # Remove headers as we now pass the API key in the URL
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
        try:
            # Attempt to parse JSON response if available
            error_details = response.json()
        except ValueError:
            # Handle case where the response is not JSON (e.g., HTML error pages)
            error_details = response.text

        print(f"Error: {response.status_code}, {error_details}")

# Test the function with your image file path
annotate_image('test-images/1.png')
