import openai
from keys import OPENAI_API_KEY


# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)

assistant = client.beta.assistants.create(
    name="BOT",
    instructions="You are a Assistant, you answer people question to help them.",
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="who are you?",
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

# print("Run completed with status: " + run.status)


if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # print("messages: ")
    # print(messages)

    for message in messages:
        assert message.content[0].type == "text"
        print({"role": message.role, "message": message.content[0].text.value})

    client.beta.assistants.delete(assistant.id)


####  MESSAGE 

    # SyncCursorPage[Message](
    #     data=[
    #      Message(id='msg_Qp26GzzCn6ytIWdRJTUZhZwH',
    #      assistant_id='asst_oRS2VgxrkCUz05Vu0KzgLW6P',
    #      attachments=[],
    #      completed_at=None,
    #      content=[
    #             TextContentBlock(text=Text(annotations=[],
    #             value="I'm not Tommy, I'm an Assistant here to help you. How can I assist you today?"),
    #             type='text')
    #             ],
    #      created_at=1729678574,
    #      incomplete_at=None,
    #      incomplete_details=None,
    #      metadata={},
    #      object='thread.message',
    #      role='assistant', 
    #      run_id='run_diHkdtJaJCDM2LGAzePLcl87', 
    #      status=None, 
    #      thread_id='thread_rRy5gZe0C4ZwaIaSxHF8g79p'), 

    #      Message(id='msg_qmWfYQqlSUeManOjlSHKWEX9', 
    #      assistant_id=None, 
    #      attachments=[], 
    #      completed_at=None, 
    #      content=[
    #             TextContentBlock(text=Text(annotations=[], 
    #             value='Tommy, Can you here me?'), 
    #             type='text')
    #         ], 
    #      created_at=1729678568, 
    #      incomplete_at=None, 
    #      incomplete_details=None, 
    #      metadata={}, 
    #      object='thread.message', 
    #      role='user', 
    #      run_id=None, 
    #      status=None, 
    #      thread_id='thread_rRy5gZe0C4ZwaIaSxHF8g79p')], 

    #      object='list', 
    #      first_id='msg_Qp26GzzCn6ytIWdRJTUZhZwH', 
    #      last_id='msg_qmWfYQqlSUeManOjlSHKWEX9', 
    #      has_more=False)
        


# Run(id='run_cHugQL63P8W4RGowfGWAazUw', 
#     assistant_id='asst_oRS2VgxrkCUz05Vu0KzgLW6P', 
#     cancelled_at=None, 
#     completed_at=1729759098, 
#     created_at=1729759097, 
#     expires_at=None, 
#     failed_at=None, 
#     incomplete_details=None, 
#     instructions='You are a Assistant, you answer people question to help them', 
#     last_error=None, 
#     max_completion_tokens=None, 
#     max_prompt_tokens=None, 
#     metadata={}, 
#     model='gpt-3.5-turbo-0125', 
#     object='thread.run', 
#     parallel_tool_calls=True, 
#     required_action=None, 
#     response_format='auto', 
#     started_at=1729759098, 
#     status='completed', 
#     thread_id='thread_mtUIswzdbNUnIIldfoB95zlL', 
#     tool_choice='auto', 
#     tools=[], 
#     truncation_strategy=TruncationStrategy(type='auto', 
#     last_messages=None), 
#     usage=Usage(completion_tokens=22, 
#     prompt_tokens=26, 
#     total_tokens=48), 
#     temperature=1.0, 
#     top_p=1.0, 
#     tool_resources={})