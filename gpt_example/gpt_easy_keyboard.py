import openai
from keys import OPENAI_API_KEY

import readline # Enhances command-line input, like text navigation and history.
import sys # Provides access to system-specific parameters and functions.

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)

assistant = client.beta.assistants.create(
    name="BOT",
    instructions="You are a chat bot, you answer people question to help them. ",
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()

try:
    while True:
        msg = ""
        msg = input(f'\033[1;30m{"intput: "}\033[0m').encode(sys.stdin.encoding).decode('utf-8')
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

        # print("Run completed with status: " + run.status)

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

finally:
    client.beta.assistants.delete(assistant.id)
    print("\n Delete Assistant ID")
