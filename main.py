import pyautogui, time, random, cv2, math, keyboard, os, numpy as np
import time
from random import randint
from threading import Thread
from window_capture import WindowCapture
pyautogui.FAILSAFE = False
from config import configure_config

class Lost_bot():

    # propeties
    wincapture = WindowCapture("LOST ARK (64-bit, DX11) v.2.3.4.1")
    translate_pos = wincapture.get_screen_position
    global screenshot
    screenshot = wincapture.get_screenshot()
    IN_CITY = True
    MOVE = False
    CAST = False
    BOT_WORKING = False
    SHOULD_EXIT = False
    TIMEOUT = 600  # seconds.
    available_spells = []
    window_size = (wincapture.w, wincapture.h)
    print(wincapture)
    method = cv2.TM_CCORR_NORMED

    resurection_path = "images\\base_res.png"
    in_game_icon_path = "images\\in_game_icon.jpg"
    portal_path = "images\\portal.jpg"

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
            if result != False:
                self.available_spells.append(spell)
        print("available spells: ", self.available_spells)
        return self.available_spells

    def find_pos(self, what_find_path, threshold, method):
        find_this = cv2.imread(what_find_path, cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(screenshot, find_this, method)
        _, maxVal, _, maxLoc = cv2.minMaxLoc(result)
        print(maxVal, what_find_path)
        if maxVal > threshold:
            return self.wincapture.get_screen_position(maxLoc)
        else:
            return False

    def scan_for_portal(self):
        while not self.IN_CITY:
            pos = self.find_pos(self.portal_path, 0.90, cv2.TM_CCORR_NORMED)
            if pos:
                print(pos)
                print("Portal appeared!")
                self.SHOULD_EXIT = True
                break

    def pos_dirs(self, index):
        x = [959, 960, 1034, 1049, 1024, 953, 886, 862, 884]
        y = [528, 419, 469, 516, 585, 581, 561, 512, 444]
        return self.wincapture.get_screen_position((x[index], y[index]))

    def pos_center(self):
        return self.wincapture.get_screen_position((959, 528))

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
        if x != False:
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

    def moveToClick(loc):
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
        
if __name__ == '__main__':
    run_bot()