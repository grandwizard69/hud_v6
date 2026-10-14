"""import sys
import os
import clr
import time

# 1. Setup path and load the DLL safely
dll_directory = r"C:\\D drive\\hi\\LibreHardwareMonitor"  #added the extra backslash to prevent errors. remove if want 2 use
if dll_directory not in sys.path:
    sys.path.append(dll_directory)

clr.AddReference("LibreHardwareMonitorLib")

# 2. Import the root namespace
import LibreHardwareMonitor

def hi():
    computer = LibreHardwareMonitor.Hardware.Computer()
    
    # Only enable the components needed for CPU and Fans
    computer.IsCpuEnabled = True
    computer.IsMotherboardEnabled = True
    computer.IsControllerEnabled = True  # Required for some dedicated fan controllers
    
    computer.Open()
    
    try:
        print("--- Monitoring CPU Temperatures & Fan Speeds (Ctrl+C to exit) ---")
        while True:
            for hardware in computer.Hardware:
                hardware.Update()
                
                # Check sensor categories we care about
                has_printed_hardware_name = False
                
                for sensor in hardware.Sensors:
                    # Filter: Only look for Temperature and Fan sensor types
                    is_temperature = "Temperature" in str(sensor.SensorType)
                    is_fan = "Fan" in str(sensor.SensorType)
                    
                    if (is_temperature or is_fan) and sensor.Value is not None:
                        # Print the hardware header only once when a matching sensor is found
                        if not has_printed_hardware_name:
                            print(f"\n[{hardware.Name}]")
                            has_printed_hardware_name = True
                        
                        unit = "°C" if is_temperature else "RPM"
                        print(f"  -> {sensor.Name}: {sensor.Value:.1f} {unit}")
            
            # Refresh every 2 seconds
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    finally:
        computer.Close()

if __name__ == "__main__":
    hi()
"""

#edit this after to only get cpu avg

import sys
import os
import clr
import time
import math

# 1. Setup path and load the DLL safely
dll_directory = r"C:\D drive\hi\LibreHardwareMonitor"
if dll_directory not in sys.path:
    sys.path.append(dll_directory)

clr.AddReference("LibreHardwareMonitorLib")

# 2. Import the root namespace
import LibreHardwareMonitor  # type: ignore
from LibreHardwareMonitor.Hardware import HardwareType # type: ignore

def hi(instance, stop_event):
    computer = LibreHardwareMonitor.Hardware.Computer()
    computer.IsCpuEnabled = True
    computer.Open()
    
    try:
        #Loop runs ONLY while stop_event is NOT set
        while not stop_event.is_set():
            for hardware in computer.Hardware:
                if hardware.HardwareType == HardwareType.Cpu:
                    hardware.Update()
                    
                    core_temps = []
                    hardware_average = None
                    
                    for sensor in hardware.Sensors:
                        if "Temperature" in str(sensor.SensorType) and sensor.Value is not None:
                            sensor_name = sensor.Name.lower()
                            
                            # Grab native package average
                            if "average" in sensor_name or "package" in sensor_name:
                                hardware_average = sensor.Value
                                break
                            if "core" in sensor_name:
                                core_temps.append(sensor.Value)
                    
                    # Determine the final value
                    if hardware_average is not None:
                        final_temp = hardware_average
                    elif core_temps:
                        final_temp = sum(core_temps) / len(core_temps)
                    else:
                        final_temp = 0.0
                    
                    # Inject the numeric value back into your main class instance
                    instance.cpu_temp = round(final_temp, 1)
            
            #Sleep for 1 second, but wake up instantly if stop_event is triggered
            if stop_event.wait(timeout=1):
                break # Exit loop immediately if event was set
            
    except Exception as e:
        print(f"Thread error: {e}")
    finally:
        computer.Close()

if __name__ == "__main__":
    #hi()
    print(hi())


