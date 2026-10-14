#hello
import os 
import sys
import math
import time
import psutil
from brain_1 import process_command
from datetime import datetime
import threading
import clr
import libre_hardware_monitor_test 
from PyQt6.QtCore import QRectF


from pynvml import *

from PyQt6.QtWidgets import QApplication, QWidget, QInputDialog
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QFont
)


class hud(QWidget):

    def __init__(self):
        super().__init__()

        #  Ceate a thread safety stop event flag
        self.stop_event = threading.Event()
        self.cpu_temp = 0.0

        # Start the background thread once pasing the stop event
        self.monitor_thread = threading.Thread(
            target=libre_hardware_monitor_test.hi, 
            args=(self, self.stop_event), 
            daemon=True
        )
        self.monitor_thread.start()

        self.completed_objectives = []


        self.last_nav_time = 0
        self.nav_delay = 0.25

        self.menu_rotation = 0
        self.target_rotation = 0

        self.rotation = 0

        # Aspect ratio math to match your carousel text tilt
        self.tilt_factor = 0.30

        self.cpu = 0
        self.cpu_history = []
        self.should_show_cpu = True

        
        self.ram = 0
        self.should_show_ram = True


        self.gpu_load = 0
        self.gpu_temp = 0
        self.should_show_gpu = True
        

        self.vram_used = 0
        self.vram_total = 0
        self.should_show_vram = True


        self.battery = 0
        self.should_show_battery = True


        self.battery_charging = False


        self.should_show_menu = True
        self.should_show_quest = True

        


        self.should_show_grid = True
        self.should_show_scan_lines = True
        self.should_show_rings = True
        self.should_show_orbiting_dots = True
        self.should_show_title = False
        self.should_show_clock = True
        self.should_show_corners = True


        self.current_mode = "default_mode"


        self.menu_history = []




        self.menus = {

            "MAIN": [
                "LIGHTS",
                "SETTINGS",
                "QUESTS",
                "SWITCH_MODES"
            ],

            "LIGHTS": [
                "LIGHTS_ON",
                "LIGHTS_OFF",
                "LIGHT_STATUS",
                "STROBE"
            ],

            "SETTINGS": [
                "DISPLAY",
                "REMEMBER_SELECTED_QUEST" 
            ],

            "DISPLAY": [
                "SYSTEM_INFO",
                "GRAPHICS",
                "OTHER"
                
            ],

            "OTHER": [
                "SHOW/HIDE_QUEST",
                "SHOW/HIDE_MENU",

            ],

            "GRAPHICS": [
                "GRID",
                "SCAN_LINES",
                "RINGS",
                "ORBITING_DOTS",
                "TITLE",
                "CLOCK",
                "CORNERS"
                
            ],

            "SYSTEM_INFO": [
                "SHOW_ALL",
                "HIDE_ALL",
                "SHOW/HIDE_CPU",
                "SHOW/HIDE_RAM",
                "SHOW/HIDE_GPU",
                "SHOW/HIDE_VRAM",
                "SHOW/HIDE_BATTERY"
            ],

            "QUESTS": [
                "TOGGLE_OBJECTIVE",
                "SET_MAIN_QUEST",
                "SET_SIDE_QUEST",
                "CREATE_QUEST",
                "DELETE_QUEST"
            ]
        }

        self.quests_file = os.path.join(
            os.path.dirname(__file__),
            "quests.txt"
        )

        with open(self.quests_file, "r", encoding="utf-8") as handle:
                    lines = [line.strip() for line in handle if line.strip()]
        
        self.should_remember_selected_quest = True if lines[0].startswith("should_remember_selected_quest=True") else False
        print("init: ", self.should_remember_selected_quest)


        self.quests = {}
        self.main_quests = []
        self.side_quests = []
        self.main_quest = ""
        self.side_quest = ""
        self.active_quest = ""
        self.current_quest_view = ""

        self.load_quests()
        self.refresh_quest_menus()

        self.current_menu = "MAIN"
        self.selected = 0

        self.selected = 0

        try:
            nvmlInit()
        except:
            print("NVML unavailable")

        self.setWindowTitle("Sage")

        self.setGeometry(
            100,
            100,
            1400,
            900
        )

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.animate
        )

        self.timer.start(16)

    def animate(self):

        menu_items = self.menus.get(self.current_menu, [])
        count = len(menu_items)

        if count <= 0:
            self.target_rotation = 0
            self.menu_rotation = 0
            self.rotation += 1
            self.update()
            return

        angle_step = 360 / count

        self.target_rotation = (
            -self.selected * angle_step
        )

        raw_difference = (
            self.target_rotation -
            self.menu_rotation
        )

        difference = (
            (raw_difference + 180) % 360
        ) - 180

        self.menu_rotation += difference * 0.5

        if abs(difference) < 0.1:
            self.menu_rotation = self.target_rotation

        self.rotation += 1

        
        if self.should_show_cpu:
            cpu_now = psutil.cpu_percent()

            self.cpu_history.append(cpu_now)

            if len(self.cpu_history) > 30:
                self.cpu_history.pop(0)

            self.cpu = sum(self.cpu_history) / len(
                self.cpu_history
            )


        if self.should_show_ram:
            self.ram = psutil.virtual_memory().percent

        if self.should_show_battery:
            battery = psutil.sensors_battery()

            if battery:

                self.battery = battery.percent

                self.battery_charging = (
                    battery.power_plugged
                )

        
        if self.should_show_gpu:
            try:

                handle = (
                    nvmlDeviceGetHandleByIndex(0)
                )

                util = (
                    nvmlDeviceGetUtilizationRates(
                        handle
                    )
                )

                memory = (
                    nvmlDeviceGetMemoryInfo(
                        handle
                    )
                )

                temp = (
                    nvmlDeviceGetTemperature(
                        handle,
                        NVML_TEMPERATURE_GPU
                    )
                )

                self.gpu_load = util.gpu

                self.gpu_temp = temp

                self.vram_used = (
                    memory.used // 1024**2
                )

                self.vram_total = (
                    memory.total // 1024**2
                )

            except Exception as exc:
                print("fail at getting gpu info. Exceptiin type: ", type(exc), "Exception: ", exc)

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        center_x = self.width() // 2
        center_y = self.height() // 2 if self.current_mode=="default_mode" else self.height() - 180

        cyan = QColor(
            0,
            255,
            255
        )

        raspberry = QColor(
            227,
            11,
            92
        )

        faint = QColor(
            0,
            255,
            255,
            60
        )

        white = QColor(
            255,
            255,
            255
        )

        # ==================
        # GRID
        # ==================
        if self.should_show_grid:
            faint.setAlpha(50)
            painter.setPen(faint)

            for x in range(
                0,
                self.width(),
                50
            ):
                painter.drawLine(
                    x,
                    0,
                    x,
                    self.height()
                )

            for y in range(
                0,
                self.height(),
                50
            ):
                painter.drawLine(
                    0,
                    y,
                    self.width(),
                    y
                )

        # ==================
        # SCANLINES
        # ==================
        if self.should_show_scan_lines:
            for y in range(
                0,
                self.height(),
                5
            ):
                painter.drawLine(
                    0,
                    y,
                    self.width(),
                    y
                )

        # ==================
        # INNER RING
        # ==================

        if self.should_show_rings:
            if self.current_mode == "default_mode":
                painter.save()

                painter.translate(
                    center_x,
                    center_y
                )

                painter.rotate(
                    self.rotation
                )

                painter.setPen(
                    QPen(
                        cyan,
                        3
                    )
                )

                painter.drawEllipse(
                    -300,
                    -300,
                    600,
                    600
                )

                painter.drawEllipse(
                    -240,
                    -240,
                    480,
                    480
                )

                painter.restore()

        # ==================
        # OUTER RING
        # ==================
        if self.should_show_rings:
            if self.current_mode == "default_mode":
                painter.save()

                painter.translate(
                    center_x,
                    center_y
                )

                painter.rotate(
                    -self.rotation * 0.5
                )

                painter.setPen(
                    QPen(
                        faint,
                        2
                    )
                )

                painter.drawEllipse(
                    -350,
                    -350,
                    700,
                    700
                )

                painter.restore()

        # ==================
        # ORBITING DOTS
        # ==================
        if self.should_show_orbiting_dots:
            if self.current_mode == "default_mode":

                for i in range(4):

                    angle = math.radians(
                        self.rotation * 2 +
                        (i * 90)
                    )

                    x = (
                        center_x +
                        math.cos(angle) * 300
                    )

                    y = (
                        center_y +
                        math.sin(angle) * 300
                    )

                    painter.setBrush(cyan)

                    painter.drawEllipse(
                        int(x) - 6,
                        int(y) - 6,
                        12,
                        12
                    )

        

        # ==========================================
        # 3D TILTED RINGS & DOTS (BACKGROUND LAYER)
        # ==========================================
        if self.current_mode == "idk_wat_2_call_it_mode":
            
            if self.should_show_rings:
                painter.save()
                
                # --- INNER RINGS ---
                painter.setPen(QPen(cyan, 0.1))
                
                # Inner Ring 1: Shrunk from 300 to 225 radius (450 width)
                painter.drawEllipse(
                    int(center_x - 225), 
                    int(center_y - (225 * self.tilt_factor)), 
                    450, 
                    int(450 * self.tilt_factor)
                )
                
                # Inner Ring 2: Shrunk from 240 to 180 radius (360 width)
                # Custom offset altered from 120 to 90 to match the 75% downscaling
                painter.drawEllipse(
                    int(center_x - 180), 
                    int(center_y - (90 * self.tilt_factor)), 
                    360, 
                    int(360 * self.tilt_factor)
                )

                # Outer Ring: Shrunk from 350 to 260 radius (520 width)
                painter.setPen(QPen(faint, 2))
                painter.drawEllipse(
                    int(center_x - 260), 
                    int(center_y - (130 * self.tilt_factor)), 
                    520, 
                    int(520 * self.tilt_factor)
                )
                
                painter.restore()


        # ==========================================
        # 3D TILTED ORBITING DOTS
        # ==========================================
            if self.should_show_orbiting_dots:


                count = len(self.menus[self.current_menu])
                if count > 0:
                    dot_angle_step = 360/ count

                    for i in range(count):  #added this so that the count matches the amount of items cuz cool
                        angle = math.radians(self.rotation * 0.5 + (i * dot_angle_step))

                        # TRACK MODIFIED: Radius 180, offset 90 * tilt_factor
                        x = float(center_x + math.sin(angle) * 180)
                        y = float(center_y + (math.cos(angle) * 180 * self.tilt_factor) + (90 * self.tilt_factor))

                        painter.setOpacity(.4)
                        painter.setBrush(cyan)
                        painter.setPen(Qt.PenStyle.NoPen)
                        
                        dot_size = 10.0 # Shrunk slightly from 12 to 10 to match the new size profile
                        dot_rect = QRectF(x - (dot_size / 2.0), y - (dot_size / 2.0), dot_size, dot_size)
                        painter.drawEllipse(dot_rect)

                    for i in range(count):  #second one is for a differenmt ring
                        angle = math.radians(self.rotation * -0.5 + (i * dot_angle_step))


                        x = float(center_x + math.sin(angle) * 260)
                        y = float(center_y + (math.cos(angle) * 260 * self.tilt_factor) + (130 * self.tilt_factor))

                        painter.setOpacity(.4)
                        painter.setBrush(cyan)
                        painter.setPen(Qt.PenStyle.NoPen)
                        
                        dot_size = 10.0 # Shrunk slightly from 12 to 10 to match the new size profile
                        dot_rect = QRectF(x - (dot_size / 2.0), y - (dot_size / 2.0), dot_size, dot_size)
                        painter.drawEllipse(dot_rect)
                    painter.setOpacity(1)


        # ==================
        # TITLE
        # ==================
        painter.setPen(cyan)
        
        painter.setFont(
            QFont(
                "Consolas",
                26
            )
        )

        if self.should_show_title:            

            painter.drawText(
                40,
                50,
                "Sage: Online"
            )

        # ==================
        # CLOCK
        # ==================
        if self.should_show_clock:
            clock = datetime.now().strftime(
                "%I:%M:%S %p"
            )

            painter.drawText(
                self.width() - 255,
                65,
                clock
            )

        # ==================
        # CORNERS
        # ==================
        if self.should_show_corners:
            painter.setPen(
                QPen(
                    cyan,
                    3
                )
            )

            corner = 120

            painter.drawLine(
                20,
                20,
                corner,
                20
            )

            painter.drawLine(
                20,
                20,
                20,
                corner
            )

            painter.drawLine(
                self.width() - 20,
                20,
                self.width() - corner,
                20
            )

            painter.drawLine(
                self.width() - 20,
                20,
                self.width() - 20,
                corner
            )

            painter.drawLine(
                20,
                self.height() - 20,
                corner,
                self.height() - 20
            )

            painter.drawLine(
                20,
                self.height() - 20,
                20,
                self.height() - corner
            )

            painter.drawLine(
                self.width() - 20,
                self.height() - 20,
                self.width() - corner,
                self.height() - 20
            )

            painter.drawLine(
                self.width() - 20,
                self.height() - 20,
                self.width() - 20,
                self.height() - corner
            )


        # ==================
        # LEFT PANEL
        # ==================

        painter.setFont(
            QFont(
                "Consolas",
                14
            )
        )

        y = 65
        painter.setPen(cyan)

        if self.should_show_cpu:
            painter.drawText(
                40,
                y,
                f"CPU: {self.cpu:.1f}%" 
            )
            painter.drawText(
                40,
                y + 30,
                f"CPU TEMP: {self.cpu_temp}°C"
            )

        if self.should_show_ram:
            painter.drawText(
                40,
                y + 60,
                f"RAM: {self.ram}%"
            )

            
        if self.should_show_gpu:
            painter.drawText(
                40,
                y + 90,
                f"GPU: {self.gpu_load}%"
            )

            painter.drawText(
                40,
                y + 120,
                f"GPU TEMP: {self.gpu_temp}C"
            )


        if self.should_show_vram:
            painter.drawText(
                40,
                y + 150,
                f"VRAM: {self.vram_used}/{self.vram_total} MB"
            )

        # ==================
        # RIGHT PANEL
        # ==================


        battery_text = (
            "CHARGING"
            if self.battery_charging
            else "BATTERY"
        )

        x = self.width() - 190

        if self.should_show_battery:   
            painter.drawText(
                x,
                90,
                f"{battery_text}: {self.battery}%"
            )


        # ==================
        # QUEST PANEL
        # ==================

        quest_box_x = 40
        quest_box_y = self.height() - 220
        quest_width = 420
        quest_height = 140

        painter.setPen(cyan)


        painter.setFont(
            QFont(
                "Consolas",
                16,
                QFont.Weight.Black
            )
        )

        if self.should_show_quest:

            painter.drawText(
                quest_box_x + 12,
                quest_box_y + 24,
                "MAIN QUESTS"
            )
            painter.drawText(
                quest_box_x + 260,
                quest_box_y + 24,
                "SIDE QUESTS"
            )

            main_titles = self.main_quests[:6]
            side_titles = self.side_quests[:6]


            for offset, title in enumerate(main_titles):
                is_selected = title == self.main_quest
                painter.setFont(
                    QFont(
                        "Consolas",
                        13,
                        QFont.Weight.Black if is_selected else QFont.Weight.Bold
                    )
                )

                painter.setPen(raspberry)
                marker = ">" if is_selected else "-"
                painter.drawText(
                    quest_box_x + 16,
                    quest_box_y + 48 + offset * 16,
                    marker
                )

                painter.setPen(cyan)
                painter.drawText(
                    quest_box_x + 30,
                    quest_box_y + 48 + offset * 16,
                    title
                )

            for offset, title in enumerate(side_titles):
                is_selected = title == self.side_quest
                painter.setFont(
                    QFont(
                        "Consolas",
                        13,
                        QFont.Weight.Black if is_selected else QFont.Weight.Bold
                    )
                )
                painter.setPen(raspberry)
                marker = ">" if is_selected else "-"
                painter.drawText(
                    quest_box_x + 266,
                    quest_box_y + 48 + offset * 16,
                    marker
                )

                painter.setPen(cyan)
                painter.drawText(
                    quest_box_x + 280,
                    quest_box_y + 48 + offset * 16,
                    title
                )

            obj_box_x = self.width() - 470
            obj_box_y = self.height() - 220
            obj_width = 430
            obj_height = 140

            objectives = self.quests.get(
                self.current_quest_view,
                []
            )

            #adds 22 pixels per line 
            section_shift = 0 if not self.current_quest_view else len(objectives)* 22

            painter.drawText(
                obj_box_x + 12,
                obj_box_y + 24 - section_shift,
                "SELECTED QUEST"
            )

            painter.drawText(
                obj_box_x + 12,
                obj_box_y + 48 - section_shift,
                f"MAIN: {self.main_quest or 'None'}"
            )

            painter.drawText(
                obj_box_x + 12,
                obj_box_y + 66 - section_shift,
                f"SIDE: {self.side_quest or 'None'}"
            )

            painter.drawText(
                obj_box_x + 12,
                obj_box_y + 92 - section_shift,
                f"OBJECTIVES FOR: {self.current_quest_view or 'None'}"
            )

            objective_font = QFont(
                "Consolas",
                13,
                QFont.Weight.Bold
            )
            painter.setFont(objective_font)
            metrics = painter.fontMetrics()
            line_height = metrics.lineSpacing() - 1
            max_width = obj_width - 48


            if not objectives:
                painter.drawText(
                    QRect(
                        obj_box_x + 24,
                        obj_box_y + 108 - section_shift,
                        max_width,
                        line_height * 3
                    ),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                    "N/A"
                )
            else:

                # Initialize current_y outside the loop at the starting position
                current_y = obj_box_y + 104 - section_shift

                for objective in objectives:

                    dash = "- "
                    text = objective
                    
                    # Check membership against your tracking list
                    is_struck_out = objective in self.completed_objectives

                    # Setup dynamic strikeout font configurations
                    current_font = QFont("Consolas", 13, QFont.Weight.Bold)
                    if is_struck_out:
                        current_font.setStrikeOut(True)
                        painter.setFont(current_font)
                        text_color = QColor(0, 150, 150, 150)    # Faded Cyan
                        dash_color = QColor(150, 11, 50, 150)    # Faded Raspberry
                    else:
                        current_font.setStrikeOut(False)
                        painter.setFont(current_font)
                        text_color = cyan
                        dash_color = raspberry

                    # Recalculate font bounding box dimensions
                    metrics = painter.fontMetrics()
                    text_bounds = metrics.boundingRect(
                        QRect(0, 0, max_width, 10000),
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                        text
                    )
                    wrapped_height = text_bounds.height() + 2

                    # Render outputs onto HUD Canvas
                    painter.setPen(dash_color)
                    painter.drawText(
                        QRect(int(obj_box_x + 16), int(current_y), int(max_width), int(wrapped_height)),
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                        dash
                    )

                    painter.setPen(text_color)
                    painter.drawText(
                        QRect(int(obj_box_x + 30), int(current_y), int(max_width), int(wrapped_height)),
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                        text
                    )
                    
                    item_spacing = 4 
                    current_y += wrapped_height + item_spacing



