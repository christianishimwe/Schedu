import time
from watchdog.observers import Observer
from utils.screenshot import ScreenshotHandler

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
