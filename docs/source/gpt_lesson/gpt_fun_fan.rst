Voice-Controlled Fan
================================================

This project is a voice-controlled fan speed regulator powered by OpenAI's API. Users can give voice commands to adjust the speed of a motor, which acts as the fan. The system utilizes a microphone for voice input, a motor driver to control fan speed, and a buzzer for auditory feedback. It ensures a seamless interaction by recognizing speech, processing commands through AI, and dynamically adjusting the fan's speed.

----------------------------------------------


**Features**

- **Voice-Controlled Fan Speed**: Users can increase, decrease, or stop the fan with voice commands.
- **Real-Time Speed Adjustment**: The system ensures the speed stays within the valid range (0-100%).
- **Touch Sensor for Speed Increase**: A physical touch sensor allows manual speed adjustments.
- **Buzzer Feedback**: Provides an audible beep for user interactions.
- **AI-Based Command Processing**: OpenAI's GPT-4 interprets user requests and generates JSON-formatted responses.
- **Speech-to-Text Conversion**: Uses OpenAI’s Whisper model for speech recognition.
- **Dynamic Noise Adjustment**: The system adapts to background noise for accurate speech recognition.

----------------------------------------------

**What You’ll Need**

- Raspberry Pi Zero 2 W
- Fusion Hat (for controlling motor, buzzer, and sensor input)
- A DC motor with PWM control
- Touch sensor

----------------------------------------------


**Wiring Diagram**

*(Omitted for brevity)*

----------------------------------------------

**Code**

*(Omitted for brevity)*

----------------------------------------------


**Code Explanation**

This project consists of several key functional components:

1. **Initialization and Setup:**

   - Imports necessary libraries, including OpenAI for AI processing and ``speech_recognition`` for speech input.
   - Sets up the OpenAI client using ``OPENAI_API_KEY``.
   - Initializes hardware components, including the motor, buzzer, and touch sensor.

2. **Speech Recognition**:

   - Converts recorded audio into text using OpenAI’s Whisper model.
   - Supports multiple languages (``zh``, ``en``).

   .. code-block:: python

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

3. **Touch Sensor Handling (``speed_up``)**:

   - A touch sensor allows manual speed adjustments.
   - Debounce logic prevents accidental multiple triggers.
   - Increments speed by 10% per touch, resetting to 0% if exceeding 100%.

   .. code-block:: python

       def speed_up():
           global speed, last_triggered
           if time.time() - last_triggered < 0.5:
               return
           last_triggered = time.time()
           speed += 10
           beep()
           if speed > 100:
               motor.stop()
               speed = 0
           else:
               motor.speed(speed)

4. **Voice Command Processing:**

   - Captures user speech and converts it into text.
   - Sends the transcribed text to OpenAI’s assistant along with the current fan speed.
   - The AI returns a JSON response containing the new speed and a textual response.

   .. code-block:: python

       send_message= "current speed:"+ str(speed) + "message:" + msg
       message = client.beta.threads.messages.create(
           thread_id=thread.id,
           role="user",
           content=send_message,
       )
       run = client.beta.threads.runs.create_and_poll(
           thread_id=thread.id,
           assistant_id=assistant.id,
       )

5. **AI Response Processing:**

   - Extracts speed and message from the AI’s JSON response.
   - Updates the motor speed accordingly.

   .. code-block:: python

       for message in messages.data:
           if message.role == 'assistant':
               for block in message.content:
                   if block.type == 'text':
                       value = eval(block.text.value)
                       if isinstance(value, dict):
                           speed = value.get('speed', -1)
                           text = value.get('message', '')
                       print(f'BOT >>> {text} {speed}')
                       if speed >= 0:
                           motor.speed(speed)

6. **Error Handling and Cleanup:**

   - Suppresses ALSA warnings to prevent unnecessary errors.
   - Ensures OpenAI assistant is deleted and hardware is reset upon exit.

   .. code-block:: python

       finally:
           client.beta.assistants.delete(assistant.id)
           buzzer.off()
           motor.stop()

----------------------------------------------

**Debugging Tips**

- **Speech recognition not working?**

  - Increase ``recognizer.adjust_for_ambient_noise(source)`` duration if background noise is interfering.

- **Fan speed not updating?**

  - Check the OpenAI API response format to ensure JSON is correctly parsed.
  - Verify that ``motor.speed(speed)`` is being executed with the expected value.

- **Touch sensor not responding?**

  - Add print statements to ``speed_up()`` to confirm it is being triggered.
  - Ensure proper pull-down configuration for the GPIO pin.

- **Buzzer not making sound?**

  - Check that ``buzzer.on()`` and ``buzzer.off()`` are properly called.
  - Ensure GPIO output is enabled for the buzzer pin.

