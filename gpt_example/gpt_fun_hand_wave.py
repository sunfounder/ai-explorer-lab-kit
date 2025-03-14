import openai
from keys import OPENAI_API_KEY
import time
from fusion_hat import Pin
from signal import pause

# init openai
client = openai.OpenAI(api_key=OPENAI_API_KEY)

assistant = client.beta.assistants.create(
    name="BOT",
    instructions="You function as a gesture interaction device equipped with two infrared obstacle avoidance sensors positioned approximately 10 cm apart. You will receive trigger information from these sensors in the format: {('left', timestamp), ('right', timestamp)}. Based on the time difference between these triggers, determine if the user is waving their hand. Provide appropriate responses, such as 'You waved quickly from left to right, hello!' or 'You waved slowly twice on the left side, hello!'.",
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()


# setup GPIO
sensor_left = Pin(17, Pin.IN, Pin.PULL_UP)
sensor_right = Pin(22, Pin.IN, Pin.PULL_UP)
led = Pin(27, Pin.OUT)  # indicate LED connect to GPIO 27
led.on()

# store timestamp of sensor triggered
events = []

def sensor_triggered(sensor_id):
    global events
    timestamp = time.time()
    events.append((sensor_id, timestamp))
    print(f"Sensor {sensor_id} triggered at {timestamp}")

    # when sensor triggered twice, analyze the hand wave
    if len(events) >= 2:
        analyze_hand_wave()

def analyze_hand_wave():
    global events
    # insure the events list has at least two elements
    if len(events) < 2:
        return
    print("Start analyzing hand wave...")
    led.off()

    # send events to AI for decoding
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=str(events),
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

        # clear events list
        events.clear()
        led.on()

    except Exception as e:
        print(f"Error in AI processing: {e}")

# set sensor callbacks
sensor_left.when_activated = lambda: sensor_triggered('left')
sensor_right.when_activated = lambda: sensor_triggered('right')

try:
    print("Press CTRL+C to exit.")
    pause()

finally:
    print("Resources cleaned up. Exiting.")
    client.beta.assistants.delete(assistant.id)
    