.. _gpt_easy_keyboard:

1.3 Real-Time Interaction
==========================

This example demonstrates a basic chatbot that can interact with users in real time, process input, and return generated responses. It showcases how to use the OpenAI API and handle sending and receiving text messages.

----------------------------------------------

**Running the Example**

All example code used in these lessons is available in the ``ai-explorer-lab-kit`` directory. 
You can follow these steps to run the example:


.. code-block:: shell

   cd ~/ai-explorer-lab-kit/gpt_example/
   sudo ~/my_venv/bin/python3 gpt_easy_keyboard.py


----------------------------------------------

**Code**

The complete example code is as follows:

.. code-block:: python

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

----------------------------------------------

**Code Explanation**

This example builds upon :ref:`gpt_easy` with two notable changes:

1.  Adding Keyboard Input

   .. code-block:: python
      :emphasize-lines: 4,5,18,19,20,21,22

      import openai
      from keys import OPENAI_API_KEY

      import readline # Enhances command-line input, like text navigation and history.
      import sys # Provides access to system-specific parameters and functions.

      # gets API Key from environment variable OPENAI_API_KEY
      client = openai.OpenAI(api_key=OPENAI_API_KEY)

      assistant = client.beta.assistants.create(
         ...
      )

      thread = client.beta.threads.create()

      try:
         while True:
            msg = ""
            msg = input(f'\033[1;30m{"intput: "}\033[0m').encode(sys.stdin.encoding).decode('utf-8')
            if msg == False or msg == "":
               print() # new line
               continue

            ...

   The ``readline`` library enhances interactive command-line input in Unix-like environments. It allows features like navigating input history and autocompletion, improving the user experience. The ``sys`` library is used here to handle system-specific input encoding, ensuring compatibility across platforms.

   In the main loop, user input is processed and sent to the assistant. Empty inputs are ignored.

   Key line for input handling:

   .. code-block:: python

      msg = input(f'\033[1;30m{"input: "}\033[0m').encode(sys.stdin.encoding).decode('utf-8')


   Explanation:

   * ``input()`` : Reads a line of input from the keyboard.
   * ``f'\033[1;30m{"input: "}\033[0m'`` : Displays a colored prompt in the terminal.

      * ``\033[1;30m`` : ANSI escape sequence to set text color to grey with bold formatting.
      * ``\033[0m`` : Resets text formatting to default.

   * ``.encode()`` and ``.decode()``: Convert input to and from the system's standard encoding (e.g., UTF-8), ensuring compatibility with different platforms.


2.  Improving Output Display:

   .. code-block:: python

      while True:

         ...

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


   This code receives and prints information in the main loop. ``messages`` stores all the messages in this conversation. 
   When traversing the messages, multiple messages will be obtained, so ``break`` is needed to terminate the traversal and only obtain the latest message of each character.

-----------------------------------------------------

**Error Handling**

Effective error handling is crucial in maintaining the reliability and usability of any real-time chatbot application. When integrating the OpenAI API in your Raspberry Pi projects, you'll likely encounter various errors that can affect the performance and output of your chatbot. Here’s how to handle some common scenarios:

1. API Connection Errors

``Problem``: Failures in connecting to the OpenAI API, which might be caused by network issues, incorrect API keys, or server downtime.

``Solution``: Implement retries for failed requests with exponential backoff. Use a try-except block to catch connection errors and attempt to reconnect after a short delay. Ensure your API key is correctly configured and valid.

.. code-block:: python

   import time import requests

   def send_request(data): 
      retry_count = 0 
      while retry_count < 5: 
         try: 
            response = client.beta.threads.messages.create(**data) 
            return response
         except requests.exceptions.ConnectionError: 
            time.sleep(2 ** retry_count) # Exponential backoff 
            retry_count += 1 
         except openai.Error as e: 
            print(f"API Error: {e}") 
            break 
      else: 
         print("Failed to connect to OpenAI after several attempts.")

2. Rate Limiting and Quotas

``Problem``: Exceeding the API rate limits or quota restrictions, resulting in HTTP 429 (Too Many Requests) errors.

``Solution``: Monitor your API usage carefully and consider implementing rate limiting on your end to prevent hitting the cap. Handle 429 status codes specifically in your code to pause or slow down requests.

.. code-block:: python

   def handle_api_call(data):
      try:
         response = send_request(data)
         if response.status_code == 429:
               print("Rate limit exceeded. Waiting before retrying...")
               time.sleep(60)  # Wait for 1 minute before retrying
               return send_request(data)
         return response
      except Exception as e:
         print(f"Unhandled exception: {e}")

3. Invalid Requests

``Problem``: Sending invalid data or parameters to the API, resulting in HTTP 400 (Bad Request) errors.

``Solution``: Validate all inputs before sending them to the API. Provide clear error messages to the user if the input data does not meet the required format or criteria.

.. code-block:: python

   def validate_input(user_input):
      if not user_input.strip():
         raise ValueError("Input cannot be empty.")
      # Additional validation based on expected input types

   try:
      user_input = input("Input: ")
      validate_input(user_input)
      data = {'thread_id': thread.id, 'role': 'user', 'content': user_input}
      response = send_request(data)
      print("Response received:", response.data)
   except ValueError as ve:
      print(ve)

4. Handling Unexpected Errors

``Problem``: Encountering unexpected or miscellaneous errors that do not fit into common categories.

``Solution``: Use a broad exception handler as a last resort to catch and log any unexpected errors. This ensures that the application can gracefully handle unforeseen issues without crashing.

.. code-block:: python

   try:
      # Attempt to execute API call
      response = handle_api_call(data)
      print("Assistant response:", response.data)
   except Exception as e:
      print(f"An unexpected error occurred: {e}")

Incorporating these error handling strategies will help ensure that your chatbot remains responsive and robust in the face of common operational challenges. Always test these scenarios during development to refine your approach and improve the experience.

