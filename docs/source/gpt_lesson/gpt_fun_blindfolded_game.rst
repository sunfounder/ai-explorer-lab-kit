blindfolded Watermelon-smashing Game
====================================

This project is an interactive blindfolded watermelon-smashing game powered by OpenAI's GPT-4 and a joystick-based control system. The game involves randomly placing a virtual watermelon within a 20x20 meter area. The player, who starts at the origin (0,0), navigates the area using a joystick and attempts to smash the watermelon by pressing a joystick. After each attempt, the AI provides directional guidance to help the player locate the target. The assistant's responses are converted into speech for an immersive experience.

----------------------------------------

**Features**

- **OpenAI GPT-4 Integration**: The assistant processes player actions and provides real-time verbal guidance.
- **Joystick-Based Navigation**: Movement is controlled using an analog joystick mapped to a coordinate system.
- **Button-Based Smashing Action**: A physical button triggers the smash attempt.
- **Text-to-Speech (TTS)**: The AI’s responses are converted into audio output using OpenAI’s TTS model.
- **Randomized Watermelon Placement**: Ensures variability in gameplay by generating a new target location each time.
- **Real-Time Position Updates**: The player receives feedback on both their position and the target's location.

----------------------------------------

**What You’ll Need**

- Raspberry Pi Zero 2 W
- Fusion Hat (for joystick and button input)
- Joystick

----------------------------------------

**Wiring Diagram**

*(Omitted – Assumes prior knowledge of connecting joystick and buttons to GPIO ports.)*

----------------------------------------

**Code**

*(Omitted – Full code provided separately.)*

----------------------------------------

**Code Explanation**

The game is structured into several key components:

1. **Initializing OpenAI GPT-4 Assistant**

.. code-block:: python

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    assistant = client.beta.assistants.create(
        name="BOT",
        instructions="This is a blindfolded watermelon-smashing game...",
        model="gpt-4-1106-preview",
    )

- This initializes an OpenAI assistant with specific instructions on how to respond to player actions.
- The assistant helps guide the player by providing directional hints after each smash attempt.

2. **Mapping Joystick Input to Movement**

.. code-block:: python

    def MAP(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    x_axis = ADC('A1')
    y_axis = ADC('A0')
    
    x_val = MAP(x_axis.read(), 0, 4095, -100, 100)
    y_val = MAP(y_axis.read(), 0, 4095, -100, 100)

- The joystick input values are read as ADC values (0-4095) and mapped to a coordinate range (-100 to 100).
- Movement is updated based on threshold values:

.. code-block:: python

    if x_val > 80:
        player_x += 1
    elif x_val < -80:
        player_x -= 1
    if y_val > 80:
        player_y += 1
    elif y_val < -80:
        player_y -= 1

3. **Smash Attempt and AI Response Processing**

- When the player presses the joystick button, an attempt to smash is made, triggering a message to OpenAI:

.. code-block:: python

    send_message = f"Watermelon position: ({watermelon_x}, {watermelon_y}), Player position: ({player_x}, {player_y})"
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=send_message,
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

- The AI processes the message and determines how far the player is from the target.
- If the smash coordinates match the watermelon’s position, the game ends with a victory message.

4. **Text-to-Speech Output**

.. code-block:: python

    def text_to_speech(text):
        speech_file_path = Path(__file__).parent / "speech.mp3"
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text
        ) as response:
            response.stream_to_file(speech_file_path)
        subprocess.Popen("mplayer speech.mp3", shell=True).wait()

- Converts AI-generated responses into speech and plays them using ``mplayer``.

5. **Game Loop and Termination**

.. code-block:: python

    try:
        text_to_speech("game start!")
        while True:
            # Read joystick values, update position
            # Process smashing logic
            if (player_x, player_y) == (watermelon_x, watermelon_y):
                print("Target hit!")
                break
    finally:
        client.beta.assistants.delete(assistant.id)
        print("\n Delete Assistant ID")

- Runs a continuous loop where the player navigates and attempts to smash the target.
- Deletes the assistant instance after exiting to free resources.

----------------------------------------

**Debugging Tips**

1. **Joystick Not Responding?**
   - Check the wiring and ensure ADC values are being read correctly.
   - Print ``x_axis.read()`` and ``y_axis.read()`` to verify the input range.

2. **No Audio Output?**
   - Ensure ``mplayer`` is installed and working (``mplayer test.mp3``).
   - Check the generated ``speech.mp3`` file for errors.

3. **Assistant Not Responding?**
   - Verify the OpenAI API key and internet connection.
   - Print AI response status to check for errors.

4. **Game Ends Prematurely?**
   - Debug movement logic to ensure the player's position updates correctly.
   - Print ``(player_x, player_y)`` at each iteration to track movements.

