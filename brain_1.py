from smart_home import turn_lights_off, turn_lights_on, get_light_status # for lights
import time
import sys

    

def process_command(command, hud_instance):

    command = command.lower().strip()
    print(command, " proccess command")

    # ==================
        # LIGHTS
    # ==================

    if "lights_off" in command:
        print("1")
        turn_lights_off()
        return

    elif "lights_on" in command:
        turn_lights_on()
        return

    elif "lights_status" in command or "light_status" in command:
        status = get_light_status()
        return status
    """elif command in ["strobe", "strobe lights"]:
        for i in range(100):
            turn_lights_on()
            time.sleep(0.01)
            turn_lights_off()
            time.sleep(0.01)
        return
"""


    # ==================
        # QUEST SETTINGS
    # ==================

    if command == "remember_selected_quest":
        hud_instance.should_remember_selected_quest = False if hud_instance.should_remember_selected_quest else True
        return


    # ==================
        # MODE SWITCHING
    # ==================

    if command == "switch_modes":
        hud_instance.next_super_cool_totally_awsome_mode()
        return




    # ==================
        # DISPLAY SETTINGS
    # ==================
    

    if command == "show_all":
        hud_instance.show_hide(command)

    elif command == "hide_all":
        hud_instance.show_hide(command)

    else:
        hud_instance.show_hide(command.removeprefix("show/hide_").strip())





    
        
