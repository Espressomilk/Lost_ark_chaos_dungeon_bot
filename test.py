import pyautogui, time, random, cv2, math, keyboard, os, numpy as np
import time
from random import randint
from threading import Thread
from window_capture import WindowCapture
pyautogui.FAILSAFE = False
from config import configure_config

from main import Lost_bot

def run_unit_test():
    global screenshot
    screenshot = cv2.imread("images\\screenshot_test_8.jpg", cv2.IMREAD_UNCHANGED)
    bot = Lost_bot(screenshot)

    my_loc = bot.get_minimap_center()
    boss_loc = bot.find_on_minimap(Lost_bot.minimap_boss_path, 0.65, cv2.TM_CCOEFF_NORMED)
    elite_loc = bot.find_on_minimap(Lost_bot.minimap_elite_path, 0.65, cv2.TM_CCOEFF_NORMED)
    foe_loc = bot.find_on_minimap(Lost_bot.minimap_foe_path, 0.65, cv2.TM_CCOEFF_NORMED)

    if my_loc:
        print("self found.")
        draw_rectangle(my_loc, (255, 0, 0))
    if boss_loc:
        print("boss found. Distance:", bot.calc_distance(my_loc, boss_loc))
        draw_rectangle(boss_loc, (0, 255, 0))
    if elite_loc:
        print("elite found. Distance:", bot.calc_distance(my_loc, elite_loc))
        draw_rectangle(elite_loc, (0, 0, 255))
    if foe_loc:
        print("foe found. Distance", bot.calc_distance(my_loc, foe_loc))
        draw_rectangle(foe_loc, (0, 0, 255))

    print(my_loc, boss_loc, elite_loc)

    my_real_loc = bot.get_center_loc()
    if my_loc and boss_loc:
        boss_real_dir = bot.get_heading_direction(my_loc, boss_loc)
        draw_line(my_real_loc, boss_real_dir)
    if my_loc and elite_loc:
        elite_real_dir = bot.get_heading_direction(my_loc, elite_loc)
        draw_line(my_real_loc, elite_real_dir)

    monster_loc = bot.locate_monster_by_health_bar()
    if monster_loc:
        print("Monster located...")
        draw_rectangle(monster_loc, (255, 0, 0))

    cv2.imshow("Heading!", screenshot)
    cv2.waitKey(0)

def draw_rectangle(loc, color):
    global screenshot
    print(loc)
    start_point = (loc[0] - 10, loc[1] - 10)
    end_point = (loc[0] + 10, loc[1] + 10)
    thickness = 2
    cv2.rectangle(screenshot, start_point, end_point, color, thickness)

def draw_line(start_loc, end_loc):
    cv2.arrowedLine(screenshot, start_loc, end_loc, (255, 0, 0), 2)

if __name__ == '__main__':
    run_unit_test()