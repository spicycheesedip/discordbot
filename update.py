import sys
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
os.system("clear")
print("Run python3 bot.py too so your bot is online, once you update your bot, this script will begin running your bot so also make sure to rerun both update.py and bot.py at the same time after each update.")
bot_script_path = "bot.py"

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print("Detected changes. Restarting bot...")
            os.execv(sys.executable, [sys.executable, bot_script_path])

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()