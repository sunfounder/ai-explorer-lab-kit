import openai
from keys import OPENAI_API_KEY
from pathlib import Path

import readline # optimize keyboard input, only need to import
import sys
import os
import subprocess

from fusion_hat import RGB_LED,PWM

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)
os.system("fusion_hat enable_speaker")

TTS_OUTPUT_FILE = 'tts_output.mp3'


instructions_text = '''
You are a smart lamp assistant. Your role is to respond to user commands by providing two outputs: 
1. A color in RGB format to control the lamp.
2. A textual response to the user.

**Input Format**:
The user will provide a command describing their mood or desired lighting condition in plain text (e.g., "I feel happy" or "Set a relaxing light").

**Output Requirements**:
1. Return a JSON output with no extraneous text or wrappers:
   - `color`: A list of three floating-point values representing the RGB color components (each between 0 and 1).
   - `message`: A textual response to the user.

**Example JSON Output**:
{
  "color": [0.5, 0.4, 0.2],
  "message": "Setting a warm and relaxing light for you."
}
'''


# assistant=client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)
assistant = client.beta.assistants.create(
    name="BOT",
    instructions=instructions_text,
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()

# Initialize an RGB LED.
rgb_led = RGB_LED(PWM('P0'), PWM('P1'), PWM('P2'),common=RGB_LED.CATHODE)



def text_to_speech(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=text
    ) as response:
        response.stream_to_file(speech_file_path)
    p=subprocess.Popen("mplayer speech.mp3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()


try:
    while True:
        msg = ""
        msg = input(f'\033[1;30m{"intput: "}\033[0m').encode(sys.stdin.encoding).decode('utf-8')
        if msg == False or msg == "":
            print() # new line
            continue

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=msg,
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            for message in messages.data:
                if message.role == 'user':
                    for block in message.content:
                        if block.type == 'text':
                            label = message.role 
                            value = block.text.value
                            print(f'{label:>10} >>> {value}')
                    break # only last reply

            for message in messages.data:
                if message.role == 'assistant':
                    for block in message.content:
                        if block.type == 'text':
                            label = assistant.name
                            value = block.text.value
                            # print(f"Raw AI Response: {value}")
                            try:
                                value = eval(value)
                            except Exception as e:
                                value = str(value)
                            if isinstance(value, dict):
                                if 'color' in value:
                                    color = list(value['color'])
                                else:
                                    color = [0,0,0]
                                if 'message' in value:
                                    text = value['message']
                                else :
                                    text = ''
                            else:
                                color = [0,0,0]
                                text = value

                            print(f'{label:>10} >>> {text} {color}')
                            rgb_led.color = color
                            text_to_speech(text)
                    break # only last reply

finally:
    client.beta.assistants.delete(assistant.id)
