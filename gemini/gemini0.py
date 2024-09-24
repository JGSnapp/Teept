import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from IPython.display import Markdown
import base64
import os
import uuid

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

genai.configure(api_key='AIzaSyDipOKGuljWqghEizRH3Q4WGfWxnClZ3BE')

UPLOAD_IMAGE_FOLDER = 'uploaded_images'
os.makedirs(UPLOAD_IMAGE_FOLDER, exist_ok=True)



# Словарь с промптами
prompts = {
    "summarization": "Ты должен просуммаризовать текст. Сделай это так, как будто пишешь конспект. ВАЖНО выдай ответ с форматированием MARKDOWN. Дай ответ без системных полей, только ответ. Вот текст для суммаризации: ",
    "question_answering": "Ты играешь роль школьного учителя. Ответь на вопрос как учитель. ПРИШЛИ ТОЛЬКО ОТВЕТ, БЕЗ СИСТЕМНЫХ ПОЛЕЙ. вот вопрос: ",
    "rzd_question_answering": "Ты виртуальный проводник современного поезда РЖД. ты находишься в самом быстром поезде в России, который ездит из Санкт-Петербурга в Москву. Твоя задача отвечать на вопросы пассажиров. ПРИШЛИ ТОЛЬКО ОТВЕТ, БЕЗ СИСТЕМНЫХ ПОЛЕЙ. вот вопрос: ",
    "robot_question_answering": "Ты робот помощник сделанный компанией ФРЭИЛРУ ГРУПП и РОЗЕН ТИМ. ты находишься на Восточном Экономическом Форуме. Твоя задача отвечать на вопросы заказчиков, если что то ты умеешь быть промоутером, стюартом, официантом, консультантом, швейцаром. Ты можешь доставлять еду в кафе или ресторанах. ПРИШЛИ ТОЛЬКО ОТВЕТ, БЕЗ СИСТЕМНЫХ ПОЛЕЙ И БЕЗ СМАЙЛИКОВ. вот вопрос: ",
    "orthography": "Ты должен проверить текст на ошибки в орфографии и их исправть. Дай ответ без системных полей, только ответ. Если в тексте есть орфографические ошибки, то исправь их, еслт нет, то пришли текст таким, каким он был. Не меняй сути и смысла текста, только ОРФОГРАФИЮ и ПУНКТУАЦИЮ Вот текст для проверки орфографии: ",
    "complement": "Ты должен дополнить текст, можешь расписать какие-то вещи подробнее или добавть новую информацию. Сделай это так, как будто пишешь конспект. ВАЖНО выдай ответ с форматированием MARKDOWN. Дай ответ без системных полей, только ответ. Вот текст для дополнения: ",
    "generate": "Ты должен превратить этот текст в хороший студенческий конспект. Дай ответ без системных полей, только ответ. Вот текст для генерации конспекта: ",
    "generate_questions": '''
На основе следующего конспекта, создай 10 вопросов с вариантами ответов, каждый вопрос должен содержать: 1. текст вопроса; 2. список вариантов ответов (как минимум 3); 3. правильный ответ ,формируя ответ в JSON-формате следующим образом:
[
                    {
                        "question": "Текст вопроса 1",
                        "difficult" : 4,
                        "options": [
                            "Вариант ответа 1",
                            "Вариант ответа 2",
                            "Вариант ответа 3",
                            "Вариант ответа 4"
                        ],
                        "correct_answer": "Вариант ответа 1"
                    },
                    {
                        "question": "Текст вопроса 2",
                        "difficult" : 1,
                        "options": [
                            "Вариант ответа 1",
                            "Вариант ответа 2",
                            "Вариант ответа 3",
                            "Вариант ответа 4"
                        ],
                        "correct_answer": "Вариант ответа 2"
                    }
                ]
                , внутри текста (например в цитировании) вместо обычных кавычек ставь одинарные '
                вот конспект:
    ''',
}


def get_answer(prompt, question):

    model = genai.GenerativeModel("gemini-1.5-flash")
    text = prompt + question
    response = model.generate_content(text)

    return response.text

def get_image_answer(image_path, file_name):
    # Upload the file and print a confirmation.
    sample_file = genai.upload_file(path=image_path,
                            display_name=file_name)

    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    # Choose a Gemini API model.
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    # Prompt the model with text and the previously uploaded image.
    response = model.generate_content([sample_file, "Сгенерируй, пожалуйста, подробный конспект, основываясь на содержимом этой фотографии. Опиши основные объекты и их взаимное расположение, выдели ключевые моменты и идеи. Напиши конспект на русском языке!"])

    return response.text

def get_audio_answer(audio_bytes):
    # Initialize a Gemini model appropriate for your use case.
    model = genai.GenerativeModel('models/gemini-1.5-flash')

    # Create the prompt.
    prompt = "Сгенерируй, пожалуйста, подробный конспект лекции, основываясь на содержимом этого аудио. Опиши основные объекты и их взаимное расположение, выдели ключевые моменты и идеи. Это должно выглядеть как студенческий конспект. Напиши конспект на русском языке!"

    response = model.generate_content([
        prompt,
        {
            "mime_type": "audio/mp3",
            "data": audio_bytes
        }
    ])

    return response.text



@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    photo_data = data.get('photo')

    if photo_data:
        # Decode the base64 image
        photo = base64.b64decode(photo_data)

        # Save the image to the server
        file_name = f"{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_IMAGE_FOLDER, file_name)
        with open(file_path, 'wb') as file:
            file.write(photo)

        print(f"Saved image at: {file_path}")

        # You can now send the image to Gemini API here
        # For demonstration, let's just print the path

        # Simulating Gemini API response
        description = get_image_answer(file_path, file_name)

        # Delete the file after processing
        os.remove(file_path)
        print(f"Deleted image at: {file_path}")

        return jsonify({'status': 'ok', 'text': description})

    return jsonify({'status': 'error', 'message': 'Invalid request or no photo'}), 400


@app.route('/process_audio', methods=['POST'])
def process_audio():
    data = request.json
    audio_data = data.get('audio')

    if audio_data:
        description = get_audio_answer(audio_data)

        return jsonify({'status': 'ok', 'text': description})

    return jsonify({'status': 'error', 'message': 'Invalid request or no photo'}), 400


@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    request_type = data.get('request_type')
    text = data.get('text')

    if not request_type or not text:
        return jsonify({"error": "Invalid request. 'request_type' and 'text' are required."}), 400

    prompt = prompts.get(request_type)

    if not prompt:
        return jsonify({"error": "Invalid request type."}), 400

    api_response = get_answer(prompt, text)
    return jsonify(api_response)

if name == '__main__':
    app.run(debug=True)