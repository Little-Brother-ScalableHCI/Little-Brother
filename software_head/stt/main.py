import pickle
import redis
import whisper
import sounddevice as sd
import numpy as np
import time
import logging
import concurrent.futures
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    WAKE_WORD: str = "hello, little brother"
    AUDIO_DURATION: int = 3
    SAMPLE_RATE: int = 16000
    SILENCE_THRESHOLD: float = 0.01
    SILENCE_DURATION: int = 3
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    WHISPER_MODEL: str = "base"

class AudioState:
    def __init__(self):
        self.is_active = False
        self.last_sound_time = time.time()
        self.consecutive_silence = 0

    def activate(self):
        self.is_active = True
        self.last_sound_time = time.time()
        self.consecutive_silence = 0

    def deactivate(self):
        self.is_active = False
        self.consecutive_silence = 0

class AudioProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.logger = self._setup_logging()
        self.state = AudioState()
        self.model = self._init_whisper()
        self.redis_client = self._init_redis()
        self.audio_buffer = []

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def _init_whisper(self):
        try:
            return whisper.load_model(self.config.WHISPER_MODEL)
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            raise

    def _init_redis(self):
        try:
            return redis.Redis(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                db=self.config.REDIS_DB
            )
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise

    def detect_silence(self, audio_data: np.ndarray) -> bool:
        rms = np.sqrt(np.mean(np.square(audio_data)))
        return rms < self.config.SILENCE_THRESHOLD

    def is_wake_word(self, text: str) -> bool:
        return self.config.WAKE_WORD.lower() in text.lower()

    def _record_audio(self) -> np.ndarray:
        recording = sd.rec(
            int(self.config.AUDIO_DURATION * self.config.SAMPLE_RATE),
            samplerate=self.config.SAMPLE_RATE,
            channels=1
        )
        sd.wait()
        return recording.flatten()

    def _process_transcription(self, audio_data: np.ndarray) -> Optional[str]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.model.transcribe, audio_data)
            try:
                result = future.result(timeout=10)
                return result["text"].strip()
            except concurrent.futures.TimeoutError:
                self.logger.warning("Transcription timed out")
                return None

    def _handle_active_audio(self, text: str):
        if text:
            self.logger.info(f"Transcribed: {text}")
            try:
                self.redis_client.set("speech-to-text", pickle.dumps(text))
                self.redis_client.publish("speech-to-text", pickle.dumps(text))
            except Exception as e:
                self.logger.error(f"Failed to send to Redis: {e}")

    def run(self):
        self.logger.info("Waiting for wake word...")
        
        try:
            while True:
                audio_data = self._record_audio()
                is_silent = self.detect_silence(audio_data)

                if not self.state.is_active:
                    text = self._process_transcription(audio_data)
                    if text and self.is_wake_word(text):
                        self.state.activate()
                        self.logger.info("🎯 Activated! I'm listening...")
                    continue

                if is_silent:
                    self.state.consecutive_silence += 1
                    if self.state.consecutive_silence >= self.config.SILENCE_DURATION:
                        self.state.deactivate()
                        self.logger.info("😴 Deactivated due to silence")
                        continue
                else:
                    self.state.consecutive_silence = 0
                    text = self._process_transcription(audio_data)
                    if text:
                        self._handle_active_audio(text)

        except KeyboardInterrupt:
            self.logger.info("Stopping...")
        finally:
            self.redis_client.close()

def main():
    config = Config()
    processor = AudioProcessor(config)
    processor.run()

if __name__ == "__main__":
    main()
