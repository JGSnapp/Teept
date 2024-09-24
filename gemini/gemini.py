import json 
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import base64
import os
import uuid

app = Flask(__name__)
CORS(app)  # Allow CORS for all domains

# Configure the API key for Google Generative AI
genai.configure(api_key=os.environ.get('AIzaSyDipOKGuljWqghEizRH3Q4WGfWxnClZ3BE'))

UPLOAD_IMAGE_FOLDER = 'uploaded_images'
os.makedirs(UPLOAD_IMAGE_FOLDER, exist_ok=True)

def get_image_answer(image_path, file_name, task):
    # Upload the file to Gemini API
    sample_file = genai.upload_file(path=image_path, display_name=file_name)
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")

    # Choose a Gemini API model
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    # Construct the prompt
    prompt = f"""
You are given an image and a task.

The image is provided as input.

The task is: {task}

Please analyze the image to find the button or interface element that can help accomplish the task.

Provide a JSON response with two fields: 'about' and 'action'.

In 'about', write a few words about the appearance of the button and its position.

In 'action', give instructions on what I should do with this button to accomplish the task.

Output only the JSON response.

Ensure the JSON is valid and properly formatted.

Example:

{{
    "about": "The button is a blue rectangle located at the top right corner.",
    "action": "Click on the blue 'Open Browser' button to launch the web browser."
}}
"""

    # Generate content with the image and prompt
    response = model.generate_content([sample_file, prompt])

    # Parse the response as JSON
    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        result = {"error": "Invalid JSON response", "raw_response": response.text}

    return result

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    photo_data = data.get('photo')
    task = data.get('task')

    if photo_data and task:
        # Decode the base64 image
        photo = base64.b64decode(photo_data)

        # Save the image to the server
        file_name = f"{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_IMAGE_FOLDER, file_name)
        with open(file_path, 'wb') as file:
            file.write(photo)
        print(f"Saved image at: {file_path}")

        # Get the response from Gemini API
        result = get_image_answer(file_path, file_name, task)

        # Delete the file after processing
        os.remove(file_path)
        print(f"Deleted image at: {file_path}")

        return jsonify(result)

    return jsonify({'status': 'error', 'message': 'Invalid request or missing photo/task'}), 400

if __name__ == '__main__':
    app.run(debug=True)
