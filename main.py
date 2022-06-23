import pyautogui, time, random, cv2, math, keyboard, os, numpy as np
import time
from random import randint
from threading import Thread
from window_capture import WindowCapture
pyautogui.FAILSAFE = False
from config import configure_config

class Lost_bot():

    # Static propeties
    # wincapture = WindowCapture("LOST ARK (64-bit, DX11) v.2.3.4.1")
    # translate_pos = wincapture.get_screen_position
    # global screenshot
    # screenshot = wincapture.get_screenshot()
    # window_size = (wincapture.w, wincapture.h)
    # print(type(screenshot))
    # print((screenshot.shape))

    wincapture = WindowCapture("TEST", True)

    IN_CITY = True
    MOVE = False
    CAST = False
    BOT_WORKING = False
    SHOULD_EXIT = False
    TIMEOUT = 600  # seconds.
    available_spells = []
    method = cv2.TM_CCORR_NORMED

    resurection_path = "images\\base_res.png"
    in_game_icon_path = "images\\in_game_icon.jpg"
    portal_path = "images\\portal.jpg"
    minimap_boss_path = "images\\minimap_boss.jpg"
    minimap_elite_path = "images\\minimap_elite.jpg"
    minimap_portal_path = "images\\minimap_portal.jpg"
    minimap_self_east_path = "images\\minimap_self_east.jpg"
    minimap_self_north_path = "images\\minimap_self_north.jpg"

    not_in_game_count = 0

    text_file = open("config.txt", "r")
    lines = text_file.read().split('\n')
    for row in lines:
        if "spells" in row:
            all_spells = row.replace("spells =","").replace(" ","")
        elif "spell/time" in row:
            duration = row[15:].split(" ")

    def waitRandomizedTime(self, min, max):
        time.sleep(random.uniform(min, max))

    def check_available_spell(self, all_spells):
        self.available_spells = []
        for spell in all_spells:
            path = ("images\\" + str(spell) + ".png")
            result = self.find_pos(path, 0.98, cv2.TM_CCORR_NORMED)
            if result:
                self.available_spells.append(spell)
        print("available spells: ", self.available_spells)
        return self.available_spells

    def show_minimap(self):
        minimap = self.get_minimap()
        cv2.imshow('minimap', minimap)
        cv2.waitKey(0)

    def get_minimap_offset(self):
        return [[66, 308], [1602, 1883]]

    def get_minimap_center(self):
        return (1742, 162)

    def get_minimap(self):
        offset = self.get_minimap_offset()
        return screenshot[offset[0][0]:offset[0][1], offset[1][0]:offset[1][1]]

    def find_on_minimap(self, target_path, threshold, method):
        target = cv2.imread(target_path, cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(self.get_minimap(), target, method)
        _, maxVal, _, maxLoc = cv2.minMaxLoc(result)
        print(maxVal, target_path, maxLoc)
        print(type(maxLoc))
        absoluteLoc = (maxLoc[0] + self.get_minimap_offset()[1][0] + target.shape[0] // 2, 
                       maxLoc[1] + self.get_minimap_offset()[0][0] + target.shape[1] // 2)
        if maxVal > threshold:
            return self.wincapture.get_screen_position(absoluteLoc)
        else:
            return None

    def find_pos(self, target_path, threshold, method):
        target = cv2.imread(target_path, cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(screenshot, target, method)
        _, maxVal, _, maxLoc = cv2.minMaxLoc(result)
        print(maxVal, target_path)
        if maxVal > threshold:
            return self.wincapture.get_screen_position(maxLoc)
        else:
            return None

    def get_heading_direction(self, my_loc, target_loc, multifier=2):
        my_real_loc = self.get_center_loc()
        return (my_real_loc[0] + (target_loc[0] - my_loc[0]) * multifier,
                my_real_loc[1] + (target_loc[1] - my_loc[1]) * multifier)

    def scan_for_portal(self):
        while not self.IN_CITY:
            pos = self.find_pos(self.portal_path, 0.90, cv2.TM_CCORR_NORMED)
            if pos:
                print("Portal appeared!")
                self.SHOULD_EXIT = True
                break

    def pos_dirs(self, index):
        x = [959, 960, 1034, 1049, 1024, 953, 886, 862, 884]
        y = [528, 419, 469, 516, 585, 581, 561, 512, 444]
        return self.wincapture.get_screen_position((x[index], y[index]))

    def get_center_loc(self):
        return (959, 528)

    def cast_spell(self, spells):
        hold_time = 0.2
        print(self.available_spells)
        if self.available_spells == []:
            self.available_spells = self.check_available_spell(spells)
            for _ in range(0,randint(5,8)):
                pyautogui.click()
                self.waitRandomizedTime(0.2,0.3)
        else: 
            cast = self.available_spells[randint(0,len(self.available_spells)-1)]
        
            random_pos = self.pos_dirs(randint(0, 8))
            pyautogui.moveTo(random_pos[0] + randint(-5, 5), random_pos[1] + randint(-5, 5))

            pyautogui.keyDown(cast)
            self.waitRandomizedTime(hold_time*0.8,hold_time)
            pyautogui.keyUp(cast)
            # Double click.
            pyautogui.keyDown(cast)
            self.waitRandomizedTime(hold_time*0.8,hold_time)
            pyautogui.keyUp(cast)
            self.available_spells.remove(cast)
            if cast == 'r' or cast == 'f':
                self.waitRandomizedTime(1.3, 1.5)
            else:
                self.waitRandomizedTime(0.2,1)

    def check_resurection(self):
        x = self.find_pos(self.resurection_path, 0.98, cv2.TM_CCORR_NORMED)
        if x:
            pyautogui.moveTo(x[0] + randint(5,25), x[1 + randint(5, 10)], random.uniform(0.2, 0.8))
            pyautogui.click()

    def is_in_game(self):
        icon = self.find_pos(self.in_game_icon_path, 0.99, cv2.TM_CCORR_NORMED)
        return icon

    def check_accept(self):
        accept_pos = self.accept_range()  
        pyautogui.moveTo(accept_pos[0], accept_pos[1], random.uniform(0.1, 0.5))
        pyautogui.click()

    def check_ok(self):
        ok_pos = self.ok_range()
        pyautogui.moveTo(ok_pos[0], ok_pos[1], random.uniform(0.1, 0.5))
        pyautogui.click()

    def ok_range(self):
        loc = [randint(865, 949), randint(596, 612)]
        return self.wincapture.get_screen_position(loc)

    def shortcut_range(self):
        loc = [869 + randint(-40 , 40), 307 + randint(-10, 10)]
        return self.wincapture.get_screen_position(loc)

    def solo_range(self):
        loc = [randint(1391, 1650), randint(842, 877)]
        return self.wincapture.get_screen_position(loc)

    def accept_range(self):
        loc = [randint(866, 956), randint(598, 627)]
        return self.wincapture.get_screen_position(loc)

    def exit_range(self):
        loc = [randint(81, 189), randint(289, 319)]
        return self.wincapture.get_screen_position(loc)

    def repair_icon_range(self):
        loc = [randint(1240, 1252), randint(691, 707)]
        return self.wincapture.get_screen_position(loc)

    def repair_equiped_gear_range(self):
        loc = [randint(1015, 1155), randint(434, 452)]
        return self.wincapture.get_screen_position(loc)

    def moveToClick(self, loc):
        pyautogui.moveTo(loc[0], loc[1], random.uniform(0.1, 0.5))
        pyautogui.click()

    def repair_items(self):
        self.wincapture.focus_window()
        pyautogui.hotkey('alt', 'p')
        self.waitRandomizedTime(1, 2)
        self.moveToClick(self.repair_icon_range())
        self.waitRandomizedTime(1, 2)
        self.moveToClick(self.repair_equiped_gear_range())
        self.waitRandomizedTime(1, 2)
        pyautogui.press("esc")
        self.waitRandomizedTime(1, 2)
        pyautogui.press("esc")

    def alt_q_chaos(self):
        self.wincapture.focus_window()
        pyautogui.hotkey('alt', 'q')
        self.waitRandomizedTime(1, 2)
        self.moveToClick(self.shortcut_range())
        self.waitRandomizedTime(1, 2)
        self.moveToClick(self.solo_range())

        self.check_accept()
        self.IN_CITY = False
        self.SHOULD_EXIT = False

    def exit_chaos(self):
        self.moveToClick(self.exit_range())
        self.waitRandomizedTime(0.5, 0.8)
        self.check_ok()
        self.IN_CITY = True
        self.waitRandomizedTime(10, 12)

    ## do chaos dungeon after finding one
    def do_chaos(self):
        start_time = time.time()
        while not self.IN_CITY and time.time() - start_time < self.TIMEOUT:
            if not self.MOVE:
                self.MOVE = True
                start_scan = Thread(target = self.scan_for_portal)
                start_scan.start()
            if self.is_in_game():
                self.check_resurection()
                self.cast_spell(self.all_spells)
            else:
                self.not_in_game_count += 1
                print("Not in game! Perhaps loading..." + str(self.not_in_game_count))
            if self.SHOULD_EXIT:
                self.exit_chaos()
            

def capture_screen():
    while True:
        global screenshot
        screenshot = Lost_bot.wincapture.get_screenshot()
        time.sleep(0.5)

def kill_bot():
    Thread(target = capture_screen, args = ()).start()
    while True:
        if keyboard.is_pressed("del"):
            os._exit(1)
        time.sleep(1)


def run_bot():
    # configure = input("Do you want configure bot? Y/N\n").lower()
    # if configure == "y":
    #     configure_config()
    total_time = int(input("How long do you want to run? (minutes)"))
    start_time = time.time()
    Esc = True
    count = 10
    while True and (time.time() - start_time) / 60 < total_time:
        bot = Lost_bot()
        if Esc:
            Thread(target = kill_bot, args = ()).start()
            Esc = False
        if count >= 10:
            count = 0
            bot.repair_items()
        bot.waitRandomizedTime(1, 2)
        bot.alt_q_chaos()
        bot.waitRandomizedTime(5, 8)
        bot.do_chaos()
        count += 1

def draw_rectangle(loc, color):
    print(loc)
    start_point = (loc[0] - 10, loc[1] - 10)
    end_point = (loc[0] + 10, loc[1] + 10)
    thickness = 2
    cv2.rectangle(screenshot, start_point, end_point, color, thickness)

def draw_line(start_loc, end_loc):
    cv2.line(screenshot, start_loc, end_loc, (255, 0, 0), 2)

def run_unit_test():
    bot = Lost_bot()
    global screenshot
    screenshot = cv2.imread("images\\screenshot_test_2.jpg", cv2.IMREAD_UNCHANGED)
    # find_on_minimap_test(bot, Lost_bot.minimap_boss_path)
    # find_on_minimap_test(bot, Lost_bot.minimap_elite_path)
    # find_on_minimap_test(bot, Lost_bot.minimap_self_east_path)

    # my_loc = bot.find_on_minimap(Lost_bot.minimap_self_north_path, 0.92, cv2.TM_CCORR_NORMED)
    my_loc = bot.get_minimap_center()
    boss_loc = bot.find_on_minimap(Lost_bot.minimap_boss_path, 0.95, cv2.TM_CCORR_NORMED)
    elite_loc = bot.find_on_minimap(Lost_bot.minimap_elite_path, 0.95, cv2.TM_CCORR_NORMED)

    if my_loc:
        print("self found.")
        draw_rectangle(my_loc, (255, 0, 0))
    if boss_loc:
        print("boss found.")
        draw_rectangle(boss_loc, (0, 255, 0))
    if elite_loc:
        print("elite found.")
        draw_rectangle(elite_loc, (0, 0, 255))

    print(my_loc, boss_loc, elite_loc)

    my_real_loc = bot.get_center_loc()
    if my_loc and boss_loc:
        boss_real_dir = bot.get_heading_direction(my_loc, boss_loc)
        draw_line(my_real_loc, boss_real_dir)
    if my_loc and elite_loc:
        elite_real_dir = bot.get_heading_direction(my_loc, elite_loc)
        draw_line(my_real_loc, elite_real_dir)

    cv2.imshow("Heading!", screenshot)
    cv2.waitKey(0)

        
if __name__ == '__main__':
    # run_bot()
    run_unit_test()