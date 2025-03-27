import openai
from keys import OPENAI_API_KEY
import readline  # Optimize keyboard input, only need to import
import sys,os
from pathlib import Path
from fusion_hat import Servo, Pin
import subprocess

os.system("fusion_hat enable_speaker")

# Define correction factor for fine-tuning servo pulse width
CORRECTION = 0.45
MAX_PW = (2.0 + CORRECTION) / 1000
MIN_PW = (1.0 - CORRECTION) / 1000

# Initialize GPIO components
servo = Servo('P0')
led1 = Pin(27, Pin.OUT)
led2 = Pin(22, Pin.OUT)
led1.off()
led2.off()

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Define assistants with specific instructions
assistants = [
    client.beta.assistants.create(
        name="Alloy",
        instructions=(
            "You are a debate team affirmative speaker. You must agree with the "
            "proposed viewpoint, provide reasonable arguments, and respond to opposition "
            "criticism. Each response should start with the phrase 'This is affirmative response #X' "
            "and must be under 100 words."
        ),
        model="gpt-4-1106-preview",
    ),
    client.beta.assistants.create(
        name="Echo",
        instructions=(
            "You are a debate team opposition speaker. You must refute the affirmative's arguments "
            "using logical reasoning and references. Each response should start with the phrase 'This is opposition response #X' "
            "and must be under 100 words."
        ),
        model="gpt-4-1106-preview",
    ),
]

# Text-to-speech function
def text_to_speech(text, player):
    """
    Convert text to speech using OpenAI's TTS model.
    :param text: The text to be converted.
    :param player: The speaker identifier (0 for Alloy, 1 for Echo).
    """
    voice_player = "alloy" if player == 0 else "echo"
    speech_file_path = Path(__file__).parent / "speech.mp3"

    try:
        with client.audio.speech.with_streaming_response.create(
            model="tts-1", voice=voice_player, input=text
        ) as response:
            response.stream_to_file(speech_file_path)
    except Exception as e:
        print(f"Error in TTS: {e}")
        return None
    return speech_file_path

# Debate function
def debate(player, msg):
    """
    Handle the debate flow for a single turn.
    :param player: The current player's identifier (0 for affirmative, 1 for opposition).
    :param msg: The message to send to the assistant.
    :return: The assistant's response as a string.
    """
    assistant = assistants[player]

    try:
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=msg
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant.id
        )

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                if message.role == "assistant" and message.assistant_id == assistant.id:
                    for block in message.content:
                        if block.type == "text":
                            response = block.text.value
                            print(f'{assistant.name} >>> {response}')
                            play_response(response, player)
                            return response
    except Exception as e:
        print(f"Error during debate: {e}")
        return "An error occurred. Please try again."

# Play response function
def play_response(response, player):
    """
    Play the assistant's response through text-to-speech and control hardware.
    :param response: The assistant's response text.
    :param player: The speaker identifier (0 for Alloy, 1 for Echo).
    """
    speech_file_path = text_to_speech(response, player)
    if speech_file_path:
        try:
            # Play the speech and control LEDs/Servo
            servo.value = 0.5 if player == 0 else -0.5
            led1.on() if player == 0 else led1.off()
            led2.on() if player == 1 else led2.off()
            p = subprocess.Popen(
                ["mplayer", str(speech_file_path)],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            p.wait()
        except Exception as e:
            print(f"Error playing response: {e}")

# Create a thread for the debate
thread = client.beta.threads.create()

try:
    print("Start the debate by entering your topic:")
    msg = input(f'\033[1;30m{"Input: "}\033[0m').strip()
    if not msg:
        print("No input provided. Exiting.")
        sys.exit(0)

    for turn in range(6):
        msg = debate(turn % 2, msg)

finally:
    # Cleanup GPIO and OpenAI resources
    servo.angle(0)
    led1.off()
    led2.off()
    for assistant in assistants:
        client.beta.assistants.delete(assistant.id)
    print("Resources cleaned up. Exiting.")