# ==================
# MENU BOX
# ==================

        painter.setPen(
            QColor(
                0,
                255,
                255,
                180
            )
        )

        painter.setFont(
            QFont(
                "Consolas",
                14
            )
        )

        menu_title = self.current_menu
        if self.current_menu == "QUEST_MAIN":
            menu_title = "SELECT MAIN QUEST"
        elif self.current_menu == "QUEST_SIDE":
            menu_title = "SELECT SIDE QUEST"


        # ==================
        # HOLOGRAPHIC CAROUSEL MENU
        # ==================
        if self.should_show_menu:
            menu_items = self.menus[self.current_menu]

            count = len(menu_items)

            radius = 260 if self.current_mode == "default_mode" else 195

            for i, item in enumerate(menu_items):

                angle_step = 360 / count

                angle = i * angle_step + self.menu_rotation
                

                rad = math.radians(angle)

                x = center_x + math.sin(rad) * radius

                y = center_y + math.cos(rad) * radius * self.tilt_factor

                # -----------------------
                # DEPTH CALCULATION
                # -----------------------

                depth = (math.cos(rad) + 1) / 2

                font_size = int(
                    12 + depth * 18
                )

                alpha = int(
                    50 + depth * 205
                )

                # -----------------------
                # SELECTED ITEM
                # -----------------------
                """painter.save()
                    
                # Match the text alpha transparency for a seamless 3D illusion
                dot_color = QColor(raspberry)
                dot_color.setAlpha(alpha) 
                painter.setBrush(dot_color)
                painter.setPen(Qt.PenStyle.NoPen)

                # Offset the dot vertically so it sits cleanly below the text baseline
                # Scaling the offset by depth ensures it shrinks when far away
                vertical_offset = int(25 * depth) if depth > 0.5 else 15
                dot_size = int(6 + depth * 6) # Dot scales from 6px to 12px

                painter.drawEllipse(
                    int(x) - (dot_size // 2),
                    int(y) + vertical_offset - (dot_size // 2),
                    dot_size,
                    dot_size
                )
                painter.restore()
    """
                if depth > 0.95:

                    painter.setPen(
                        QColor(
                            0 if self.current_mode == "default_mode" else 255,
                            255,
                            255,
                            255
                        )
                    )

                    painter.setFont(
                        QFont(
                            "Playfair Display",
                            font_size,
                            QFont.Weight.Bold
                        )
                    )

                    text = f"< {item} >"

                    if self.current_menu in ("QUEST_MAIN", "QUEST_SIDE"):
                        if self.current_menu == "QUEST_MAIN":
                            selected_label = self.main_quest
                        else:
                            selected_label = self.side_quest

                        if item == selected_label:
                            text = f"> {item} <"

                else:

                    painter.setPen(
                        QColor(
                            0 if self.current_mode == "default_mode" else 255,
                            255,
                            255,
                            alpha
                        )
                    )

                    painter.setFont(
                        QFont(
                            "Playfair Display",
                            font_size
                        )
                    )

                    text = item

                width = len(text) * font_size * 0.40

                painter.drawText(
                    int(x - width),
                    int(y),
                    text
                )



    def next_super_cool_totally_awsome_mode(self):
            self.modes = [
                "default_mode",
                "idk_wat_2_call_it_mode",
                "min"
            ]
    
            self.mode_code = [
                "self.should_show_grid = True;  self.should_show_scan_lines = True;self.should_show_rings = True;self.should_show_orbiting_dots = True;self.should_show_title = False;self.should_show_clock = True;self.should_show_corners = True; self.should_show_quest = True; self.should_show_menu = True; self.show_hide('show_all')",
    
                "self.should_show_grid = False;  self.should_show_scan_lines = False;self.should_show_rings = True;self.should_show_orbiting_dots = True;self.should_show_title = False;self.should_show_clock = True;self.should_show_corners = False; self.should_show_quest = True; self.should_show_menu = True; self.show_hide('show_all')",

                "self.should_show_grid = False;  self.should_show_scan_lines = False;self.should_show_rings = False;self.should_show_orbiting_dots = False;self.should_show_title = False;self.should_show_clock = True;self.should_show_corners = False; self.should_show_quest = False; self.should_show_menu = True; self.show_hide('hide_all')"  
            ]
    
    
            self.current_index = self.modes.index(self.current_mode)
    
            self.next_mode_index = self.current_index + 1 if self.current_index + 1 < len(self.modes) else 0
    
            self.current_mode = self.modes[self.next_mode_index]
            self.current_index = self.next_mode_index
    
            exec(self.mode_code[self.current_index])
            print(self.current_mode, self.current_index)
    

        
    def keyPressEvent(self, event):

        if self.carousel_busy():
            return

        now = time.time()

        if event.key() in (
            Qt.Key.Key_Left,
            Qt.Key.Key_Right
        ):

            if now - self.last_nav_time < self.nav_delay:
                return

        if event.key() == Qt.Key.Key_Right:

            self.next_item()
            self.last_nav_time = now

        elif event.key() == Qt.Key.Key_Left:

            self.previous_item()
            self.last_nav_time = now

        elif event.key() == Qt.Key.Key_Down:

            self.select_item()

        elif event.key() == Qt.Key.Key_Up:

            self.go_back()

        elif event.key() == Qt.Key.Key_Q:

            # Tell the background thread loop to stop running
            self.stop_event.set()
            
            # Wait up to 1.5 seconds for the thread loop to finish its current sleep cycle
            if hasattr(self, 'monitor_thread'):
                self.monitor_thread.join(timeout=1.5)
                
            # Safely close your main program/window
            sys.exit(0) 
            self.close()
        
        elif event.key() == Qt.Key.Key_M:
            self.next_super_cool_totally_awsome_mode()


    # ==================
        # NAVIGATION
    # ==================

    def next_item(self):

        items = self.menus.get(self.current_menu, [])
        if not items:
            self.selected = 0
            return

        self.selected = (
            self.selected + 1
        ) % len(items)

    def previous_item(self):

        items = self.menus.get(self.current_menu, [])
        if not items:
            self.selected = 0
            return

        self.selected = (
            self.selected - 1
        ) % len(items)

    def get_selected(self):

        items = self.menus.get(self.current_menu, [])
        if not items:
            return ""

        return items[self.selected]
    
    def select_item(self):

        item = self.get_selected()

        if not item:
            self.current_menu = "MAIN"
            self.selected = 0
            self.menu_rotation = 0
            self.target_rotation = 0
            return

        if item in self.menus:

            self.menu_history.append(self.current_menu)

            self.current_menu = item
            self.selected = 0

            # Reset carousel position
            self.menu_rotation = 0
            self.target_rotation = 0

            return

        if item == "SET_MAIN_QUEST":
            self.refresh_quest_menus()
            self.current_menu = "QUEST_MAIN"
            self.selected = 0
            self.menu_rotation = 0
            self.target_rotation = 0
            return

        if item == "SET_SIDE_QUEST":
            self.refresh_quest_menus()
            self.current_menu = "QUEST_SIDE"
            self.selected = 0
            self.menu_rotation = 0
            self.target_rotation = 0
            return

        if item == "CREATE_QUEST":
            self.create_quest()
            self.current_menu = "MAIN"
            self.selected = 0
            self.menu_rotation = 0
            self.target_rotation = 0
            return

        if item == "DELETE_QUEST":
            self.refresh_quest_menus()
            self.current_menu = "QUEST_DELETE"
            self.selected = 0
            self.menu_rotation = 0
            self.target_rotation = 0
            return

        if item == "TOGGLE_OBJECTIVE":
            self.current_menu = "OBJECTIVE_SELECT"
            self.menus["OBJECTIVE_SELECT"] = list(self.quests.get(self.current_quest_view, []))
            self.selected = 0
            self.menu_rotation = 0
            self.target_rotation = 0
            return
        
        elif self.current_menu == "OBJECTIVE_SELECT":
            objective = self.quests[self.current_quest_view][self.selected]
            # --- TOGGLE COMPLETION FROM THE COMPLETED LIST ---
            if objective in self.completed_objectives:
                self.completed_objectives.remove(objective) # Unstrike if clicked again
                print(f"Active: {objective}")
            else:
                self.completed_objectives.append(objective) # Strike out
                print(f"Struck Out: {objective}")

            self.save_quests()
            self.current_menu = "MAIN"
            self.selected = 0
            return

        if self.current_menu in ("QUEST_MAIN", "QUEST_SIDE"):
            if self.current_menu == "QUEST_MAIN":
                if item not in self.main_quests:
                    self.main_quests.append(item)
                self.main_quest = item
                self.current_quest_view = item
                self.active_quest = item
            else:
                if item not in self.side_quests:
                    self.side_quests.append(item)
                self.side_quest = item
                self.current_quest_view = item
                self.active_quest = item
            self.save_quests()
            self.current_menu = "MAIN"
            self.selected = 0
            self.menu_rotation = 0
            self.target_rotation = 0
            return

        if self.current_menu == "QUEST_DELETE":

            del self.quests[item]

            if item in self.main_quests:
                self.main_quests.remove(item)

            if item in self.side_quests:
                self.side_quests.remove(item)

            if self.main_quest == item:
                self.main_quest = ""

            if self.side_quest == item:
                self.side_quest = ""

            if self.current_quest_view == item:
                self.current_quest_view = ""

            self.refresh_quest_menus()
            self.save_quests()

            self.current_menu = "QUESTS"
            self.selected = 0
            self.menu_rotation = 0
            self.target_rotation = 0
            return

        print("EXECUTE:", item)

        self.current_menu = "MAIN"
        self.selected = 0

        self.menu_rotation = 0
        self.target_rotation = 0

        #start thread for function
        hi = threading.Thread(target=process_command, args=(item,self), daemon=True)
        hi.start()

    def go_back(self):

        if self.menu_history:

            self.current_menu = self.menu_history.pop()

        else:

            self.current_menu = "MAIN"

        self.selected = 0
        self.menu_rotation = 0
        self.target_rotation = 0

    """
        if self.current_menu in ("QUEST_MAIN", "QUEST_SIDE"):
            self.current_menu = "QUESTS"
            self.selected = 0
            self.menu_rotation = 0
            self.target_rotation = 0
        elif self.current_menu != "MAIN":

            self.current_menu = "MAIN"
            self.selected = 0

            self.menu_rotation = 0
            self.target_rotation = 0
            
"""

        

    def load_quests(self):
        '''
        default_quests = {
            "Find the lost key": [
                "Search the study",
                "Unlock the drawer",
                "Return the key to the vault"
            ],
            "Repair the bridge": [
                "Gather wood",
                "Reinforce the supports",
                "Test the bridge"
            ]
        }

        if not os.path.exists(self.quests_file):
            self.quests = default_quests
            self.main_quests = ["Find the lost key"]
            self.side_quests = ["Repair the bridge"]
            self.main_quest = self.main_quests[0]
            self.side_quest = self.side_quests[0]
            self.active_quest = self.main_quest
            self.current_quest_view = self.main_quest
            self.save_quests()
            return'''    #used for testing

        try:
            with open(self.quests_file, "r", encoding="utf-8") as handle:
                lines = [line.strip() for line in handle if line.strip()]

            loaded_quests = {}
            self.main_quests = []
            self.side_quests = []
            self.main_quest = ""
            self.side_quest = ""
            self.current_quest_view = ""

            for line in lines:
                if line.startswith("main_quests="):
                    self.main_quests = [item.strip() for item in line.split("=", 1)[1].split(",") if item.strip()]
                elif line.startswith("side_quests="):
                    self.side_quests = [item.strip() for item in line.split("=", 1)[1].split(",") if item.strip()]
                elif line.startswith("selected_quest"):
                    self.current_quest_view = line.split("=", 1)[1].strip() if self.should_remember_selected_quest == True else ""
                elif line.startswith("main_quest="):
                    legacy_value = line.split("=", 1)[1].strip()
                    if legacy_value:
                        self.main_quests = [legacy_value]
                elif line.startswith("side_quest="):
                    legacy_value = line.split("=", 1)[1].strip()
                    if legacy_value:
                        self.side_quests = [legacy_value]
                elif line.startswith("quest:"):
                    parts = line[len("quest:"):].split("|")
                    if parts:
                        title = parts[0]
                        objectives = [part for part in parts[1:] if part]
                        loaded_quests[title] = objectives
                if line.startswith("COMPLETED_OBJ:"):
                    self.completed_objectives.append(line.replace("COMPLETED_OBJ:", ""))
                    continue


            if loaded_quests:
                self.quests = loaded_quests

            if not self.quests:
                self.quests = {}


            '''if self.main_quest and self.main_quest not in self.main_quests:
                self.main_quest = ""
            if self.side_quest and self.side_quest not in self.side_quests:
                self.side_quest = ""
            if self.current_quest_view and self.current_quest_view not in self.quests:
                self.current_quest_view = ""

            self.active_quest = self.current_quest_view'''
            self.save_quests()

        except Exception as exc:
            print(f"Unable to read quest file: {exc}")

    def save_quests(self):
        print("save_quest: ", self.should_remember_selected_quest)
        lines = [
            f"should_remember_selected_quest={True if self.should_remember_selected_quest else False}",
            f"main_quests={','.join(self.main_quests)}",
            f"side_quests={','.join(self.side_quests)}",
            f"selected_quest={self.current_quest_view}" if self.should_remember_selected_quest else "selected_quest="
        ]

        for title in sorted(self.quests.keys()):
            objectives = self.quests[title]
            lines.append("quest:" + "|".join([title] + objectives))

        with open(self.quests_file, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))

            for comp_obj in self.completed_objectives:
                handle.write(f"COMPLETED_OBJ:{comp_obj}\n")

    def refresh_quest_menus(self):
        self.menus["QUEST_MAIN"] = list(self.main_quests)
        self.menus["QUEST_SIDE"] = list(self.side_quests)
        self.menus["QUEST_DELETE"] = list(self.quests.keys())
        self.menus["OBJECTIVE_SELECT"] = list(self.quests.get(self.current_quest_view, []))

    def create_quest(self):
        title, ok = QInputDialog.getText(
            self,
            "Create Quest",
            "Quest title:"
        )

        if not ok:
            return

        title = title.strip()
        if not title:
            title = "New quest"

        objectives_text, ok = QInputDialog.getText(
            self,
            "Create Quest",
            "Objectives (comma separated):"
        )

        if not ok:
            objectives_text = ""

        objectives = [
            objective.strip()
            for objective in objectives_text.split(",")
            if objective.strip()
        ]

        if not objectives:
            objectives = ["Complete the quest"]

        quest_type, ok = QInputDialog.getItem(
            self,
            "Create Quest",
            "Quest type:",
            ["Main Quest", "Side Quest"],
            0,
            False
        )

        if not ok:
            quest_type = "Main Quest"

        self.quests[title] = objectives
        self.current_quest_view = title
        self.active_quest = title

        if quest_type == "Main Quest":
            if title not in self.main_quests:
                self.main_quests.append(title)
            self.main_quest = title
        else:
            if title not in self.side_quests:
                self.side_quests.append(title)
            self.side_quest = title

        self.refresh_quest_menus()
        self.save_quests()
        print(f"Quest created: {title} as {quest_type}")

    def carousel_busy(self):
        return abs(
            self.target_rotation -
            self.menu_rotation
        ) > 5


    
    # ==================
        #DISPLAY SETTINGS
    # ==================

    def show_hide(self, input):

        print(input, "show_hide")
        #print(input == "show all")
        hi = [i.removeprefix("SHOW/HIDE_").strip().lower()  for i in self.menus["SYSTEM_INFO"] if i not in ("SHOW_ALL", "HIDE_ALL", "")] # this gets all the menu options so that it wont need to be hard coded and can be scaled without having to add more


        if input == "hide_all":
            for i in hi: exec("self.should_show_" + i + " = False")

        elif input == "show_all":
            for i in hi: exec("self.should_show_" + i + " = True")

        
        else:   exec("self.should_show_" + input + " = False if self.should_show_" + input + "== True else True") # makes it so i dont have to do all the damn if statements


        return






