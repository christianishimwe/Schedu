from langchain.agents import create_agent
from agent.tools import get_events, add_event
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agent.prompt import system_prompt

load_dotenv()
messages = []

model = ChatOpenAI(
    model="gpt-5.5",
    api_key=os.environ["openai_api_key"],
)
agent = create_agent(
    model=model,
    tools=[get_events, add_event],
    system_prompt=system_prompt
)
