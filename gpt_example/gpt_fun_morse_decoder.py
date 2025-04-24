import openai
from keys import OPENAI_API_KEY
from fusion_hat import Pin
from signal import pause
import time

# init openai
client = openai.OpenAI(api_key=OPENAI_API_KEY)

assistant = client.beta.assistants.create(
    name="BOT",
    instructions="You are a Morse code decoder. Decode based on the button press time, interpreting short presses as dots and long presses as dashes. The message you receive may be a word or a sentence, please decode it and output it.",
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()

# setup GPIO
morse_input = Pin(22, Pin.IN, pull= Pin.PULL_DOWN)  
start_stop_button = Pin(17, Pin.IN, pull= Pin.PULL_DOWN)  
led = Pin(27, Pin.OUT)  # indicate LED to GPIO 27

# store the morse code events
morse_events = []
input_active = False  # flag to indicate if the input is active

# send the morse code to the AI for decoding
def decode_and_speak():
    global morse_events
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=str(morse_events),
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
       )

        # print("Run completed with status: " + run.status)

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            for message in messages.data:
                if message.role == 'assistant':
                    for block in message.content:
                        if block.type == 'text':
                            decoded_message = block.text.value
                    break # only last reply

        print(f"Decoded Message: {decoded_message}")
    except Exception as e:
        print(f"Error in decoding: {e}")
    morse_events = []  # clear the morse code events

# morse code input
start_time = 0

def morse_input_pressed():
    global start_time
    start_time = time.time()  

def morse_input_released():
    release_time = time.time()  
    if release_time - start_time < 0.1:
        return  # debounce
    morse_events.append(('pressed', start_time))
    morse_events.append(('released', release_time))
    print(f" Pressed at {start_time}-{release_time}")

# start/stop button
def handle_start_stop():
    global input_active
    if input_active:
        led.off()
        print("Input stopped and decoded.")
        decode_and_speak()
        input_active = False
    else:
        input_active = True
        morse_events.clear()
        led.on()
        print("Input started.")

# add event listeners
morse_input.when_activated = morse_input_pressed
morse_input.when_deactivated = morse_input_released
start_stop_button.when_activated = handle_start_stop

try:
    print("Morse Code Decoder is running. Press CTRL+C to exit.")
    handle_start_stop()
    pause()

finally:
    client.beta.assistants.delete(assistant.id)
    print("\n Delete Assistant ID")