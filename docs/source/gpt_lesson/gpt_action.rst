.. _gpt_easy_action:


Take Action
==========================

In recent years, the convergence of artificial intelligence (AI) and the Internet of Things (IoT) has sparked a revolution in smart home technology. By integrating AI capabilities with physical devices, it's possible to create highly interactive and responsive environments. This tutorial explores how OpenAI can be utilized to control a physical device—specifically an RGB LED—through natural language commands. Such integration paves the way for intelligent systems that enhance everyday living by responding to vocal instructions for tasks like adjusting lighting based on mood or time of day.

The ability to control devices through AI not only adds convenience but also enables more personalized user experiences. This project serves as an excellent foundation for further exploration into the realm of smart homes, where devices can adapt to individual preferences and environmental conditions seamlessly.


This tutorial demonstrates how you can leverage OpenAI to turn a Raspberry Pi into a command center for controlling an RGB LED light. The process involves understanding user commands processed by OpenAI and translating them into actionable instructions that adjust the colors and behavior of an LED. This example can be expanded into more complex scenarios within a smart home, such as voice-activated temperature adjustments, security systems, or even multi-device orchestration.

By the end of this tutorial, you will be equipped with the knowledge to build an AI-powered interface that can interpret natural language and interact with physical hardware. This is a stepping stone towards creating more sophisticated systems like those found in advanced smart home setups.

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

**Running the Example**

We provide all example code used in this course, located in the ``pizero-gpt`` directory. 
Use the following steps to run this example:


.. code-block:: shell

   cd ~/pizero-gpt/gpt_examples/
   ~/my_venv/bin/python3 gpt_easy_action.py

----------------------------------------------

**Code**

Here is the complete example code:


.. code-block:: python

   import openai
   from keys import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
   from pathlib import Path

   import readline # optimize keyboard input, only need to import
   import sys
   import os
   import subprocess

   from gpiozero import RGBLED

   # gets API Key from environment variable OPENAI_API_KEY
   client = openai.OpenAI(api_key=OPENAI_API_KEY)

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

   # Initialize an RGB LED. Connect the red component to GPIO 17, green to GPIO 18, and blue to GPIO 27.
   rgb_led = RGBLED(red=23, green=24, blue=25)

   def text_to_speech(text):
      speech_file_path = Path(__file__).parent / "speech.mp3"
      with client.audio.speech.with_streaming_response.create(
         model="tts-1",
         voice="alloy",
         input=text
      ) as response:
         response.stream_to_file(speech_file_path)

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
                        p=subprocess.Popen("mplayer speech.mp3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        p.wait()
                  break # only last reply

   finally:
      client.beta.assistants.delete(assistant.id)

----------------------------------------------

**Code Explanation**


This section highlights the new features, 
including controlling a physical RGB light and parsing JSON data returned by the assistant. 
For details on controlling RGB lights, refer to :ref:`1.1.2_py`. 
Below, we’ll focus on JSON parsing and its key aspects.


.. code-block:: python
   :emphasize-lines: 40-55

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

   try:
      while True:
         ...
         if run.status == "completed":
            ...
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
                        ...
                  break # only last reply


The highlighted portion of the code is essential for extracting meaningful information from the assistant's responses. 
It parses JSON strings to extract the ``color`` (RGB values) and ``message`` (text message) to control the 
light and generate speech output.

.. code-block:: python

   try:
      value = eval(value)  # Attempt to parse the string into a Python data structure
   except Exception as e:
      value = str(value)  # If parsing fails, keep the original string

``eval(value)`` attempts to parse the AI's JSON string into a Python dictionary.

* **Example Input:** ``'{"color": [0.5, 0.3, 0.2], "message": "Setting a warm light."}'``
* **Example Output:** ``{'color': [0.5, 0.3, 0.2], 'message': 'Setting a warm light.'}``


If parsing fails (e.g., the string is not valid JSON), the raw string is retained, 
which prevents crashes and aids debugging.


.. code-block:: python

   if isinstance(value, dict):

This ensures that the parsed result is a dictionary, confirming that the assistant returned properly formatted JSON. 
If the response is not a dictionary, a fallback logic is applied.



.. code-block:: python

   if 'color' in value:
      color = list(value['color'])
   else:
      color = [0,0,0]

Extracts the ``color`` field from the dictionary. 
If the field exists, its values are converted to a list to directly control the RGB light. 
If the field is missing, the default value ``[0, 0, 0]`` is applied (light off).


.. code-block:: python

   if 'message' in value:
      text = value['message']
   else :
      text = ''

Extracts the ``message`` field from the dictionary. If the field is missing, 
it defaults to an empty string, indicating no message is available for text-to-speech output.


.. code-block:: python

   else:
      color = [0,0,0]
      text = value

If ``value`` is not a dictionary (e.g., an error message or unstructured text), 
it defaults to turning the light off (``[0, 0, 0]``) and uses the raw output as the message for debugging or user prompts.

Overall, JSON parsing is the core logic in this example, 
ensuring the assistant's output is correctly interpreted to control the RGB light and generate voice feedback.


----------------------------------------------

**Debugging Tips**

This section offers practical advice for troubleshooting common issues you may encounter while working on this project. By following these tips, you can ensure your setup functions as intended and diagnose any problems efficiently.

1. **If the RGB light does not work:**


   - **Check the Wiring:** Ensure all wires are securely connected and the GPIO pins are correctly configured. Loose connections are a frequent cause of issues.
   - **Verify the Pin Configuration:** Confirm that the ``RGBLED(red=23, green=24, blue=25)`` in the code matches the actual GPIO pins used in your hardware setup.
   - **Test the LED:** Replace the LED with another to rule out the possibility of a defective LED.

2. **If the AI's output is not in JSON format:**

   - **Check the Instructions:** Make sure that the ``instructions_text`` in your assistant setup clearly specifies that the output should be in JSON format.
   - **Inspect the Raw Output:** Use ``print(f"Raw AI Response: {value}")`` immediately after the response is received to check if the output is in the expected format.
   - **Validate the JSON:** If you are manually parsing JSON, ensure the string is valid JSON. Tools like JSONLint can help validate and format JSON strings.

3. **If text-to-speech does not work:**

   - **Check MP3 File Generation:** Ensure that the ``text_to_speech`` function is generating MP3 files correctly. Verify the file path and permissions.
   - **Test the Audio Output:** Ensure your Raspberry Pi's audio output is configured correctly and that the volume is turned up.
   - **Verify MPlayer Installation:** Confirm that ``mplayer`` is properly installed on your Raspberry Pi. You can reinstall it using ``sudo apt install mplayer`` if necessary.

4. **General Software Debugging:**

   - **Monitor Logs:** Keep an eye on the logs for any errors that might indicate what went wrong. Use commands like ``tail -f /var/log/syslog`` to view system logs in real time.
   - **Update Software:** Make sure your Raspberry Pi and all related software are up to date. Run ``sudo apt update`` and ``sudo apt upgrade`` to update your system.
   - **Check API Usage:** Ensure that your API calls to OpenAI are within usage limits and the API key is correct.
