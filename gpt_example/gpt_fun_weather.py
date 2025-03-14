import openai
from keys import OPENAI_API_KEY, OPENWEATHER_API_KEY
from pathlib import Path
import sys,os,subprocess
import speech_recognition as sr
import time
import json
import requests
# pip install requests

from fusion_hat import LCD1602  # Import module for interfacing with lcd

os.system("fusion_hat enable_speaker")

# Initialize LCD with I2C address 0x27 and enable backlight
lcd=LCD1602(0x27, 1) 

# LCD Initialization
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# OpenAI Assistant Setup
assistant = client.beta.assistants.create(
    name="Weather Butler",
    instructions=(
        "You are a weather assistant. Based on the provided local weather data, "
        "offer appropriate clothing recommendations in natural language. "
        "Your responses will be converted to speech, so avoid symbols like braces."
    ),
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()
recognizer = sr.Recognizer()

def speech_to_text(audio_file):
    """
    Convert speech audio to text using OpenAI Whisper model.
    """
    from io import BytesIO

    try:
        wav_data = BytesIO(audio_file.get_wav_data())
        wav_data.name = "record.wav"
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=wav_data, language=["zh", "en"]
        )
        return transcription.text
    except Exception as e:
        print(f"Error in speech-to-text: {e}")
        return ""

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

def sox_volume(input_file, output_file):
    """
    Adjust the volume of an audio file using the sox library.
    """
    import sox

    VOLUME_DB=3  # The volume adjustment in decibels (increase by 3 dB)
    try:
        transform = sox.Transformer()
        transform.vol(VOLUME_DB)
        transform.build(input_file, output_file)
        return True 
    except Exception as e:
        print(f"sox_volume err: {e}")
        return False

def text_to_speech(text):
    """
    Convert text to speech using OpenAI TTS model.
    """
    speech_file_path = Path(__file__).parent / "speech.wav"
    speech_file_path_db = Path(__file__).parent / "speech_db.wav"
    try:
        with client.audio.speech.with_streaming_response.create(
            model="tts-1", voice="alloy", input=text, response_format="wav"
        ) as response:
            response.stream_to_file(speech_file_path)
        sox_volume(speech_file_path,speech_file_path_db)
        subprocess.Popen(
            ["mplayer", str(speech_file_path_db)], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        ).wait()
        os.remove(str(speech_file_path))
        os.remove(str(speech_file_path_db))
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

def get_weather(api_key, city):
    """
    Fetch current weather data for a given city.
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status() 
        return response.json()
    
    except requests.RequestException as e:
        print("Error: ", e)

def lcd_print(weather_data):
    """
    Update the LCD display with weather information.
    """
    if not weather_data:
        lcd.clear()
        lcd.write(0, 0, "Weather Unavailable")
        return

    weather=weather_data["weather"][0]["main"]
    t=weather_data["main"]["temp"]
    rh=weather_data["main"]["humidity"]

    lcd.clear() 
    time.sleep(0.2)
    lcd.write(0,0,f'{weather}')
    lcd.write(0,1,f'{t}{"°C"} {rh}%rh')

try:
    while True:
        print(f'\033[1;30m{"listing... "}\033[0m')
        _stderr_back = redirect_error_2_null() # ignore error print to ignore ALSA errors
        with sr.Microphone(chunk_size=8192) as source:
            cancel_redirect_error(_stderr_back) # restore error print
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        print(f'\033[1;30m{"stop listening... "}\033[0m')

        msg = ""
        msg = speech_to_text(audio)
        if msg == False or msg == "":
            print() # new line
            continue

        weather_data=get_weather(OPENWEATHER_API_KEY, 'shenzhen')
        lcd_print(weather_data)
        
        message_content = {
            "weather": weather_data,
            "message": msg,
        }

        # Send the user's message and weather data to the assistant
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=str(message_content),
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
                            response = block.text.value
                            print(f'{assistant.name:>10} >>> {response}')
                            text_to_speech(response)
                    break # only last reply

finally:
    client.beta.assistants.delete(assistant.id)
    print("Resources cleaned up.")

{
    'coord': {'lon': 114.0683, 'lat': 22.5455}, 
    'weather': [
        {'id': 800, 
         'main': 'Clear', 
         'description': 'clear sky', 
         'icon': '01d'
         }
         ], 
    'base': 'stations', 
    'main': {
        'temp': 22.3, 
        'feels_like': 21.24, 
        'temp_min': 20.92, 
        'temp_max': 22.7, 
        'pressure': 1018, 
        'humidity': 25, 
        'sea_level': 1018, 
        'grnd_level': 1009
        }, 
    'visibility': 10000, 
    'wind': {
        'speed': 4.31, 'deg': 40, 'gust': 5.03
        }, 
    'clouds': {'all': 1}, 
    'dt': 1732865063, 
    'sys': {'type': 2, 
            'id': 2031340, 
            'country': 'CN', 
            'sunrise': 1732833958, 
            'sunset': 1732873111
            }, 
    'timezone': 28800, 
    'id': 1795565, 
    'name': 'Shenzhen', 
    'cod': 200}