def choose_screen():
    screens = app.screens()

    for i in range(len(screens)):
        print(screens[i].name() + "  " , i)
    
    
    screen_choice = input("\nEnter screen index plz: ")  #if commented out, put static option (this is for when im coding it and dont feel like doing the input  EVERY. SINGLE. TIME  cuz it anoyying)

    if screen_choice == "": # this makes it so i dont have to comment and uncomment the line everytime and will just use the static option if nothing is entered
        screen_choice = "1" #this is to make a static option for when im coding and blah whatever


    if screen_choice in [str(i) for i in range(len(screens))]: # makes sure screen_choice is an actual index and not a random thing cuz someone was stupid and put something wrong. IMPORTANT ALSO i have str(i) because screen_choice is a string and string 0 wont == an int 0 LEAVE IT AS str(i) check comment on geometry below for explanation cuz i aint typing that again

        geometry = screens[int(screen_choice)].geometry()  #i am making it an int now so that if the user is dumb enough to enter a string (which he defenetily is) it will not crash and instead get redone because of the if statement insead of crashing because you cant do int(input("blah")) and enter a string cuz it will crash 

        hud.setGeometry(geometry)
        return hud
    
    elif screen_choice == "q":
        return

    else:
        print("\nyou have to choose an index thats in the list dumbass now try again")
        return choose_screen() #call function again to redo until user stops being dumb and puts the correct thing      ps. never thought i would resort to recursion though this isn't really recursion but it still calls itself just doesn't lessen the problem like recursion does


# Create QApplication if it doesn't exist (for importing hud instance)
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Create hud instance at module level so it can be imported
hud = hud()

if __name__ == "__main__":

    protocal_three_protect_the_pilot = choose_screen()
    protocal_three_protect_the_pilot.showFullScreen()

    sys.exit(app.exec())