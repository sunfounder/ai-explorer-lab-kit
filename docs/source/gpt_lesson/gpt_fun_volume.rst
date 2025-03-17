Voice Level
=====================================

This project is a voice-controlled AI assistant that listens to user speech, transcribes it using OpenAI's Whisper model, generates a response using GPT-4, and plays the response back through text-to-speech (TTS). The system also integrates a potentiometer to control volume levels with visual LED feedback.

--------------------------------------

**Features**

- **Voice Recognition**: Uses OpenAI's Whisper model to transcribe speech.
- **AI-Powered Responses**: Utilizes GPT-4 to generate relevant responses based on user input.
- **Text-to-Speech (TTS)**: Converts AI-generated responses into spoken audio.
- **Volume Control via Potentiometer**: Adjusts system volume with real-time LED indicators.
- **Continuous Monitoring**: Runs in an infinite loop to process user commands dynamically.
- **LED Feedback System**: Indicates volume levels using a series of LEDs.

--------------------------------------

**What You’ll Need**

- Raspberry Pi Zero 2 W
- Fusion HAT
- Potentiometer for volume control
- LED Bar Graph for volume level indication

--------------------------------------

**Wiring Diagram**

(Include a wiring diagram illustrating the connections between the microphone, speaker, potentiometer, and LED array.)

--------------------------------------

**Code**



--------------------------------------

**Code Explanation**

1. **Initialization**

The script starts by importing necessary modules and enabling the speaker:

.. code-block:: python

    import openai
    from keys import OPENAI_API_KEY
    from fusion_hat import ADC, Pin
    from time import sleep
    import speech_recognition as sr
    import subprocess
    import os
    from pathlib import Path

    os.system("fusion_hat enable_speaker")

The OpenAI client is initialized:

.. code-block:: python

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

An AI assistant and a conversation thread are created:

.. code-block:: python

    assistant = client.beta.assistants.create(
        name="BOT",
        instructions="You are a chatbot, you answer people’s questions to help them.",
        model="gpt-4-1106-preview",
    )

    thread = client.beta.threads.create()


2. **Speech Recognition Setup**

The ``speech_to_text`` function converts spoken input into text using OpenAI’s Whisper model:

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

- Converts recorded audio to WAV format.
- Sends the audio file to OpenAI’s Whisper model for transcription.
- Returns the transcribed text.


3. **Text-to-Speech Processing**

The ``text_to_speech`` function generates an audio response:

.. code-block:: python

    def text_to_speech(text):
        speech_file_path = Path(__file__).parent / "speech.mp3"
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text
        ) as response:
            response.stream_to_file(speech_file_path)
        p = subprocess.Popen("mplayer speech.mp3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()

- Converts the response text into an MP3 file.
- Uses ``mplayer`` to play the generated speech.


4. **Potentiometer and LED Volume Control**

The potentiometer reads the ADC value and maps it to a percentage for volume control:

.. code-block:: python

    def MAP(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def set_volume(percent):
        for led in leds:
            led.low()
        for i in range(int(percent/10)):
            leds[i].high()
        os.system(f"amixer set Master {percent}%")

- ``MAP``: Converts the ADC reading (0-4095) to a percentage (0-100%).
- ``set_volume``: Updates LED indicators and adjusts system volume accordingly.



5. **Main Loop: Listening & Processing**

The script continuously listens for user input and processes it:

.. code-block:: python

    while True:
        if not is_mplayer_running():
            print("Listening...")
            with sr.Microphone(chunk_size=8192) as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
            print("Processing...")

            msg = speech_to_text(audio)
            if msg:
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
                        if message.role == 'assistant':
                            for block in message.content:
                                if block.type == 'text':
                                    text_to_speech(block.text.value)
                            break
        
        volume = MAP(pot.read(), 0, 4095, 0, 100)
        set_volume(volume)
        sleep(0.2)


6. **Cleanup and Resource Management**

If the script is interrupted, resources are cleaned up:

.. code-block:: python

    finally:
        client.beta.assistants.delete(assistant.id)
        for led in leds:
            led.low()

- Deletes the assistant to free API resources.
- Turns off all LEDs before exiting.

--------------------------------------

**Debugging Tips**

1. **No Audio Response?**

   - Ensure ``mplayer`` is installed.
   - Check if ``fusion_hat enable_speaker`` is executed properly.

2. **Speech Recognition Not Working?**

   - Adjust noise threshold settings in ``speech_recognition``.

3. **Volume Control Not Responding?**

   - Check the potentiometer connections.
   - Use ``print(pot.read())`` to verify ADC readings.
