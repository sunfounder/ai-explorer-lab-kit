
.. _gpt_easy:


A Simple Conversation
======================

This example demonstrates how to use OpenAI's Python library to create and interact with a chatbot through a simple conversation.

----------------------------------------------



**Running the Example**

All example code used in these lessons is available in the ``ai-explorer-lab-kit`` directory. Follow these steps to run the example:

.. code-block:: shell

   cd ~/ai-explorer-lab-kit/gpt_examples/
   ~/my_venv/bin/python3 gpt_easy.py

----------------------------------------------

**Code**

Here is the complete example code:

.. code-block:: python

   import openai
   from keys import OPENAI_API_KEY

   # gets API Key from environment variable OPENAI_API_KEY
   client = openai.OpenAI(api_key=OPENAI_API_KEY)

   assistant = client.beta.assistants.create(
      name="BOT",
      instructions="You are an Assistant, you answer people's questions to help them.",
      model="gpt-4-1106-preview",
   )

   thread = client.beta.threads.create()

   message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content="Who are you?",
   )

   run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id,
      assistant_id=assistant.id,
   )

   if run.status == "completed":
      messages = client.beta.threads.messages.list(thread_id=thread.id)

      for message in messages:
         assert message.content[0].type == "text"
         print({"role": message.role, "message": message.content[0].text.value})

      client.beta.assistants.delete(assistant.id)


----------------------------------------------

**Code Explanation**

We can break the code into several parts and briefly explain the purpose of each part.

1. **Creating and Configuring the Client**

   First, create an API client instance and configure it using your API key. The client handles communication with OpenAI's servers by sending requests and receiving responses.

   .. code-block:: python

      import openai
      from keys import OPENAI_API_KEY

      # gets API Key from environment variable OPENAI_API_KEY
      client = openai.OpenAI(api_key=OPENAI_API_KEY)

2. **Creating the Assistant**

   Next, create an assistant.

   An Assistant is a specialized AI that uses OpenAI models to perform tasks via natural language understanding and generation. Assistants can be tailored to specific application scenarios.

   .. code-block:: python

      assistant = client.beta.assistants.create(
         name="BOT",
         instructions="You are an Assistant, you answer people's questions to help them.",
         model="gpt-4-1106-preview",
      )

   Here, we use `client` to create an assistant named "BOT." The assistant is instructed to help users by answering their questions and uses the latest GPT-4 model.




   **Using Models**

   You can interact with advanced models like GPT-4 or GPT-3.5, designed for various text generation tasks. As of December 2024, the available models include:

   .. list-table::
      :widths: 20 80
      :header-rows: 1

      * - Model
        - Description
      * - GPT-4o
        - High-intelligence flagship model for complex, multi-step tasks.
      * - GPT-4o mini
        - Lightweight, fast model for simpler tasks.
      * - o1-preview and o1-mini
        - Models trained with reinforcement learning for advanced reasoning.
      * - GPT-4
        - Earlier high-intelligence models.
      * - GPT-3.5 Turbo
        - A fast, inexpensive model for simple tasks.
      * - DALL·E
        - Image generation and editing from natural language prompts.
      * - TTS
        - Converts text into natural-sounding audio.
      * - Whisper
        - Transcribes audio into text.
      * - Embeddings
        - Converts text into numerical representations.
      * - Moderation
        - Detects potentially sensitive or unsafe text.

   .. note:: View https://platform.openai.com/docs/models for more information on the available models and their capabilities.


3. **Creating a Conversation Thread**

   .. code-block:: python

      thread = client.beta.threads.create()

   Create a conversation thread, which represents an independent session with the assistant. Each thread maintains consistent context, enabling uninterrupted multi-turn conversations. Reference the thread later using ``thread.id``.

4. **Sending a Message**

   .. code-block:: python

      message = client.beta.threads.messages.create(
         thread_id=thread.id,
         role="user",
         content="Who are you?",
      )

   Send a message to the assistant in the created thread. 
   Messages include the following parameters:


   * ``thread_id=thread.id``: Links the message to a specific thread.
   * ``role="user"``: Indicates the message is from the user. Other roles include:

      * ``user``: User messages.
      * ``assistant``: Assistant replies.
      * ``system``: System context and settings.

   * ``content="Who are you?"``: The content of the message.

   In practice, you can send multiple messages in a loop to engage in more complex conversations.

