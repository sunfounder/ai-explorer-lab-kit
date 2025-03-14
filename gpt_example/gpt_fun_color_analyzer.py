#!/usr/bin/env python3
import colorsys
from fusion_hat import Pin, RGB_LED, PWM, Rotary_Encoder
from signal import pause

import openai
from keys import OPENAI_API_KEY
import subprocess
import os
from pathlib import Path

os.system("fusion_hat enable_speaker")

# initialize openai client
client = openai.OpenAI(api_key=OPENAI_API_KEY)


instructions_text = '''
You are a mood-aware assistant. Your task is to interpret the user's environment based on RGB color values and provide mood-related insights or advice.

### Input Format:
"red: [value], green: [value], blue: [value]"

### Output Guidelines:
1. Analyze the RGB values to determine the overall mood or atmosphere.
2. If the color is warm (e.g., high red/yellow tones), describe it as cozy, energetic, or passionate.
3. If the color is cool (e.g., high blue/green tones), describe it as calming, relaxing, or refreshing.
4. If the color is neutral (e.g., balanced RGB), describe it as stable or neutral.
5. Provide mood-based advice or activities that suit the detected atmosphere.
6. Include the RGB values in your response to justify your interpretation.

### Example Input:
red: 255, green: 100, blue: 50

### Example Output:
The dominant warm tones (R: 255, G: 100, B: 50) create an energetic and cozy ambiance. This color is great for stimulating creativity and warmth. Consider using this lighting for social gatherings or artistic activities.
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

def change_color(encoder, led):
    """
    This function reads the position from the encoder and sets the LED color.
    The color is adjusted according to the hue value on the color wheel.
    """
    global r, g, b
    hue = encoder.steps() % 360  # Hue value cycles between 0 and 359
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)  # Full saturation and value for bright colors
    led.color = (int(r * 255), int(g * 255), int(b * 255))

def send_message(message):
    global r, g, b
    events = "red: {}, green: {}, blue: {}" .format(r, g, b)
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=events,
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
        text_to_speech(decoded_message)

    except Exception as e:
        print(f"Error in AI processing: {e}")

try:
    clk_pin = 17  # Example GPIO pin for CLK
    dt_pin = 4   # Example GPIO pin for DT
    encoder = Rotary_Encoder(clk_pin, dt_pin)
    sw = Pin(27, Pin.IN, pull= Pin.PULL_UP)  # Button (sw) connected to GPIO pin 27

    # Initialize an RGB LED. Connect the red component to P0, green to P1, and blue to P2.
    r,g,b = 0,0,0
    rgb_led = RGB_LED(PWM('P0'), PWM('P1'), PWM('P2'),common=RGB_LED.CATHODE)

    # Set the callback for when the encoder is rotated
    encoder.when_rotated = lambda: change_color(encoder, rgb_led)
    sw.when_activated = send_message

    pause()  # Wait indefinitely for events


finally:
    client.beta.assistants.delete(assistant.id)
