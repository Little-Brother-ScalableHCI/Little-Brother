FROM python:3.10

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libasound-dev \
        libportaudio2 \
        portaudio19-dev

RUN pip install -r requirements.txt

RUN apt-get install -y --no-install-recommends flac

COPY . /app

CMD ["python", "-u", "main.py", "&>", "/dev/null"]