5. **Executing the Conversation**

   .. code-block:: python

      run = client.beta.threads.runs.create_and_poll(
         thread_id=thread.id,
         assistant_id=assistant.id,
      )

   Use the ``create_and_poll`` method to trigger the assistant's processing of user messages. Key parameters:
   
   * ``thread_id=thread.id``: Specifies the thread for this conversation.
   * ``assistant_id=assistant.id``: Specifies which assistant to use.

   Possible statuses:

   * ``completed``: The assistant successfully processed the message.
   * ``in_progress``: Processing is ongoing; wait a moment.
   * ``failed``: An error occurred during processing.

   For more control, use separate ``create`` and ``poll`` calls to enable asynchronous or staged processing.

6. **Checking the Results**

   .. code-block:: python

      if run.status == "completed":
         messages = client.beta.threads.messages.list(thread_id=thread.id)

   If the execution is completed, retrieve all messages in the thread. Each message includes critical fields:
   
   * ``role``: The sender's role (``user``, ``assistant``, or ``system``).
   * ``content``: The message content, typically as a text block (``type="text"``).

   .. code-block:: python

      for message in messages:
         assert message.content[0].type == "text"
         print({"role": message.role, "message": message.content[0].text.value})

   Iterate through all messages to print their roles and content.

   .. code-block:: python

      client.beta.assistants.delete(assistant.id)

   After completing the conversation, delete the assistant to free resources. Deleting the assistant makes related threads unusable, so skip this step if the assistant must remain active. However, ensure mechanisms are in place to manage thread resources.




--------------------------------------------



**Troubleshooting Common Issues**



When working with OpenAI's API and developing chatbots on a Raspberry Pi, you might encounter several common issues. This section provides solutions to help you resolve these problems quickly and ensure smooth operation of your applications.


1. **API Key Errors**

``Problem``: You receive errors related to the API key, such as "Invalid API Key" or "API Key not found."

``Solution``: Ensure that your API key is correctly entered in the keys.py file or the environment variable. Double-check that there are no extra spaces or typos. If the problem persists, regenerate a new API key from the OpenAI platform and update your configuration.

2. **Network Issues**

``Problem``: Your device struggles to connect to OpenAI's servers, resulting in timeouts or connectivity errors.

``Solution``: Verify your Raspberry Pi's internet connection. If connected via WiFi, ensure the signal is strong and stable. Consider using a wired connection if possible. Additionally, check if any firewall settings or network policies are blocking access to OpenAI's servers.

3. **Model Limitations**

``Problem``: The responses from the assistant are not as expected, or the model fails to understand complex queries.

``Solution``: Ensure you are using the appropriate model for your task. For complex queries, consider switching to a more advanced model like GPT-4. Also, review the instructions and context provided to the assistant to ensure they are clear and concise.

4. **Python Dependency Issues**

``Problem``: Errors occur during the installation or execution of Python dependencies.

``Solution``: Verify that all dependencies are compatible with your Python version. Use a virtual environment to avoid conflicts between project dependencies. If issues persist, consider reinstalling the dependencies or Python itself.















.. 一次最简单的交谈
.. ==================

.. 这个示例主要展示了如何使用OpenAI的Python库来创建和使用一个聊天机器人，并与它进行一次简短的对话。



.. **运行示例**

.. 我们提供了这些课程用到的所有示例代码。位于 ``ai-explorer-lab-kit`` 目录下。
.. 你可以按以下步骤执行指令，来启动这个示例。

.. .. code-block:: shell

..    cd ~/ai-explorer-lab-kit/gpt_examples/
..    ~/my_venv/bin/python3 gpt_easy.py

.. **Code**

.. 完整示例代码如下所示：

.. .. code-block:: python

..    import openai
..    from keys import OPENAI_API_KEY

..    # gets API Key from environment variable OPENAI_API_KEY
..    client = openai.OpenAI(api_key=OPENAI_API_KEY)

..    assistant = client.beta.assistants.create(
..       name="BOT",
..       instructions="You are a Assistant, you answer people question to help them.",
..       model="gpt-4-1106-preview",
..    )

..    thread = client.beta.threads.create()

..    message = client.beta.threads.messages.create(
..       thread_id=thread.id,
..       role="user",
..       content="who are you?",
..    )

