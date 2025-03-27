
import openai
from keys import OPENAI_API_KEY
import readline # optimize keyboard input, only need to import
import sys
import os
from time import sleep

import speech_recognition as sr

from fusion_hat import Buzzer,Pin,PWM

os.system("fusion_hat enable_speaker")

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Speech recognizer
recognizer = sr.Recognizer()

def speech_to_text(audio_file):
    from io import BytesIO

    wav_data = BytesIO(audio_file.get_wav_data())
    wav_data.name = "stt_output.wav"

    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=wav_data,
        language=['zh','en']
    )
    return transcription.text

def redirect_error_2_null():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    return old_stderr

def cancel_redirect_error(old_stderr):
    os.dup2(old_stderr, 2)
    os.close(old_stderr)

# Initialize hardware components
buzzer = Buzzer(PWM('P0')) 
led = Pin(17, Pin.OUT)

# Create an OpenAI assistant
instructions_text = (
    "You are a music composition assistant. Based on three given notes, "
    "you must create a melody and provide it as a JSON dictionary. "
    "The JSON must include 'melody' (a list of tuples with notes and durations) "
    "and 'message' (a textual description). Example format: "
    "{\"melody\": [('C#4', 0.2), ('D4', 0.2), (None, 0.2)], \"message\": \"Your melody is ready.\"}"
)

assistant = client.beta.assistants.create(
    name="BOT",
    instructions=instructions_text,
    model="gpt-4o",
)

thread = client.beta.threads.create()

def play_tune(tune):
    """
    Play a musical tune using the buzzer.
    :param tune: List of tuples (note, duration), where each tuple represents a note and its duration.
    """
    for note, duration in tune:
        print(note)  # Output the current note being played
        buzzer.play(note,float(duration))  # Play the note on the buzzer
    buzzer.off()  # Stop playing after the tune is complete
    sleep(1)

try:
    while True:
        # Listen to user input
        led.on()
        print(f'\033[1;30m{"listening... "}\033[0m')
        _stderr_back = redirect_error_2_null() # ignore error print to ignore ALSA errors
        with sr.Microphone(chunk_size=8192) as source:
            cancel_redirect_error(_stderr_back) # restore error print
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        print(f'\033[1;30m{"stop listening... "}\033[0m')
        led.off()

        # Convert audio to text
        msg = ""
        msg = speech_to_text(audio)
        if msg == False or msg == "":
            print("No valid input received.")
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
                            response = block.text.value
                            try:
                                response_dict = eval(response)
                                melody = response_dict.get('melody', [])
                                text = response_dict.get('message', "No message provided.")
                                print(f"{assistant.name:>10} >>>  {text}")
                                play_tune(melody)
                            except Exception as e:
                                print(f"Error processing assistant response: {e}")


                    break # only last reply

finally:
    buzzer.off()
    client.beta.assistants.delete(assistant.id)
