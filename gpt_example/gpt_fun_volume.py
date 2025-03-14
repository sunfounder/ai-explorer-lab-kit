#!/usr/bin/env python3

from fusion_hat import ADC, Pin
from time import sleep
import openai
from keys import OPENAI_API_KEY
import sys
import os
import subprocess
from pathlib import Path

import speech_recognition as sr

os.system("fusion_hat enable_speaker")

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)

TTS_OUTPUT_FILE = 'tts_output.mp3'

assistant = client.beta.assistants.create(
    name="BOT",
    instructions="You are a chat bot, you answer people question to help them.",
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()
recognizer = sr.Recognizer()
os.system("fusion_hat enable_speaker")

# speech_recognition init
# =================================================================
'''
recognizer.energy_threshold = 300  # minimum audio energy to consider for recording
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5
recognizer.pause_threshold = 0.8  # seconds of non-speaking audio before a phrase is considered complete
recognizer.operation_timeout = None  # seconds after an internal operation (e.g., an API request) starts before it times out, or ``None`` for no timeout

recognizer.phrase_threshold = 0.3  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
recognizer.non_speaking_duration = 0.5  # seconds of non-speaking audio to keep on both sides of the recording

'''
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1
recognizer.operation_timeout = None  # seconds after an internal operation (e.g., an API request) starts before it times out, or ``None`` for no timeout
recognizer.pause_threshold = 1

def speech_to_text(audio_file):
    from io import BytesIO

    wav_data = BytesIO(audio_file.get_wav_data())
    wav_data.name = "record.wav"

    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=wav_data,
        language=['zh','en']
    )
    return transcription.text

def redirect_error_2_null():
    # https://github.com/spatialaudio/python-sounddevice/issues/11

    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    return old_stderr

def cancel_redirect_error(old_stderr):
    os.dup2(old_stderr, 2)
    os.close(old_stderr)

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

# Set up the potentiometer
pot = ADC('A0')

# Define GPIO pins where LEDs are connected
led_pins = [4, 17, 27, 22, 23, 24, 25, 5, 13, 26]

# Create LED objects for each pin
leds = [Pin(pin, Pin.OUT) for pin in led_pins]


def MAP(x, in_min, in_max, out_min, out_max):
    """
    Map a value from one range to another.
    :param x: The value to be mapped.
    :param in_min: The lower bound of the value's current range.
    :param in_max: The upper bound of the value's current range.
    :param out_min: The lower bound of the value's target range.
    :param out_max: The upper bound of the value's target range.
    :return: The mapped value.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def set_volume(percent):
    """set volume (0-100%)"""
    for led in leds:
        led.low()
    for i in range(int(percent/10)):
        leds[i].high()
    os.system(f"amixer set Master {percent}%")

def is_mplayer_running():
    """check if mplayer is running"""
    result = subprocess.run(["pgrep", "-x", "mplayer"], stdout=subprocess.PIPE)
    return result.returncode == True  

try:
    while True:
        # Check if mplayer is running, if not, start recording
        if not is_mplayer_running():
            msg = ""
            print(f'\033[1;30m{"listening... "}\033[0m')
            _stderr_back = redirect_error_2_null() 
            with sr.Microphone(chunk_size=8192) as source:
                cancel_redirect_error(_stderr_back)
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
            print(f'\033[1;30m{"stop listening... "}\033[0m')

            # Convert recorded audio to text
            msg = speech_to_text(audio)

            if msg == False or msg == "":
                print() # new line
                continue

            # Pass the transcribed text to the chatbot
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=msg,
            )

            # Generate and process the assistant's response
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )

            # print("Run completed with status: " + run.status)
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
                                print(f'{label:>10} >>> {value}')
                                text_to_speech(value)
                        break # only last reply

        # Map the ADC value to a range suitable for setting LED brightness
        volume = MAP(pot.read(), 0, 4095, 0, 100)
        # print('current volume = %d ' %(result))
        set_volume(volume)    
        sleep(0.2)

finally:
    client.beta.assistants.delete(assistant.id)
    for led in leds:
        led.low()