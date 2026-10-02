# we will create an agent whose role is basically to analyze an image
# and determine a list of events that needs to be added to the calenda
# and when they need to be added
# this agent will give this our as an output in a structured format and this
# format will be used by a diffente agent in the graph to add these to the calendar
from watchdog.observers import Observer
import time
from langchain.messages import HumanMessage
import base64
import re
from watchdog.events import FileSystemEventHandler
from email import message
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from agent.models import CalendarEvent
load_dotenv()


agent = create_agent(
    model=ChatOpenAI(
        model="gpt-5.5",
        api_key=os.environ["openai_api_key"],
    ),
    tools=[CalendarEvent],
    system_prompt=f"""
    Your name is Schedu. You are an AI agent that analyzes images and extracts events that need to be added to a calendar.
    You should ouptput the list of events in a strucutred format that can be used by another agent to add these events to a calendar.
    """
)


# create an event hanlder

screenshot_pattern = SCREENSHOT_PATTERN = re.compile(
    r"^Screenshot \d{4}-\d{2}-\d{2} at .+\.png$")


class ScreenshotHandler(FileSystemEventHandler):
    def on_moved(self, event):
        # macOS writes screenshots to a hidden temp file, then renames it
        # to the final name, so the real filename shows up as a move.
        if event.is_directory:
            return
        moved_file_name = event.dest_path.split("/")[-1]

        if screenshot_pattern.match(moved_file_name):
            print(event.dest_path)
            print(f"\nScreenshot detected: {moved_file_name}")
            # TO DO
            # here exract data from the screeenshot and git it to the agent
            image_prompt = self.extract_screenshot_data(event.dest_path)
            agent_response = agent.invoke({"messages": [image_prompt]})
            print(agent_response["messages"][-1].content)

    def extract_screenshot_data(self, filepath: str):
        with open(filepath, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

            message = HumanMessage(
                content=[
                    {
                        "type": "image",
                        "base64": image_data,
                        "mime_type": "image/png"
                    }
                ]
            )
            return message


screenshot_path = "/Users/christianishimwe/Desktop"


def main():
    # create an observer
    screenshot_observer = Observer()
    handler = ScreenshotHandler()
    screenshot_observer.schedule(handler, screenshot_path, recursive=False)
    screenshot_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        screenshot_observer.stop()
    screenshot_observer.join()


if __name__ == "__main__":
    main()
