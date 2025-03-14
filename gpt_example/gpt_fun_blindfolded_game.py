import openai
from keys import OPENAI_API_KEY
import time
from fusion_hat import Pin, ADC
import sys, os
import subprocess
from pathlib import Path
import random

# Initialize the OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

assistant = client.beta.assistants.create(
    name="BOT",
    instructions="This is a blindfolded watermelon-smashing game. A point representing a watermelon is randomly generated within a 20x20 meter area with coordinates ranging from (-10,-10) to (10,10). The player starts from the origin (0,0) and moves using a joystick. Even if the player can't see anything, they press a button to perform a smash action. After smashing, you will receive the watermelon's and player's coordinates. You need to advise the player on the direction of the watermelon, like 'The watermelon is ten meters to your northeast.' If the smash coordinates match, the game ends. Your responses will be converted into speech via TTS, so please keep them brief, ideally within two sentences.",
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()
os.system("fusion_hat enable_speaker")

# Setup GPIO ports
btn_pin = Pin(17, Pin.IN, Pin.PULL_UP)
x_axis = ADC('A1')
y_axis = ADC('A0')

def MAP(x, in_min, in_max, out_min, out_max):
    """
    Map a value from one range to another.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def text_to_speech(text):
    """
    Convert text to speech and play it using an external player.
    """
    speech_file_path = Path(__file__).parent / "speech.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",  # Low-latency TTS model for real-time usage
        voice="alloy",  # Selected voice for audio playback
        input=text  # Text to convert to speech
    ) as response:
        response.stream_to_file(speech_file_path)  # Save audio to the specified file
    p = subprocess.Popen("mplayer speech.mp3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()

def activate():
    global smash_tips
    smash_tips = True
        
watermelon_x, watermelon_y = random.randint(-10, 10), random.randint(-10, 10)
player_x, player_y = 0, 0
btn_pin.when_activated = activate

try:
    text_to_speech("game start!")
    smash_tips = True
    # Main loop to read and print ADC values and button state
    while True:
        x_val = MAP(x_axis.read(), 0, 4095, -100, 100)
        y_val = MAP(y_axis.read(), 0, 4095, -100, 100)
        if x_val > 80:
            player_x += 1
        elif x_val < -80:
            player_x -= 1
        if y_val > 80:
            player_y += 1
        elif y_val < -80:
            player_y -= 1

        print('Watermelon position: %d, %d  ' % (watermelon_x, watermelon_y))
        print('Player position: %d, %d  ' % (player_x, player_y))

        time.sleep(0.3)

        if smash_tips:
            smash_tips = False
            print("Smash!")
            send_message = f"Watermelon position: ({watermelon_x}, {watermelon_y}), Player position: ({player_x}, {player_y})"

            try:
                message = client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=send_message,
                )

                run = client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id,
                    assistant_id=assistant.id,
                )

                if run.status == "completed":
                    messages = client.beta.threads.messages.list(thread_id=thread.id)

                    for message in messages.data:
                        if message.role == 'assistant':
                            for block in message.content:
                                if block.type == 'text':
                                    decoded_message = block.text.value
                            break  # Only take the last reply

                print("Assistant:", decoded_message)
                text_to_speech(decoded_message)
                if (player_x, player_y) == (watermelon_x, watermelon_y):
                    print("Target hit!")
                    break
            except Exception as e:
                print(f"Error in AI processing: {e}")
    print("Good Game. Bye!")

finally:
    client.beta.assistants.delete(assistant.id)
    print("\n Delete Assistant ID")