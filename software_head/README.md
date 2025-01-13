# Software of the Little Brother Project

## Structure

This project is made of individual software components that are designed to work together. Each component is a separate docker container that can be run independently. The components are:
- core: The core component that aggregates the data from the other components and hosts the web interface.
- commands: The component that listens for commands to send to the cable-driven system.
- speech-to-text: The component that listens for speech and converts it to text.
- text-to-command: The component that listens for text and converts it to structured commands.
- vision: Reads the camera feed and sends it to the YoloV8 API

All the components communicate using redis

The code running on the cable-driven system side is in the `remote` folder. It is a simple python script that listens for commands and sends them to the cable-driven system, as well as servers the YoloV8 API.

## Running the software

To run the software, you need to have docker and docker-compose installed. Then, you can run the following command on the head computer:

```bash
docker-compose up --build
```

On the cable-driven system, you can run the following command:

```bash
docker build -t remote remote && docker run --network host remote
```
