import asyncio
import random
import sys

from copilot import CopilotClient, PermissionHandler
from copilot.generated.session_events import SessionEventType
from copilot.tools import define_tool
from pydantic import BaseModel, Field


class GetWeatherParams(BaseModel):
    city: str = Field(description="The city name to get weather for")


@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": params.city, "temperature": f"{temp}°F", "condition": condition}


async def run_session(prompt: str | None = None) -> None:
    async with CopilotClient() as client:
        async with await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model="gpt-4.1",
            streaming=True,
            tools=[get_weather],
        ) as session:
            def handle_event(event) -> None:
                if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
                    sys.stdout.write(event.data.delta_content)
                    sys.stdout.flush()
                if event.type == SessionEventType.SESSION_IDLE:
                    print()

            session.on(handle_event)

            if prompt:
                print(f"User: {prompt}")
                print("Assistant: ", end="", flush=True)
                await session.send_and_wait(prompt)
                print()
                return

            print("Weather Assistant (type 'exit' to quit)")
            print("Try: 'What's the weather in Paris?\n")

            while True:
                try:
                    user_input = input("You: ")
                except EOFError:
                    break

                if user_input.lower() == "exit":
                    break

                print("Assistant: ", end="", flush=True)
                await session.send_and_wait(user_input)
                print()


async def main() -> None:
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        await run_session(prompt)
        return

    await run_session()


if __name__ == "__main__":
    asyncio.run(main())
