import openai
from keys import OPENAI_API_KEY
import speech_recognition as sr

from fusion_hat import LedMatrix
from pathlib import Path
import subprocess
import sys
import os


# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)
os.system("fusion_hat enable_speaker")

# Initialize hardware components
rgb_matrix = LedMatrix(rotate=0)
recognizer = sr.Recognizer()


# Functions for speech-to-text and text-to-speech
def speech_to_text(audio_file):
    """
    Convert speech audio to text using OpenAI Whisper model.
    """
    from io import BytesIO
    wav_data = BytesIO(audio_file.get_wav_data())
    wav_data.name = "record.wav"

    try:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=wav_data,
            language=["zh", "en"]
        )
        return transcription.text
    except Exception as e:
        print(f"Error in Speech-to-Text: {e}")
        return ""


def text_to_speech(text):
    """
    Convert text to speech using OpenAI's TTS model.
    """
    speech_file_path = Path(__file__).parent / "speech.mp3"
    try:
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text
        ) as response:
            response.stream_to_file(speech_file_path)
        p=subprocess.Popen("mplayer speech.mp3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
    except Exception as e:
        print(f"Error in Text-to-Speech: {e}")
        return None


# Redirect ALSA errors to null
def redirect_error_to_null():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    return old_stderr


def cancel_redirect_error(old_stderr):
    os.dup2(old_stderr, 2)
    os.close(old_stderr)


# Create an OpenAI assistant
assistant = client.beta.assistants.create(
    name="Electronic Pet Bot",
    instructions=(
        "You are an electronic pet robot with an 8x8 LED matrix as your face. "
        "When interacting with the user, provide a JSON output with a 'pattern' for the face "
        "and a 'message' for interaction. Example JSON: "
        '{"pattern": [0b00111100, 0b01000010, 0b10100101, 0b10000001, 0b10100101, 0b10011001, 0b01000010, 0b00111100], '
        '"message": "Hello, nice to meet you!"}'
    ),
    model="gpt-4o-mini",
    response_format="auto",
)

# Create a conversation thread
thread = client.beta.threads.create()

try:
    while True:
        print(f'\033[1;30m{"Listening..."}\033[0m')
        old_stderr = redirect_error_to_null()
        with sr.Microphone(chunk_size=8192) as source:
            cancel_redirect_error(old_stderr)
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        print(f'\033[1;30m{"Processing audio..."}\033[0m')
        user_message = speech_to_text(audio)
        if not user_message:
            print("No input detected. Please try again.")
            continue

        # Send the user's message to the assistant
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        # Process the assistant's response
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                if message.role == "assistant":
                    for block in message.content:
                        if block.type == "text":
                            try:
                                response = eval(block.text.value)
                                pattern = response.get("pattern", [])
                                assistant_message = response.get("message", "")
                                if pattern:
                                    rgb_matrix.display_pattern(pattern) 
                                if assistant_message:
                                    print(f"Bot: {assistant_message}")
                                    text_to_speech(assistant_message)
                            except Exception as e:
                                print(f"Error in processing assistant response: {e}")
                    break

finally:
    client.beta.assistants.delete(assistant.id)
    print("Resources cleaned up.")