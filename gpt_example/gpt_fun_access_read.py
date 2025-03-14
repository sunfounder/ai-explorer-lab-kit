from fusion_hat import RC522,Pin
import json
import openai
from keys import OPENAI_API_KEY
from pathlib import Path
import subprocess
import os
import time

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)
# thread = client.beta.threads.create()
os.system("fusion_hat enable_speaker")

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


relay = Pin(17,Pin.OUT)
rc = RC522()
rc.Pcd_start()

users_db = "users.json"  # users database file

# load user data from file
with open(users_db, "r") as file:
    users = json.load(file)

def access_door():
    print("Please place your card to access the door...")
    uid,message = rc.read(2)
    if uid and uid in users:
        # print(f"Access granted to {users[uid]}!")
        relay.high()
        text_to_speech(f"The door is open. Access granted to {users[uid]}!")
        time.sleep(2)
        relay.off()
        return True
    else:
        print("Access denied!")
        text_to_speech("Access denied!")
    return False


while True:
    result=access_door()
    if result:
        break
