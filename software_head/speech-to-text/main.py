
import pickle

import redis
import speech_recognition as sr


#* ############################################################################
#* Speech-to-Text function
#* ############################################################################


def main():
    db = redis.Redis(host="redis", port=6379, db=0)

    while True:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening for audio...")
            audio = recognizer.listen(source)

        try:
            # Uses Google Web Speech API (requires internet)
            text_input = recognizer.recognize_google(audio)
            print("You said: ", text_input)
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            continue
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            continue

        if not text_input:
            continue

        db.set("speech-to-text", pickle.dumps(text_input))
        db.publish("speech-to-text", pickle.dumps(text_input))

if __name__ == "__main__":
    main()
