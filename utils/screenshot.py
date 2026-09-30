from email import message
from watchdog.events import FileSystemEventHandler
import re
import base64
from langchain.messages import HumanMessage
from agent.agent import agent

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
