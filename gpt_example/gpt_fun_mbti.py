import openai
from keys import OPENAI_API_KEY
import sys
from fusion_hat import Keypad

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

instructions_text = '''
You are an MBTI personality test assistant. Your role is to ask me a series of personality-related questions and assess my MBTI type based on my responses. Please follow these guidelines:

1. **Rules Overview**: Before asking, briefly explain how the test works and how I should answer.
2. **Numbered Questions**: Each question must be labeled with a number (e.g., “Question 1: …,” “Question 2: …”) for clarity.
3. **Answer Format**: I will respond with a number from 1 to 5, where:
   - 1: Strongly disagree
   - 2: Disagree
   - 3: Neutral
   - 4: Agree
   - 5: Strongly agree
4. **Question Count**: After I have answered 10 questions, please use my responses to generate my MBTI result and provide a concise explanation.
5. **Style Requirements**: Maintain a concise, friendly tone without adding extraneous details.

Once all 10 questions are answered, please provide a summary and give me the final MBTI result.
'''

# Create or retrieve the assistant
assistant = client.beta.assistants.create(
    name="MBTI_Assistant",
    instructions=instructions_text,
    model="gpt-4-1106-preview",
)

# Create a conversation thread
thread = client.beta.threads.create()


def process_user_input(keypad, count):
    """
    Handles user input through the keypad or initiates the test.
    """
    if count == 0:
        return "10 questions to test personality! Let's go!", count + 1

    while True:
        pressed_keys = keypad.read()
        if pressed_keys:
            print(f"Key pressed: {pressed_keys}")
            return pressed_keys[0], count + 1


try:
    # Configure rows, columns, and keypad layout
    rows_pins = [4, 17, 27, 22]
    cols_pins = [23, 24, 25, 12]
    keys = ["1", "2", "3", "A",
            "4", "5", "6", "B",
            "7", "8", "9", "C",
            "*", "0", "#", "D"]

    keypad = Keypad(rows_pins, cols_pins, keys)
    count = 0

    while count<=10:

        msg = ""
        msg, count = process_user_input(keypad, count)

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
                            print(f'{label:>10} >>> {value}')
                    break # only last reply

    input("\n Press enter for quit.")

finally:
    client.beta.assistants.delete(assistant.id)
    print("\n Delete Assistant ID")
