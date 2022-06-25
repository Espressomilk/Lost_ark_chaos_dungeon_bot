import pyautogui, time, random, cv2, math, keyboard, os, numpy as np
import time
from random import randint
from threading import Thread
from window_capture import WindowCapture
pyautogui.FAILSAFE = False
from config import configure_config

class Lost_bot():

    global screenshot
    try:
        wincapture = WindowCapture("LOST ARK (64-bit, DX11) v.2.3.5.1")
        translate_pos = wincapture.get_screen_position
        screenshot = wincapture.get_screenshot()
        window_size = (wincapture.w, wincapture.h)
    except:
        wincapture = WindowCapture("TEST", True)
        screenshot = None

    IN_CITY = True
    MOVE = False
    TIMEOUT = 250  # seconds.
    available_spells = []

    RUN_COUNT = 0
    RESURRECT_COUNT = 0

    resurrection_path = "images\\base_res.jpg"
    in_game_icon_path = "images\\in_game_icon.jpg"
    portal_path = "images\\portal.jpg"
    minimap_boss_path = "images\\minimap_boss.jpg"
    minimap_elite_path = "images\\minimap_elite.jpg"
    minimap_portal_path = "images\\minimap_portal.jpg"
    minimap_self_east_path = "images\\minimap_self_east.jpg"
    minimap_self_north_path = "images\\minimap_self_north.jpg"
    minimap_crystal_tower_path = "images\\minimap_crystal_tower.jpg"
    level_2_path = "images\\level_2.jpg"
    blue_portal_path = "images\\blue_portal.jpg"

    text_file = open("config.txt", "r")
    lines = text_file.read().split('\n')
    for row in lines:
        if "spells" in row:
            all_spells = row.replace("spells =","").replace(" ","")
        elif "spell/time" in row:
            duration = row[15:].split(" ")

    def __init__(self, test_screenshot = []):
        self.should_exit = False
        self.target_direction = None
        self.not_in_game_count = 0
        self.is_level_2 = False
        self.disable_cast = False
        if test_screenshot != []:
            global screenshot
            screenshot = test_screenshot

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
        return (1743, 184)

    def get_minimap(self):
        offset = self.get_minimap_offset()
        return screenshot[offset[0][0]:offset[0][1], offset[1][0]:offset[1][1]]

    def find_on_minimap(self, target_path, threshold, method):
        target = cv2.imread(target_path, cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(self.get_minimap(), target, method)
        _, maxVal, _, maxLoc = cv2.minMaxLoc(result)
        absoluteLoc = (maxLoc[0] + self.get_minimap_offset()[1][0] + target.shape[0] // 2, 
                       maxLoc[1] + self.get_minimap_offset()[0][0] + target.shape[1] // 2)
        if maxVal > threshold:
            print(maxVal, target_path)
            return self.wincapture.get_screen_position(absoluteLoc)
        else:
            return None

    def find_pos(self, target_path, threshold, method):
        target = cv2.imread(target_path, cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(screenshot, target, method)
        _, maxVal, _, maxLoc = cv2.minMaxLoc(result)
        if maxVal > threshold:
            return self.wincapture.get_screen_position(maxLoc)
        else:
            return None

    def calc_distance(self, loc1, loc2):
        print(loc1, loc2)
        return math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)

    def get_heading_direction(self, my_loc, target_loc, multifier=3):
        my_real_loc = self.get_center_loc()
        print(target_loc[0] - my_loc[0], target_loc[1] - my_loc[1])
        return (my_real_loc[0] + (target_loc[0] - my_loc[0]) * multifier,
                my_real_loc[1] + (target_loc[1] - my_loc[1]) * multifier)

    def scan_for_portal(self):
        print("Portal scanning registered...")
        while not self.IN_CITY:
            portal_pos = self.find_pos(self.portal_path, 0.90, cv2.TM_CCORR_NORMED)
            if portal_pos:
                print("Portal appeared!")
                self.should_exit = True

            # blue_portal_pos = self.find_pos(self.blue_portal_path, 0.90, cv2.TM_CCORR_NORMED)
            # if blue_portal_pos:
            #     print("Portal in sight!")
            #     pyautogui.moveTo(blue_portal_pos[0], blue_portal_pos[1], random.uniform(0.1, 0.3))
            #     pyautogui.click(button='right')
            #     self.waitRandomizedTime(1, 2)
            #     self.should_exit = True
        print("Portal scanning ends...")
    
    def check_disable_cast(self, self_minimap_pos, target_minimap_pos):
        if self.calc_distance(self_minimap_pos, target_minimap_pos) > 50:
            if not self.disable_cast:
                print("Target too far. Disable casting...")
            self.disable_cast = True
        else:
            if self.disable_cast:
                print("Target nearby. Enable casting...")
            self.disable_cast = False


    def scan_minimap(self):
        print("Minimap scanning registered...")
        while not self.IN_CITY:
            boss_minimap_pos = self.find_on_minimap(self.minimap_boss_path, 0.68, cv2.TM_CCOEFF_NORMED)
            elite_minimap_pos = self.find_on_minimap(self.minimap_elite_path, 0.68, cv2.TM_CCOEFF_NORMED)
            portal_minimap_pos = self.find_on_minimap(self.minimap_portal_path, 0.68, cv2.TM_CCOEFF_NORMED)
            self_minimap_pos = self.get_minimap_center()
            crystal_tower_minimap_pos = self.find_on_minimap(self.minimap_crystal_tower_path, 0.68, cv2.TM_CCOEFF_NORMED)
            if crystal_tower_minimap_pos:
                print("Accidentally entered third floor. Exiting now...")
                self.should_exit = True
                self.is_level_2 = True
            elif elite_minimap_pos:
                print("Elite found on minimap at", elite_minimap_pos)
                self.target_direction = self.get_heading_direction(self_minimap_pos, elite_minimap_pos)
                self.is_level_2 = True
                self.check_disable_cast(self_minimap_pos, elite_minimap_pos)
            elif boss_minimap_pos:
                print("Boss found on minimap at", boss_minimap_pos)
                self.target_direction = self.get_heading_direction(self_minimap_pos, boss_minimap_pos)
                self.is_level_2 = True
                self.check_disable_cast(self_minimap_pos, boss_minimap_pos)
            elif portal_minimap_pos:
                print("Portal found on minimap at", portal_minimap_pos)
                self.target_direction = self.get_heading_direction(self_minimap_pos, portal_minimap_pos)
                self.check_disable_cast(self_minimap_pos, portal_minimap_pos)
                if self.is_level_2:
                    self.should_exit = True
            else:
                self.target_direction = None
                self.disable_cast = False
            time.sleep(0.5)
        print("Minimap scanning ends...")

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
        
            if not self.target_direction:
                random_pos = self.pos_dirs(randint(0, 8))
                pyautogui.moveTo(random_pos[0] + randint(-5, 5), random_pos[1] + randint(-5, 5), random.uniform(0.1, 0.3))
                if self.is_level_2 and randint(0, 1):
                    # Wondering more in second floor to avoid stuck.
                    pyautogui.mouseDown(button='right')
                    self.waitRandomizedTime(0.5, 1)
                    pyautogui.mouseUp(button='right')

            pyautogui.keyDown(cast)
            self.waitRandomizedTime(0.07, 0.15)
            pyautogui.keyUp(cast)
            self.waitRandomizedTime(0.07, 0.15)
            # Double click.
            pyautogui.keyDown(cast)
            self.waitRandomizedTime(0.07, 0.15)
            pyautogui.keyUp(cast)
            self.available_spells.remove(cast)
            if cast == 'r' or cast == 'f':
                self.waitRandomizedTime(1.3, 1.5)
            else:
                self.waitRandomizedTime(0.5, 1)

    def ressurrection_range(self):
        loc = [randint(1266, 1467), randint(428, 466)]
        return self.wincapture.get_screen_position(loc)

    def check_resurrection(self):
        x = self.find_pos(self.resurrection_path, 0.95, cv2.TM_CCORR_NORMED)
        if x:
            print("Resurrecting!")
            self.moveToClick(self.ressurrection_range())
            self.RESURRECT_COUNT += 1

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
        self.should_exit = False

    def enter_next_level(self):
        pyautogui.press('g')

    def character_move_to(self, pos):
        random_action = randint(0, 5)
        pyautogui.moveTo(pos[0], pos[1], random.uniform(0.1, 0.3))
        if random_action == 0:
            pyautogui.press('space')
        else:
            pyautogui.mouseDown(button='right')
            self.waitRandomizedTime(0.5, 1.5)
            pyautogui.mouseUp(button='right')

    def exit_chaos(self):
        self.moveToClick(self.exit_range())
        self.waitRandomizedTime(0.5, 0.8)
        self.check_ok()
        self.IN_CITY = True

    def print_state(self, remaining_time):
        print("============================================================================================================")
        print("Remaining seconds: ", remaining_time)
        print("IN_CITY\tMOVE\texit\tlevel2\tcast\tdirec")
        print(self.IN_CITY, self.MOVE, self.should_exit, self.is_level_2, self.disable_cast, self.target_direction, sep='\t')
        print("============================================================================================================")

    ## do chaos dungeon after finding one
    def do_chaos(self):
        start_time = time.time()
        force_cast_count = 0
        state_count = 10
        while not self.IN_CITY and time.time() - start_time < self.TIMEOUT:
            if state_count >= 10:
                self.print_state(self.TIMEOUT - (time.time() - start_time))
                state_count = 0
            else:
                state_count += 1
            if not self.MOVE:
                self.MOVE = True
                Thread(target = self.scan_for_portal).start()
                Thread(target = self.scan_minimap).start()
            if self.is_in_game():
                if self.should_exit:
                    if not self.is_level_2:
                        print("Entering next level.")
                        self.enter_next_level()
                    else:
                        print("Exiting dungeon.")
                        self.exit_chaos()
                    self.should_exit = False
                    continue
                if self.target_direction:
                    print("Heading to ", self.target_direction)
                    self.character_move_to(self.target_direction)
                if not self.disable_cast or force_cast_count >= 10:
                    force_cast_count = 0
                    self.cast_spell(self.all_spells)
                else:
                    force_cast_count += 1
                    print("cast disabled...", force_cast_count)
            else:
                self.not_in_game_count += 1
                print("Not in game! Perhaps loading..." + str(self.not_in_game_count))
        if not self.IN_CITY:
            print("Exiting dungeon due to timeout.")
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
            print("RUN_COUNT:", Lost_bot.RUN_COUNT)
            print("RESURRECT_COUNT:", Lost_bot.RESURRECT_COUNT)
            os._exit(1)
        time.sleep(1)


def run_bot():
    # configure = input("Do you want configure bot? Y/N\n").lower()
    # if configure == "y":
    #     configure_config()
    total_time = int(input("How long do you want to run? (minutes)"))
    start_time = time.time()
    Esc = True
    repair_count = 10  # Start with repairing.
    while True and (time.time() - start_time) / 60 < total_time:
        bot = Lost_bot()
        if Esc:
            Thread(target = kill_bot, args = ()).start()
            Esc = False
        if repair_count >= 10:
            repair_count = 0
            print("Reparing...")
            bot.repair_items()
        bot.waitRandomizedTime(1, 2)
        print("Entering chaos...")
        bot.alt_q_chaos()
        bot.waitRandomizedTime(5, 8)
        bot.do_chaos()
        repair_count += 1
        Lost_bot.RUN_COUNT += 1
        bot.waitRandomizedTime(15, 20)
    print("Whole run complete.")
    os._exit(1)

        
if __name__ == '__main__':
    run_bot()