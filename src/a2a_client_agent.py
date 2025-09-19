
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
        self.timeout = 30
        self.retry_attempts = 3
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
async def send_message(client, text: str):
    message_payload = Message(
        role=Role.user,
        messageId=str(uuid.uuid4()),
        parts=[Part(root=TextPart(text=text))]
    )

    async for response in client.send_message(message_payload):
        # Print simplified output
        print(f"[{response.role}] {response.parts[0].root.text}")
        print("------")

# -------------------------------
# Main function
# -------------------------------
async def main():
    async with httpx.AsyncClient() as httpx_client:
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
        await send_message(client, "Hello, how are you?")
        await send_message(client, "This is a second test message!")

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    asyncio.run(main())

