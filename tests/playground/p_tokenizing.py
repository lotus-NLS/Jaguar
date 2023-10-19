from src.l3_lotus_core import Entry, DialogueRole
from src.l2_lotus_agent import Tokenizer

# ---------------------------------------------------------

import tiktoken

example_messages = [
    {
        "role": "system",
        "content": "You are a helpful, pattern-following assistant that translates corporate jargon into plain English.",
    },
    {
        "role": "system",
        "name": "example_user",
        "content": "New synergies will help drive top-line growth.",
    },
    {
        "role": "system",
        "name": "example_assistant",
        "content": "Things working well together will increase revenue.",
    },
    {
        "role": "system",
        "name": "example_user",
        "content": "Let's circle back when we have more bandwidth to touch base on opportunities for increased leverage.",
    },
    {
        "role": "system",
        "name": "example_assistant",
        "content": "Let's talk later when we're less busy about how to do better.",
    },
    {
        "role": "user",
        "content": "This late pivot means we don't have time to boil the ocean for the client deliverable.",
    },
]
entries = []
for message in example_messages:
    role = message['role']
    content = message['content']
    name = message.get('name')



    entry = Entry(role=DialogueRole(role=role) ,msg=content, name=name)
    entries.append(entry)

from src.l0_lotus_run.entities import Alpha

alpha_agent = Alpha()
funct_docts = alpha_agent.tool_handler.get_public_tool_docs()

test_tokenizer = Tokenizer(tiktoken.get_encoding('cl100k_base'))

print(f'Total tokens: {test_tokenizer.get_context_tokens(entries=entries,funct_docs=funct_docts)}')