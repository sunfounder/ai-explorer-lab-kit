from fusion_hat import MPU6050, Pin
from time import sleep,time
import openai
from keys import OPENAI_API_KEY
import sys,os
import subprocess
from pathlib import Path

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)
os.system("fusion_hat enable_speaker")

TTS_OUTPUT_FILE = 'tts_output.mp3'

instructions_text = '''
You are a smart fitness assistant. Your task is to analyze the user's dumbbell workout based on the number of lifts and speed data, then provide feedback and recommendations.

### Input Format:
"The number of times you lift dumbbells: [count], Motion data: [(timestamp, speed), (timestamp, speed), ...]"

### Output Guidelines:
1. **If the user stops lifting for 5 seconds**, acknowledge the session's completion and summarize performance.
2. **Analyze lifting consistency**:
   - If speed varies greatly, suggest maintaining a steady pace.
   - If speed is increasing, praise progress and encourage continued effort.
   - If speed is decreasing, suggest focusing on endurance.
3. **Encourage based on repetition count**:
   - **<10 reps**: Motivate the user to do more.
   - **10-30 reps**: Encourage consistency.
   - **>30 reps**: Praise the effort and suggest a rest.
4. **Provide fitness insights**:
   - If the user lifts too fast, suggest controlled movements for muscle engagement.
   - If the user lifts too slow, suggest increasing intensity for better endurance.
5. **Ensure responses are engaging and motivational**.

### Example Inputs & Outputs:

**Example 1:**
Input:  
"The number of times you lift dumbbells: 5, Motion data: [(1700000000, 0.2), (1700000002, 0.25), (1700000004, 0.22)]"

Output:  
"You've lifted the dumbbell 5 times. Keep going! Try to maintain a steady rhythm to maximize your gains."

---

**Example 2:**
Input:  
"The number of times you lift dumbbells: 35, Motion data: [(1700000000, 0.3), (1700000001, 0.32), (1700000002, 0.31)]"

Output:  
"Great job! You've completed 35 reps with excellent consistency. Take a short break and stay hydrated before your next set."

---

**Example 3:**
Input:  
"The number of times you lift dumbbells: 20, Motion data: [(1700000000, 0.4), (1700000002, 0.6), (1700000004, 0.2)]"

Output:  
"You're at 20 reps, but your speed fluctuates. Try to maintain a controlled pace for better strength gains!"
'''

assistant = client.beta.assistants.create(
    name="BOT",
    instructions=instructions_text,
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()

def text_to_speech(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",  # Low-latency TTS model for real-time usage
        voice="alloy",  # Selected voice for audio playback
        input=text  # Text to convert to speech
    ) as response:
        response.stream_to_file(speech_file_path) # Save audio to the specified file
    p=subprocess.Popen("mplayer speech.mp3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()


# Define GPIO pins for the 74HC595 shift register
SDI = Pin(17,Pin.OUT)   # Serial Data Input
RCLK = Pin(4,Pin.OUT)  # Register Clock
SRCLK = Pin(27,Pin.OUT) # Shift Register Clock


# Define GPIO pins for digit selection on the 7-segment display
placePin = [Pin(pin,Pin.OUT) for pin in (23, 24, 25, 12)]

# Define segment codes for numbers 0-9 for the 7-segment display
number = (0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90)


def clearDisplay():
    """ Clear the 7-segment display. """
    for _ in range(8):
        SDI.high()
        SRCLK.high()
        SRCLK.low()
    RCLK.high()
    RCLK.low()

def hc595_shift(data):
    """ Shift a byte of data to the 74HC595 shift register. """
    for i in range(8):
        SDI.value(0x80 & (data << i))  # Set SDI high/low based on data bit
        SRCLK.high()  # Pulse the Shift Register Clock
        SRCLK.low()
    RCLK.high()  # Latch data on the output by pulsing Register Clock
    RCLK.low()

def pickDigit(digit):
    """ Select a digit for display on the 7-segment display. """
    for pin in placePin:
        pin.low()  # Turn off all digit selection pins
    placePin[digit].high()  # Turn on the selected digit

def display(count):
    """ Main loop to update the 7-segment display with count value. """
    for i in range(4):  # Loop through each digit
        clearDisplay()  # Clear display before setting new digit
        pickDigit(i)    # Select digit for display

        # Choose the digit of count to display
        digit = (count // (10 ** (3-i))) % 10

        hc595_shift(number[digit])  # Shift digit value to 74HC595
        sleep(0.001)  # Short delay for display stability

def destroy():
    """ Cleanup GPIO resources and stop timer on exit. """
    global timer1
    timer1.cancel()  # Stop the timer
    for device in [SDI, RCLK, SRCLK] + placePin:
        device.close()  # Close GPIO devices


mpu = MPU6050()

# mpu.set_accel_range(MPU6050.ACCEL_RANGE_2G)
# mpu.set_gyro_range(MPU6050.GYRO_RANGE_250DEG)

threshold_up = 11  # raise threshold
threshold_down = 8  # down threshold

last_state = "down"
time_last = time()
last_lift_time = time()
motion_data = []  # store timestamp for analysis
speed_list = []
count = 0


text_to_speech("Start exercise!")

while count <= 100:
    time_now = time()  # get current time
    dt = time_now - time_last  # calculate time interval
    time_last = time_now  # update last time

    acc_x, acc_y, acc_z = mpu.get_accel_data()

    # speed calculation
    v = abs(acc_z * dt) 

    # print("v:", v, "acc_z:", acc_z, "time:", dt)

    # detect lift
    if acc_z > threshold_up and last_state == "down":
        count += 1
        last_state = "up"

        # record motion data
        motion_data.append((time_now, v))
        last_lift_time = time_now  # update last_lift_time to current time only when a lift is detected

        print(f"Dumbbell lifts: {count}, Speed: {v:.2f} m/s")

    elif acc_z < threshold_down and last_state == "up":
        last_state = "down"

    # 5s to auto stop
    if time_now - last_lift_time > 30:
        print("No movement detected for 30 seconds. Ending session.")
        break

    display(count)
    sleep(0.2)
# send data to AI

try:
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

    # print("Run completed with status: " + run.status)

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        for message in messages.data:
            if message.role == 'assistant':
                for block in message.content:
                    if block.type == 'text':
                        label = assistant.name
                        value = block.text.value
                        print(f'{label:>10} >>> {value}')
                        text_to_speech(value)
                break # only last reply

finally:
    client.beta.assistants.delete(assistant.id)