..    run = client.beta.threads.runs.create_and_poll(
..       thread_id=thread.id,
..       assistant_id=assistant.id,
..    )

..    if run.status == "completed":
..       messages = client.beta.threads.messages.list(thread_id=thread.id)

..       for message in messages:
..          assert message.content[0].type == "text"
..          print({"role": message.role, "message": message.content[0].text.value})

..       client.beta.assistants.delete(assistant.id)


.. **代码解析**


.. 我们可以将其分解成几个部分，并简单解释每一部分的功能和目的。下面是逐步的解释：


.. 1.  创建和配置客户端


..    首先，你需要创建一个API客户端实例，并使用你的API密钥进行配置。
..    这个客户端将负责与OpenAI的服务器进行通信，发送请求和接收响应。

..    .. code-block:: python

..       import openai
..       from keys import OPENAI_API_KEY

..       # gets API Key from environment variable OPENAI_API_KEY
..       client = openai.OpenAI(api_key=OPENAI_API_KEY)


.. 2.  创建助手

..    接下来，你需要创建一个助手。

..    Assistant 是一种专用 AI，基于 OpenAI 提供的模型，设计用于完成各种自然语言任务，如问题解答、内容生成等。

..    .. code-block:: python

..       assistant = client.beta.assistants.create(
..          name="BOT",
..          instructions="You are a Assistant, you answer people question to help them.",
..          model="gpt-4-1106-preview",
..       )

..    在这里，我们使用 ``client`` 创建一个名为 "BOT" 的聊天助手。
..    我们定义了这个助手的基本指导原则——回答人们的问题来帮助他们，
..    它基于最新版本的GPT-4模型。


..    **使用模型**

..    你可以与一些先进的机器学习模型进行交互，比如GPT-4o或GPT-4，这些模型被设计来处理各种文本生成任务。

..    截止至2024年12月，你能调用的模型包括但不限于以下列表。

..    .. list-table::
..       :widths: 20 80
..       :header-rows: 1

..       *   - Model	
..          - Description
..       *   - GPT-4o	
..          - Our high-intelligence flagship model for complex, multi-step tasks
..       *   - GPT-4o mini	
..          - Our affordable and intelligent small model for fast, lightweight tasks
..       *   - o1-preview and o1-mini	
..          - Language models trained with reinforcement learning to perform complex reasoning.
..       *   - GPT-4 
..          - Turbo and GPT-4	The previous set of high-intelligence models
..       *   - GPT-3.5 
..          - Turbo	A fast, inexpensive model for simple tasks
..       *   - DALL·E	
..          - A model that can generate and edit images given a natural language prompt
..       *   - TTS	
..          - A set of models that can convert text into natural sounding spoken audio
..       *   - Whisper	
..          - A model that can convert audio into text
..       *   - Embeddings	
..          - A set of models that can convert text into a numerical form
..       *   - Moderation	
..          - A fine-tuned model that can detect whether text may be sensitive or unsafe


.. 3.  创建对话线程

..    .. code-block:: python

..       thread = client.beta.threads.create()

..    创建一个对话线程，这是与助手交互的一个独立会话。
..    创建对话线程 ``thread`` 是与助手交互的基础。
..    每个对话线程可以看作是与助手的一次独立会话，它保持了上下文一致性。
..    例如，如果你在一个线程中问“你是谁？”，助手会根据当前上下文提供回答。
..    线程的概念使得多个独立会话不会互相干扰，非常适合需要保持连续性对话的应用。

..    你可以在之后的 API 调用中通过 ``thread.id`` 来引用这个线程。

.. 4.  发送消息

..    .. code-block:: python

..       message = client.beta.threads.messages.create(
..          thread_id=thread.id,
..          role="user",
..          content="who are you?",
..       )

..    在创建的线程中，以用户的身份发送消息给助手。
..    发送消息是与助手交互的核心步骤。
..    通过指定 ``role`` 和 ``content``，用户可以向助手发送问题或指令。

..    这个代码包含以下几个参数：

..    * ``thread_id=thread.id``：将消息关联到特定的线程。
..    * ``role="user"``：表示消息是由用户发送的。OpenAI API 支持不同的角色，如：
..       * ``user``: 用户发出的消息。
..       * ``assistant``: 助手的回复。
..       * ``system``: 系统信息，用于设定对话背景和上下文。
..    * ``content="who are you?"``：消息的具体内容，可以是问题、命令或描述性文本。
   
