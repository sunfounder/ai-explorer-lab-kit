Virtual Plant 
===================================

This example demonstrates how to integrate OpenAI's GPT model with IoT hardware components to create a virtual plant assistant. The assistant uses environmental data from sensors to simulate a plant's "feelings" and responds to user inquiries in a natural, plant-like manner.

----------------------------------------------

**Features**

1. **Speech Interaction:** Users can interact with the virtual plant using speech. The assistant uses OpenAI's Whisper model to convert speech to text.

2. **Sensor Data Integration:** The virtual plant gathers real-time environmental data from sensors, including:

   * **DHT11:** Measures temperature and humidity.
   * **ADC0834:** Measures soil moisture and light intensity.

3. **Text-to-Speech Feedback:** The plant responds to user questions using OpenAI's TTS model, providing a spoken response.

4. **Concise Responses:** The assistant replies in a way that mimics a plant's feelings based on environmental data.

5. **Real-Time Processing:** Sensor data is collected in the background, ensuring up-to-date information for interactions.


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

**Code**

.. code-block:: python

   import openai
   from keys import OPENAI_API_KEY
   import readline  # Optimize keyboard input
   import sys
   import os
   import subprocess
   from pathlib import Path
   import speech_recognition as sr
   from DHT import DHT11
   import ADC0834
   import time
   import threading

   # Initialize OpenAI client
   client = openai.OpenAI(api_key=OPENAI_API_KEY)

   # Initialize speech recognizer
   recognizer = sr.Recognizer()

   # Initialize hardware components
   ADC0834.setup(cs=17, clk=22, dio=27)
   dht11 = DHT11(12)

   humidity = None
   temperature = None
   light = None
   moisture = None

   # Function to fetch sensor data
   def fetch_sensor_data():
      global humidity, temperature, light, moisture
      while True:
         _humidity, _temperature = dht11.read_data()
         if _humidity != 0.0:
               humidity = _humidity
         if _temperature != 0.0:
               temperature = _temperature
         light = ADC0834.getResult(channel=0)
         moisture = ADC0834.getResult(channel=1)
         time.sleep(1)

   # Start a background thread for sensor data
   sensor_thread = threading.Thread(target=fetch_sensor_data)
   sensor_thread.daemon = True
   sensor_thread.start()

   # Function for text-to-speech conversion
   def text_to_speech(text):
      speech_file_path = Path(__file__).parent / "speech.mp3"
      try:
         with client.audio.speech.with_streaming_response.create(
               model="tts-1", voice="alloy", input=text
         ) as response:
               response.stream_to_file(speech_file_path)
      except Exception as e:
         print(f"Error in TTS: {e}")
         return None
      return speech_file_path

   # Function for speech-to-text conversion
   def speech_to_text(audio_file):
      from io import BytesIO

      wav_data = BytesIO(audio_file.get_wav_data())
      wav_data.name = "record.wav"
      transcription = client.audio.transcriptions.create(
         model="whisper-1", file=wav_data, language=["zh", "en"]
      )
      return transcription.text

   # Function to redirect errors to null
   def redirect_error_to_null():
      devnull = os.open(os.devnull, os.O_WRONLY)
      old_stderr = os.dup(2)
      sys.stderr.flush()
      os.dup2(devnull, 2)
      os.close(devnull)
      return old_stderr

   # Function to cancel redirected errors
   def cancel_redirect_error(old_stderr):
      os.dup2(old_stderr, 2)
      os.close(old_stderr)

   # Create OpenAI assistant
   assistant = client.beta.assistants.create(
      name="Plant Bot",
      instructions=(
         "You are a virtual plant. Based on the received greeting and environmental conditions "
         "(light, soil moisture, temperature, humidity), respond with how you feel. "
         "Provide a concise, plant-like response. Units: "
         "Temperature in Celsius, humidity in %, soil moisture (3200: dry, 2500: wet), "
         "light (4095: dark, 2300: bright sunlight). User input will be JSON format like: "
         '{"light": 512, "moisture": 3000, "temperature": 25, "humidity": 62, "message": "How do you feel?"}'
      ),
      tools=[{"type": "code_interpreter"}],
      model="gpt-4-1106-preview",
   )

   # Create a conversation thread
   thread = client.beta.threads.create()

   try:
      while True:
         # Listen for user input
         print(f'\033[1;30m{"Listening..."}\033[0m')
         old_stderr = redirect_error_to_null()
         with sr.Microphone(chunk_size=8192) as source:
               cancel_redirect_error(old_stderr)
               recognizer.adjust_for_ambient_noise(source)
               audio = recognizer.listen(source)
         print(f'\033[1;30m{"Processing audio..."}\033[0m')

         # Convert speech to text
         user_message = speech_to_text(audio)
         if not user_message:
               print("No valid input detected.")
               continue

         # Prepare input for assistant
         assistant_input = {
               "light": light,
               "moisture": moisture,
               "temperature": temperature,
               "humidity": humidity,
               "message": user_message,
         }

         # Send message to assistant
         message = client.beta.threads.messages.create(
               thread_id=thread.id, role="user", content=str(assistant_input)
         )

         # Get assistant response
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
                              print(f"Plant Bot >>> {response}")
                              speech_path = text_to_speech(response)
                              if speech_path:
                                 subprocess.Popen(
                                       ["mplayer", str(speech_path)],
                                       shell=False,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                 ).wait()
   finally:
      client.beta.assistants.delete(assistant.id)
      print("Cleaned up resources.")


