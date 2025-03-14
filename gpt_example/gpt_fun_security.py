import openai
from keys import OPENAI_API_KEY
from fusion_hat import Pin
from pathlib import Path
import subprocess
import os

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)
# thread = client.beta.threads.create()
os.system("fusion_hat enable_speaker")

# Initialize sensors
reed_switch = Pin(17, Pin.IN, pull=Pin.PULL_UP)
motion_sensor = Pin(22, Pin.IN, pull=Pin.PULL_DOWN)

# Function for text-to-speech conversion and play the speech
def text_to_speech(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    try:
        with client.audio.speech.with_streaming_response.create(
            model="tts-1", voice="alloy", input=text
        ) as response:
            response.stream_to_file(speech_file_path)
        # Play the generated speech file
        subprocess.Popen(
            ["mplayer", str(speech_file_path)],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
         ).wait()
    except Exception as e:
        print(f"Error in TTS or playing the file: {e}")

# Sensor event handlers
def door_opened():
    print("Door was opened!")
    text_to_speech("Attention! The door was opened.")

def motion_detected():
    print("Motion detected!")
    text_to_speech("Warning! Motion detected.")

# Assign event handlers
reed_switch.when_deactivated = door_opened
motion_sensor.when_activated = motion_detected

# Keep the script running
try:
    print("System is active. Monitoring...")
    import signal
    signal.pause()  # Use signal.pause() on Unix to keep the script running
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    print("Cleaning up resources.")
