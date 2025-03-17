Access Control System with RFID
===============================

This project is an RFID-based access control system using the Fusion Hat module. The system allows users to register RFID cards and use them to unlock a door. It consists of two main scripts: ``gpt_fun_access_registration.py`` for registering cards and ``gpt_fun_access_read.py`` for granting access.

----------------------------------------------

**Features**

- **RFID Card Registration**: Users can register RFID cards and associate them with their names.
- **RFID-Based Authentication**: Reads an RFID card and checks if it is registered in the system.
- **Text-to-Speech (TTS) Notification**: Uses OpenAI's TTS model to provide auditory feedback on access status.
- **Relay Control**: A relay module is used to unlock the door upon successful authentication.
- **Persistent User Data Storage**: Stores registered users in a JSON file for future reference.

----------------------------------------------

**What You’ll Need**

- Fusion Hat
- RFID Cards
- Raspberry Pi Zero 2 W
- RFID module
- Relay module for door control

----------------------------------------------

**Wiring Diagram**

(Include a wiring diagram if necessary.)




----------------------------------------------

Card Registration Script
----------------------------------------


The ``gpt_fun_access_registration.py`` script is responsible for registering new RFID cards by associating them with a user’s name.



**Code**


.. code-block:: python

    from fusion_hat import RC522
    import json

    rc = RC522()
    rc.Pcd_start()

    users_db = "users.json"  # the file to store user data

    # load the existing user data from the file
    try:
        with open(users_db, "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}

    def register_card():
        print("Please place the card to register...")
        uid, message = rc.read(2)
        if uid:
            user_name = input("Enter the name of the cardholder: ")
            users[uid] = user_name
            with open(users_db, "w") as file:
                json.dump(users, file)
            print(f"Card registered successfully for {user_name}.")
        else:
            print("Failed to read the card.")

    if __name__ == "__main__":
        while True:
            register_card()
            if input("Register another card? (y/n): ").lower() != 'y':
                break


**How it Works:**

1. Initializes the RFID reader using ``RC522()``.

2. Loads existing users from ``users.json``.

3. Waits for an RFID card to be placed.

4. Reads the card UID and prompts the user to enter a name.

5. Saves the user’s data in the JSON file.

6. Repeats the process if the user chooses to register another card.


----------------------------------------------

Access Control Script
--------------------------------------


The ``gpt_fun_access_read.py`` script checks if an RFID card is registered and grants or denies access accordingly. It also provides auditory feedback via OpenAI's text-to-speech.

**Code**

.. code-block:: python

    from fusion_hat import RC522, Pin
    import json
    import openai
    from keys import OPENAI_API_KEY
    from pathlib import Path
    import subprocess
    import os
    import time

    # Initialize OpenAI client
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    os.system("fusion_hat enable_speaker")

    def text_to_speech(text):
        speech_file_path = Path(__file__).parent / "speech.mp3"
        try:
            with client.audio.speech.with_streaming_response.create(
                model="tts-1", voice="alloy", input=text
            ) as response:
                response.stream_to_file(speech_file_path)
            subprocess.Popen(["mplayer", str(speech_file_path)], shell=False).wait()
        except Exception as e:
            print(f"Error in TTS or playing the file: {e}")

    relay = Pin(17, Pin.OUT)
    rc = RC522()
    rc.Pcd_start()

    users_db = "users.json"

    with open(users_db, "r") as file:
        users = json.load(file)

    def access_door():
        print("Please place your card to access the door...")
        uid, message = rc.read(2)
        if uid and uid in users:
            relay.high()
            text_to_speech(f"The door is open. Access granted to {users[uid]}!")
            time.sleep(2)
            relay.off()
            return True
        else:
            print("Access denied!")
            text_to_speech("Access denied!")
        return False

    while True:
        result = access_door()
        if result:
            break




**How it Works:**

1. Initializes the RFID reader and loads user data.

2. Waits for a card to be placed on the reader.

3. Checks if the card UID exists in the JSON database.

4. If the card is recognized:

   - The relay is activated to unlock the door.
   - A text-to-speech message announces the access grant.
   - The relay deactivates after 2 seconds.
5. If the card is unrecognized:

   - Access is denied.
   - A TTS message announces the denial.

6. The process repeats until a recognized card is used.

----------------------------------------------

**Debugging Tips**

1. **Check RFID Reader Connection**

   - Ensure that the RFID module is properly connected to the Raspberry Pi.
   - Run ``dmesg | grep spi`` to check if SPI is enabled.

2. **Verify JSON User Data**

   - If access is denied for a known card, verify the ``users.json`` file and ensure the UID is correctly stored.
   - Delete and recreate the file if corrupted.

3. **Debugging Text-to-Speech Issues**

   - Ensure the OpenAI API key is correct and has sufficient quota.
   - Check if the ``mplayer`` package is installed using ``which mplayer``.

4. **Check Relay Activation**

   - Use a multimeter to check if the relay receives power.
   - Manually toggle the relay using ``relay.high()`` and ``relay.off()`` in a Python shell.

5. **Error Handling for File Operations**

   - If ``users.json`` is missing or unreadable, ensure proper file permissions using ``chmod 644 users.json``.
   - Add exception handling for unexpected file read/write errors.

----------------------------------------------

This documentation provides a comprehensive understanding of the RFID-based access control system. Let me know if you need further clarifications!

