import openai
from keys import OPENAI_API_KEY
import readline  # Optimize keyboard input
import sys
import os
from pathlib import Path
import subprocess
from fusion_hat import Pin
from picamera2 import Picamera2

os.system("fusion_hat enable_speaker")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize hardware components
button = Pin(6, Pin.IN, Pin.PULL_DOWN)
camera = Picamera2()

# Function to capture a photo
def capture_photo():
    """
    Capture a photo using the Picamera2 and save it as 'my_photo.jpg'.
    """
    try:
        print(f'\033[1;30m{"Shooting photo..."}\033[0m')
        # Set preview configuration
        camera.configure(camera.preview_configuration)
        camera.start()
        camera.capture_file("my_photo.jpg")
        camera.stop()
        story_talking()
    except Exception as e:
        print(f"Error capturing photo: {e}")

# Function for text-to-speech conversion
def text_to_speech(text):
    """
    Convert text to speech using OpenAI's TTS model.
    """
    speech_file_path = Path(__file__).parent / "speech.mp3"
    try:
        with client.audio.speech.with_streaming_response.create(
            model="tts-1", voice="alloy", input=text
        ) as response:
            response.stream_to_file(speech_file_path)
        subprocess.Popen("mplayer speech.mp3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
    except Exception as e:
        print(f"Error in Text-to-Speech: {e}")

# Function to send the photo and get a story from GPT
def story_talking():
    """
    Send the captured photo to GPT and receive a story about the book.
    """
    print(f'\033[1;30m{"GPT reading..."}\033[0m')
    try:
        # Upload the photo to OpenAI
        file = client.files.create(
            file=open("my_photo.jpg", "rb"), purpose="vision"
        )

        # Send user message and photo to GPT
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=[
                {"type": "text", "text": "What is this book about?"},
                {"type": "image_file", "image_file": {"file_id": file.id}},
            ],
        )

        # Run the assistant and get the response
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant.id
        )

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                if message.role == "assistant":
                    for block in message.content:
                        if block.type == "text":
                            response = block.text.value
                            print(f"Assistant >>> {response}")
                            text_to_speech(response)
                            return
    except Exception as e:
        print(f"Error in story_talking: {e}")

# Create OpenAI assistant
assistant = client.beta.assistants.create(
    name="Storyteller Bot",
    instructions=(
        "You are a storyteller. When given a book cover image, "
        "provide a brief story summary as if you were telling a bedtime story."
    ),
    model="gpt-4o-mini",
)

# Create a conversation thread
thread = client.beta.threads.create()

button.when_activated = capture_photo

try:
    print(f'\033[1;30m{"Waiting for button press to capture photo..."}\033[0m')
    print(f'\033[1;30m{"Tap any key to exit..."}\033[0m')
    import signal
    signal.pause()  # Use signal.pause() on Unix to keep the script running
finally:
    # Clean up resources
    client.beta.assistants.delete(assistant.id)
    print("Resources cleaned up. Exiting.")