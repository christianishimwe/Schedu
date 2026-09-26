from langchain.agents import create_agent
from calendar_tools import get_events, add_event
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
messages = []

model = ChatOpenAI(
    model="gpt-5.5",
    api_key=os.environ["openai_api_key"],
)
agent = create_agent(
    model=model,
    tools=[get_events, add_event],
    system_prompt=f"""
    You are Schede, an AI calendar agent whose task is to check events on the calendar
    the current time is {datetime.now()} and the current date is {datetime.now().date()} and the current timezone is {datetime.now().astimezone().tzinfo}
"""
)
while True:
    user_input = input("Ask Schedu a question about your calendar: ")
    messages.append({"role": "user", "content": user_input})
    response = agent.invoke({
        "messages": messages
    })
    print(response["messages"][-1].content)
