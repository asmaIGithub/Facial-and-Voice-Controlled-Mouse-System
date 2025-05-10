# control_runner.py
import threading
import cv2
from mouse_cursor_control import run_mouse_controller  # <- You'll wrap your loop into this function

RUNNING = False
_thread = None

def start_control():
    global RUNNING, _thread
    if _thread is None or not _thread.is_alive():
        RUNNING = True
        _thread = threading.Thread(target=run_mouse_controller)
        _thread.start()

def stop_control():
    global RUNNING
    RUNNING = False

def is_running():
    return RUNNING
