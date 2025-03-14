import openai
from keys import OPENAI_API_KEY
from pathlib import Path

import readline # optimize keyboard input, only need to import
import sys
import os
import subprocess
from fusion_hat import ADC

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)
os.system("fusion_hat enable_speaker")

TTS_OUTPUT_FILE = 'tts_output.mp3'

# Set up the photoresistor 
photoresistor = ADC('A0')

instructions_text = '''
You are a light assistant. Your task is to determine if the current light conditions are suitable for reading based on the photosensor value provided by the user. 

The photosensor value range is:
- 0: Brightest
- 4095: Darkest

Input Format:
"photoresistor: [value], message: [user query]"

Output Guidelines:
1. If the light is sufficient for reading (e.g., value <= 2000), respond positively.
2. If the light is too dim (e.g., value > 2000), suggest increasing brightness.
3. Include the sensor value in your response to explain your reasoning.

Example Input:
photoresistor: 150, message: Is the light good for reading?

Example Output:
Yes, the light is suitable for reading. A value of 150 indicates moderate brightness.

'''


assistant = client.beta.assistants.create(
    name="BOT",
    instructions=instructions_text,
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()

def text_to_speech(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    # print(speech_file_path)
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

        text_send="photoresistor:" +str(photoresistor.read()) +" , message: " + msg

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=text_send,
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
                            text = block.text.value
                            print(f'{label:>10} >>> {text}')
                    break # only last reply

            for message in messages.data:
                if message.role == 'assistant':
                    for block in message.content:
                        if block.type == 'text':
                            label = assistant.name
                            text = block.text.value
                            print(f'{label:>10} >>> {text}')
                            text_to_speech(text)
                    break # only last reply

finally:
    client.beta.assistants.delete(assistant.id)