----------------------------------------------

**Code Explanation**

1. Initialization

.. code-block:: python

   client = openai.OpenAI(api_key=OPENAI_API_KEY)

Initializes the OpenAI client using your API key.

.. code-block:: python

   ADC0834.setup(cs=17, clk=22, dio=27)
   dht11 = DHT11(12)

Configures the ADC0834 module for reading light and soil moisture data and initializes the DHT11 sensor for temperature and humidity readings.


2. Sensor Data Collection

.. code-block:: python

   # Function to fetch sensor data
   def fetch_sensor_data():
      global humidity, temperature, light, moisture
      while True:
         _humidity, _temperature = dht11.read_data()
         if _humidity != 0.0:
               humidity = _humidity
         if _temperature != 0.0:
               temperature = _temperature
         light = ADC0834.getResult(channel=0)
         moisture = ADC0834.getResult(channel=1)
         time.sleep(1)

This function continuously updates global variables with sensor data, running on a separate thread to avoid blocking the main program.

3. Speech-to-Text and Text-to-Speech

.. code-block:: python

   def speech_to_text(audio_file):
      transcription = client.audio.transcriptions.create(
         model="whisper-1", file=wav_data, language=["zh", "en"]
      )
      return transcription.text

Uses OpenAI's Whisper model to transcribe the user's spoken input into text.

.. code-block:: python

   def text_to_speech(text):
      with client.audio.speech.with_streaming_response.create(
         model="tts-1", voice="alloy", input=text
      ) as response:
         response.stream_to_file(speech_file_path)

Converts the assistant's textual response into a spoken audio file using OpenAI's TTS model.

4. Creating the Assistant

.. code-block:: python

   instructions = (
      "You are a virtual plant. Based on the received greeting and environmental conditions "
      "(light, soil moisture, temperature, humidity), respond with how you feel. "
      "Provide a concise, plant-like response. Units: "
      "Temperature in Celsius, humidity in %, soil moisture (3200: dry, 2500: wet), "
      "light (4095: dark, 2300: bright sunlight)."
   )

The assistant is designed to mimic the personality of a plant, considering environmental data when responding.

5. Processing User Interactions


.. code-block:: python

   assistant_input = {
      "light": light,
      "moisture": moisture,
      "temperature": temperature,
      "humidity": humidity,
      "message": user_message,
   }
   message = client.beta.threads.messages.create(
      thread_id=thread.id, role="user", content=str(assistant_input)
   )

Sends the sensor data and user query to the assistant as a JSON-formatted string.

6. Generating a Response

.. code-block:: python

   run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id, assistant_id=assistant.id
   )

Waits for the assistant to generate a response.

.. code-block:: python

   speech_path = text_to_speech(response)
   subprocess.Popen(
      ["mplayer", str(speech_path)],
      shell=False,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
   ).wait()

Plays the assistant's response through the speaker.


----------------------------------------------

**Debugging Tips**


1. **No Sensor Data:**
   
   * Ensure sensors are properly connected to the GPIO pins.
   * Use a multimeter to verify power supply to the sensors.

2. **Audio Issues:**
   
   * Verify microphone and speaker connections.
   * Check if audio input/output devices are recognized by the system.
