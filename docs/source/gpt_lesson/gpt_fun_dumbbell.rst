Smart Fitness Assistant
======================================

This project is a smart fitness assistant that helps users track their dumbbell workouts in real-time. Using an MPU6050 accelerometer sensor, the system detects lifting motions, calculates speed, and interacts with OpenAI's API to provide personalized feedback and motivation. The feedback is delivered through text-to-speech (TTS), ensuring a seamless workout experience.


----------------------------------------------

**Features**

- **Motion Detection**: Uses an MPU6050 accelerometer to track dumbbell lifts.
- **Repetition Counting**: Keeps track of the number of lifts performed.
- **Speed Calculation**: Monitors lifting speed to assess consistency and effort.
- **Real-Time Feedback**: Uses OpenAI's API to analyze workout data and generate feedback.
- **Text-to-Speech Output**: Provides spoken feedback to encourage and guide the user.
- **7-Segment Display**: Shows the lift count in real-time.
- **Auto Stop Feature**: Ends the session after 30 seconds of inactivity.


----------------------------------------------


**What You’ll Need**

- Raspberry Pi Zero 2 W
- Fusion Hat with an MPU6050 sensor
- 74HC595 Shift Register for 7-segment display control
- 4 digit 7-segment display


----------------------------------------------

**Wiring Diagram**

*(Omitted for brevity)*

**Code**

*(Omitted for brevity)*

**Code Explanation**

This project is structured around multiple functionalities:

1. **Initialization and Setup:**

   - The program starts by importing necessary modules and initializing OpenAI's API.
   - It sets up GPIO pins for the 74HC595 shift register and the 7-segment display.
   - The ``MPU6050`` sensor is initialized to read motion data.

2. **Text-to-Speech Function**:

   - This function converts text responses from the AI into speech using OpenAI’s TTS model.
   - The generated audio is played using ``mplayer``.

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

3. **7-Segment Display Control:**

   - Functions ``hc595_shift``, ``clearDisplay``, and ``display`` control the shift register to update the display.
   - ``display(count)`` is used to show the number of lifts in real-time.

   .. code-block:: python

       def display(count):
           for i in range(4):
               clearDisplay()
               pickDigit(i)
               digit = (count // (10 ** i)) % 10
               hc595_shift(number[digit])
               sleep(0.001)

4. **Workout Tracking Logic:**

   - Reads acceleration data from ``MPU6050``.
   - Calculates the speed of motion.
   - Detects when a dumbbell is lifted and counts repetitions.
   - Stores motion data for analysis.
   - Ends the session if no movement is detected for 30 seconds.

   .. code-block:: python

       while count <= 100:
           time_now = time()
           dt = time_now - time_last
           time_last = time_now
           acc_x, acc_y, acc_z = mpu.get_accel_data()
           v = abs(acc_z * dt)

           if acc_z > threshold_up and last_state == "down":
               count += 1
               last_state = "up"
               motion_data.append((time_now, v))
               last_lift_time = time_now
               print(f"Dumbbell lifts: {count}, Speed: {v:.2f} m/s")
           elif acc_z < threshold_down and last_state == "up":
               last_state = "down"

           if time_now - last_lift_time > 30:
               print("No movement detected for 30 seconds. Ending session.")
               break

           display(count)
           sleep(0.2)

5. **AI Feedback Generation:**

   - Sends motion data and repetition count to OpenAI.
   - The AI analyzes the data and generates motivational feedback.
   - The feedback is spoken using TTS.

   .. code-block:: python

       msg = f"Dumbbell lifts: {count}, Motion data: {motion_data}"
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
                           print(f'BOT >>> {block.text.value}')
                           text_to_speech(block.text.value)
                   break

6. **Cleanup and Exit:**

   - The program ensures resources are cleaned up properly on exit.
   - GPIO pins are reset.
   - The AI assistant instance is deleted.

   .. code-block:: python

       finally:
           client.beta.assistants.delete(assistant.id)

**Debugging Tips**

- **No movement detected?**
  - Check that the MPU6050 sensor is correctly connected and configured.
  - Print raw acceleration data to confirm it's being read correctly.

- **Incorrect repetition count?**
  - Adjust the ``threshold_up`` and ``threshold_down`` values to better detect lifts.
  - Ensure noise in acceleration readings is minimized.

- **No AI response?**
  - Verify your OpenAI API key is correctly set up.
  - Ensure network connectivity for API calls.
  - Add print statements to debug response statuses from OpenAI.

- **No speech output?**
  - Check if ``mplayer`` is installed and working.
  - Ensure TTS output files are being generated correctly.

