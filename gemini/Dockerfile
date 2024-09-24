FROM python:3.9-slim

RUN mkdir /app
WORKDIR /app

RUN pip install json 
RUN pip install flask
RUN pip install flask_cors
RUN pip install google.generativeai

COPY . /app

CMD ["python", "gemini.py"]