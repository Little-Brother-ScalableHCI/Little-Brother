FROM ultralytics/ultralytics:latest-cpu

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["python","-u", "main.py"]
