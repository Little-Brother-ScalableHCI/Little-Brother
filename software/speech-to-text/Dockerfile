FROM python:3.10

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libasound-dev \
        libportaudio2 \
        portaudio19-dev

RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "main.py"]