..    在实际的使用场景中，你可以在循环中连续发送多条消息，与助手进行复杂对话。

.. 5.  执行对话

..    .. code-block:: python

..       run = client.beta.threads.runs.create_and_poll(
..          thread_id=thread.id,
..          assistant_id=assistant.id,
..       )

..    调用 ``create_and_poll`` 方法会触发助手处理用户发送的消息。
..    这个方法会等待助手完成对话处理，然后返回结果。

..    其参数：
..    * ``thread_id=thread.id``：指定要在哪个对话线程中运行对话。
..    * ``assistant_id=assistant.id``：指定使用哪个助手来处理消息。

..    这个方法的执行结果有以下几种：
..    * ``completed``：助手成功处理了消息。
..    * ``in_progress``：助手仍在处理中，通常只需等待一段时间。
..    * ``failed``：助手处理消息时发生错误。

..    如果你希望更高的控制，可以拆分为两个步骤：
..    1. 调用 ``create`` 启动对话处理。
..    2. 使用 ``poll`` 检查执行状态。
..    这对需要异步或分阶段处理的应用非常有用。

.. 6.  检查执行结果

..    .. code-block:: python

..       if run.status == "completed":
..          messages = client.beta.threads.messages.list(thread_id=thread.id)

..    检查对话的执行状态。如果执行完成，它将获取线程中的所有消息。这包括用户发送的消息和助手的回复。

..    一次完整的对话中会产生以下 ``messages``。
..    你能看到消息中包含了许多内容，在这里我们不一一讲解，只需要找到我们需要的几条就可以了。

..    .. code-block:: python
..       :emphasize-lines: 9,10,17,28,29,36

..       SyncCursorPage[Message](
..          data=[
..          Message(id='msg_Qp26GXXXXXXXXXXXXXXXXXXXX',
..          assistant_id='asst_oRSXXXXXXXXXXXXXXXXXXXXXX',
..          attachments=[],
..          completed_at=None,
..          content=[
..                TextContentBlock(text=Text(annotations=[],
..                value="I'm an Assistant here to help you. How can I assist you today?"),
..                type='text')
..                ],
..          created_at=1729678574,
..          incomplete_at=None,
..          incomplete_details=None,
..          metadata={},
..          object='thread.message',
..          role='BOT', 
..          run_id='run_diHkXXXXXXXXXXXXXXXXXXXXXXX', 
..          status=None, 
..          thread_id='thread_rRy5gZeXXXXXXXXXXXXXXXXXXXXXXp'), 

..          Message(id='msg_qmXXXXXXXXXXXXXXXXXXXXX', 
..          assistant_id=None, 
..          attachments=[], 
..          completed_at=None, 
..          content=[
..                TextContentBlock(text=Text(annotations=[], 
..                value='who are you?'), 
..                type='text')
..             ], 
..          created_at=1729678568, 
..          incomplete_at=None, 
..          incomplete_details=None, 
..          metadata={}, 
..          object='thread.message', 
..          role='user', 
..          run_id=None, 
..          status=None, 
..          thread_id='thread_rRyXXXXXXXXXXXXXXXXXXXX')], 

..    每条消息包含以下关键字段：
..    * ``role``：消息的角色（ ``user``、 ``assistant`` 或 ``system``）。
..    * ``content``：消息的内容，可以是文本块（ ``type="text"``）或其他数据（如代码、图片等）。

..    .. code-block:: python

..       for message in messages:
..          assert message.content[0].type == "text"
..          print({"role": message.role, "message": message.content[0].text.value})

..    遍历所有消息，我们需要从中找到每条消息包括发送者的角色和消息内容。将它们打印出来。


..    .. code-block:: python

..       client.beta.assistants.delete(assistant.id)

..    对话完成后，删除创建的助手，清理资源。
..    删除助手是保持资源有效利用的最佳实践，特别是在需要频繁创建和销毁助手的场景中。需要注意的是，删除助手会使所有与其相关的线程失效，请确保这些线程不再需要使用。

..    如果助手需要长时间保持活跃，可以跳过删除步骤，但需要管理对话线程的上下文。
..    除此之外，你还得确保有机制避免线程资源无限增长。
