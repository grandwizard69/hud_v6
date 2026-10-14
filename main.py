import keyboard
from ui import jarvis_print
from smart_home import turn_lights_off, turn_lights_on, get_light_status
from brain_1 import process_command
import threading
from STT import voice_loop, quit_STT
import time
kill_switch = "ctrl+shift+alt"
global should_run
should_run = True


def main():
    global should_run
    jarvis_print("Online")
    voice_thread = None

    while should_run:
        if keyboard.is_pressed(kill_switch):
            jarvis_print("Kill switch activated. Shutting down.")
            quit_all()
            break



        """# Start a new voice thread only if there isn't one running
        if voice_thread is None or not voice_thread.is_alive():
            voice_thread = threading.Thread(target=voice_loop, daemon=True)
            voice_thread.start()

        # avoid busy-looping
        time.sleep(0.1)

    # ensure voice thread finishes before exiting
    if voice_thread is not None and voice_thread.is_alive():
        voice_thread.join(timeout=2)"""

        user_input = input(">>> ").strip()
        
        if user_input.lower() in ["exit", "quit"]:
            jarvis_print("Shutting down.")
            break
        elif user_input.lower() == "": # incase missinput/wrong whatever blah blah we can skip processing
            continue
        else:
            process_command(user_input)


def quit():
    global should_run
    jarvis_print("Shutting down.")
    should_run = False

def quit_all():
    quit()
    quit_STT()

def get_shouldrun():
    return should_run



if __name__ == "__main__":
    main()