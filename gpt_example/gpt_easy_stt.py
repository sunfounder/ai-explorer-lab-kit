import openai
from keys import OPENAI_API_KEY
import readline # optimize keyboard input, only need to import
import sys
import os
import subprocess
from pathlib import Path

import speech_recognition as sr

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


try:
    while True:
        msg = ""
        # Notify user that recording has started
        print(f'\033[1;30m{"listening... "}\033[0m')
        # Redirect error messages to suppress ALSA warnings
        _stderr_back = redirect_error_2_null() 
        with sr.Microphone(chunk_size=8192) as source:
            # Restore standard error output
            cancel_redirect_error(_stderr_back)
            # Adjust for ambient noise to filter background sound
            recognizer.adjust_for_ambient_noise(source)
            # Record user speech
            audio = recognizer.listen(source)
        print(f'\033[1;30m{"stop listening... "}\033[0m')

        # Optional: Save and playback the recorded audio for debugging
        # This is for testing purposes and can be removed in production
        with open("stt-rec.wav", "wb") as f:
            f.write(audio.get_wav_data())
        os.system('play stt-rec.wav')

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

finally:
    client.beta.assistants.delete(assistant.id)


