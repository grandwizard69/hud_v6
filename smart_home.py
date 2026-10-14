import tinytuya
from ui import jarvis_print
import time

plug = tinytuya.OutletDevice(
    dev_id="ebf1b0ca6bcd9d88b18leo",
    address="10.0.0.26",
    local_key="WvM{FrL|g&1d/MC{"
)

plug.set_version(3.3)

should_run = True

def turn_lights_on():
    global should_run
    if should_run:
        should_run = False
        plug.set_status(True)
        time.sleep(0.5)  # small delay to ensure the command is sent before allowing new commands
        should_run = True
        return "Lights turned on"

def turn_lights_off():
    global should_run
    if should_run:
        should_run = False
        plug.set_status(False)
        time.sleep(0.5)  # small delay to ensure the command is sent before allowing new commands
        should_run = True
        return "Lights turned off"

def get_light_status():
    global should_run
    if should_run:
        should_run = False
        status = plug.status()
        time.sleep(0.5)  # small delay to ensure the command is sent before allowing new commands
        should_run = True

    if status["dps"]["1"]:
        jarvis_print("Lights are on")
    else:
        jarvis_print("Lights are off")