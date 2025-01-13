FROM python:3.10

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

RUN python -m spacy download en_core_web_sm

CMD ["python", "-u", "main.py"]
