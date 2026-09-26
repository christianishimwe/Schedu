from watchdog.events import FileSystemEventHandler
import re
import time
from watchdog.observers import Observer

# create an event hanlder

screenshot_pattern = SCREENSHOT_PATTERN = re.compile(
    r"^Screenshot \d{4}-\d{2}-\d{2} at .+\.png$")
screenshot_path = "/Users/christianishimwe/Desktop"


class ScreenshotHandler(FileSystemEventHandler):
    def on_moved(self, event):
        # macOS writes screenshots to a hidden temp file, then renames it
        # to the final name, so the real filename shows up as a move.
        if event.is_directory:
            return
        moved_file_name = event.dest_path.split("/")[-1]

        if screenshot_pattern.match(moved_file_name):
            print(f"Screenshot detected: {moved_file_name}")


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
