
import uuid
import asyncio
import httpx
from a2a.client import A2ACardResolver, ClientFactory
from a2a.types import Message, Part, Role, TextPart

# -------------------------------
# Constants
# -------------------------------
BASE_URL = "http://localhost:9999"
PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"

# -------------------------------
# MinimalConfig for BaseClient
# -------------------------------
class MinimalConfig:
    def __init__(self, httpx_client):
        self.supported_transports = ["JSONRPC"]
        self.use_client_preference = True
        self.httpx_client = httpx_client
        self.timeout = 300
        self.retry_attempts = 5
        self.log_level = "INFO"
        self.enable_metrics = False
        self.default_headers = {}
        self.accepted_output_modes = ["text"]
        self.polling = True
        self.push_notification_configs = None
        self.extensions = None
        self.state_transition_history = None
        self.streaming = None
        self.other_configs = {}

# -------------------------------
# Helper function to send a message
# -------------------------------
# async def send_message(client, text: str):
#     message_payload = Message(
#         role=Role.user,
#         messageId=str(uuid.uuid4()),
#         parts=[Part(root=TextPart(text=text))]
#     )

#     async for response in client.send_message(message_payload):
#         # Print simplified output
#         print("---Agent response---")
#         print(f"[{response.role}] {response.parts[0].root.text}")
#         print("---Agent response---")

async def send_langgraph_message(client, text: str):
    #prompt1
    #user_message = '{"name":"add","parameters":{"a":"23","b":"45"}}'

    #prompt2
    #user_message = '{"name":"multiply","parameters":{"a":"23","b":"45"}}'

    #prompt3
    #user_message = '{"name":"weather alert","parameters":{"state":"CA"}}'

    #prompt4
    #user_message = '{"name":"weather forcast for State","parameters":{"state":"CA"}}'

    #prompt5
    #user_message = '{"name":"airbnb prices for Banff national park in Canada"}'

    #prompt6
    #user_message = "Open Google and search for Groq information using Playwright"

     #prompt6
    #user_message = "add two numbers 234 and 34"
    #user_message="forcast weather for State -CA"
    user_message="Open Google and search for Groq information"


    # Set the skill you want to call
    #"Run my LangGraph agent, add two numbers 23 and 45!"
    message_payload = Message(
        role=Role.user,
        messageId=str(uuid.uuid4()),
        parts=[Part(root=TextPart(text=user_message))],
    )

    async for response in client.send_message(message_payload):
        # Print simplified output
        print("--Langgrapgh response----")
        print(f"[{response.role}] {response.parts[0].root.text}")
        print("--Langgrapgh response----")

# -------------------------------
# Main function
# -------------------------------
async def main():
    timeout = httpx.Timeout(300.0, connect=60.0) 
    async with httpx.AsyncClient(timeout=timeout) as httpx_client:
        # Fetch agent card
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=BASE_URL)
        print(f"Fetching public agent card from: {BASE_URL}{PUBLIC_AGENT_CARD_PATH}")
        agent_card = await resolver.get_agent_card()
        print("Fetched public agent card")
        print(agent_card.model_dump_json(indent=2))

        # Initialize client
        factory = ClientFactory(config=MinimalConfig(httpx_client))
        client = factory.create(card=agent_card)
        print("A2AClient initialized")

        # Send messages
        # await send_message(client, "Hello, how are you?")
        # await send_message(client, "This is a second test message!")

        # Set the skill you want to call
        # client is already your BaseClient created with ClientFactory

        await send_langgraph_message(client, "Run my LangGraph agent ,add two number 23 and 45!")
        
       # await send_message(client, "Hello, how are you?")

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    asyncio.run(main())

