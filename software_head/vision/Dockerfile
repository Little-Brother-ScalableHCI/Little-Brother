FROM balenalib/raspberrypi4-64-python:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends libcamera-dev

# Install necessary Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the streaming script
COPY main.py .

# Expose the streaming port
EXPOSE 8554

# Run the streaming script
CMD ["python3", "main.py"]
