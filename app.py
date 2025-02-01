import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    # Access the content of the message using message.content
    response = "You said: " + message.content
    await cl.Message(content=response).send()
