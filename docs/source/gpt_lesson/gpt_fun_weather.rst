Weather Assistant
==================================

This project demonstrates the creation of an interactive weather assistant that uses voice commands to provide real-time clothing recommendations based on local weather conditions. 

The assistant is designed to be simple, intuitive, and useful for everyday tasks like deciding what to wear based on the current weather. This project is ideal for showcasing how voice-controlled AI and IoT technologies can work together to create a practical, user-friendly system.

----------------------------------------------

**Features**

* Voice Interaction: Captures user queries through a microphone and processes them using OpenAI's Whisper model for speech-to-text conversion.

* Weather Fetching: Retrieves real-time weather data from OpenWeatherMap API for a specified city.

* LCD Display: Displays concise weather information (e.g., temperature, humidity) on a 16x2 LCD screen.

* Clothing Suggestions: Uses OpenAI GPT-4 to analyze weather conditions and user queries to suggest appropriate clothing.

* Text-to-Speech: Converts GPT-generated text responses into speech for a conversational user experience.

----------------------------------------------

**What You’ll Need**

The following components are required for this project:


.. list-table::
    :widths: 30 20
    :header-rows: 1

    * - COMPONENT INTRODUCTION
      - PURCHASE LINK
    * - GPIO Extension Board
      - |link_gpio_board_buy|
    * - Breadboard
      - |link_breadboard_buy|
    * - Wires
      - |link_wires_buy|
    * - Resistor
      - |link_resistor_buy|
    * - LED
      - |link_led_buy|
    * - Button
      - |link_button_buy|
    * - Camera Module
      - |link_camera_buy|


----------------------------------------------

**Diagram**

【电路图】

----------------------------------------------

**Get OpenWeather API keys**

|link_openweather| is an online service, owned by OpenWeather Ltd, that provides global weather data via API, including current weather data, forecasts, nowcasts and historical weather data for any geographical location.

#. Visit |link_openweather| to log in/create an account.

    .. image:: img/OWM-1.png


#. Click into the API page from the navigation bar.

    .. image:: img/OWM-2.png


#. Find **Current Weather Data** and click Subscribe.

    .. image:: img/OWM-3.png


#. Under **Current weather and forecasts collection**, subscribe to the appropriate service. In our project, Free is good enough.

   .. image:: img/OWM-4.png


#. Copy the Key from the **API keys** page.

   .. image:: img/OWM-5.png

#. Open the ``keys.py`` file with the following command:

   .. code-block:: shell

      nano ~/pizero-gpt/gpt_examples/keys.py

#. Add the copied API Key:

   .. code-block:: shell
      :emphasize-lines: 2

      OPENAI_API_KEY = "sk-proj-vEBo7Ahxxxx-xxxxx-xxxx"
      OPENWEATHER_API_KEY = "732exxxxxxxxxxxxxxxxxxxxx919b"


#. Press ``Ctrl + X``, ``Y``, and then ``Enter`` to save the file and exit.

----------------------------------------------

**Code**

.. code-block:: python

   import openai
   from keys import OPENAI_API_KEY, OPENWEATHER_API_KEY
   from pathlib import Path
   import sys,os,subprocess
   import speech_recognition as sr
   import time
   import json
   import requests
   import LCD1602  # Import module for interfacing with LCD1602

   # Initialize LCD with I2C address 0x27 and enable backlight
   LCD1602.init(0x27, 1) 

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
         LCD1602.clear()
         LCD1602.write(0, 0, "Weather Unavailable")
         return

      weather=weather_data["weather"][0]["main"]
      t=weather_data["main"]["temp"]
      rh=weather_data["main"]["humidity"]

      LCD1602.clear() 
      time.sleep(0.2)
      LCD1602.write(0,0,f'{weather}')
      LCD1602.write(0,1,f'{t}{"°C"} {rh}%rh')

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

----------------------------------------------

**Code Explanation**

1. Libraries and Hardware Initialization

.. code-block:: python

   import openai
   from keys import OPENAI_API_KEY, OPENWEATHER_API_KEY
   from pathlib import Path
   import sys,os,subprocess
   import speech_recognition as sr
   import time
   import json
   import requests
   import LCD1602

* OpenAI API: Enables GPT-4 and Whisper integrations.
* OpenWeatherMap API: Fetches real-time weather data.
* LCD1602 Module: Interacts with the 16x2 LCD screen to display weather data.
* SpeechRecognition: Captures audio from the microphone and processes it for text conversion.

2. LCD and OpenAI Setup

.. code-block:: python

   LCD1602.init(0x27, 1) 
   client = openai.OpenAI(api_key=OPENAI_API_KEY)
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

* LCD Initialization: Sets up the LCD with the I2C address and enables the backlight.
* OpenAI Assistant: Creates a GPT-4 assistant tailored to provide weather-based recommendations.


3. Speech-to-Text Conversion

.. code-block:: python

   def speech_to_text(audio_file):
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

* Uses OpenAI Whisper for speech recognition, supporting multiple languages like Chinese and English.

4. Text-to-Speech Conversion

.. code-block:: python

   def text_to_speech(text):
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

* Converts GPT responses into speech using OpenAI's TTS API.
* The audio is played using the mplayer command-line utility.

5. Weather Data Retrieval

.. code-block:: python

   def get_weather(api_key, city):
      try:
         url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
         response = requests.get(url)
         response.raise_for_status() 
         return response.json()
      
      except requests.RequestException as e:
         print("Error: ", e)

* Retrieves weather data for a specified city from OpenWeatherMap API.

6. LCD Display Update

.. code-block:: python

   def lcd_print(weather_data):
      """
      Update the LCD display with weather information.
      """
      if not weather_data:
         LCD1602.clear()
         LCD1602.write(0, 0, "Weather Unavailable")
         return

      weather=weather_data["weather"][0]["main"]
      t=weather_data["main"]["temp"]
      rh=weather_data["main"]["humidity"]

      LCD1602.clear() 
      time.sleep(0.2)
      LCD1602.write(0,0,f'{weather}')
      LCD1602.write(0,1,f'{t}{"°C"} {rh}%rh')

* Updates the LCD display with the retrieved weather data.

7. Main Loop

.. code-block:: python

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

* Voice Input: Captures user queries via a microphone.
* Weather Fetching: Retrieves weather data for the specified city.
* Assistant Interaction: Sends the weather data and user query to GPT-4 and processes the response.
* Output: Displays weather data on the LCD and plays GPT-4's recommendations via TTS.

----------------------------------------------

**Debugging Tips**

#. No Voice Input Detected:
   
   * Ensure the microphone is correctly connected and configured.
   * Check for background noise that might interfere with recognition.

#. Weather Data Unavailable:
   
   * Verify the OpenWeatherMap API key and internet connection.
   * Ensure the specified city is valid.

#. No Response from Assistant:
   
   * Confirm OpenAI API key validity.
   * Check if the assistant is properly initialized.

#. LCD Not Displaying:
   
   * Ensure correct I2C connections and addresses.
   * Restart the LCD module if unresponsive.
