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
    wincapture.focus_window()
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
    z = 0
    global regions
    regions =   {"region_results" : (238,119,1873,926), 
                "region_check_in_fight" : (245,0,563,116),
                "region_check_accept" : (700,410,1260,700),
                "region_check_ok" : (570,725,1400,1065),
                "region_minimap" : (1593,40,1889,295),
                }
    minimap_path = 'images\\minimap.png'
    target_path = 'images\\pixel.png'
    # mini_boss_path = "boss2.png"
    # final_boss_path = "final_boss2.png"
    # enemy_path = "enemy.png"
    # portal_path = "portal2.png"
    spell_check = "images\\spell_check.png"
    result_path = "images\\result.png"
    solo_path = "images\\solo.jpg"
    shortcut_path = "images\\shortcut.jpg"
    ok2_button_path = "images\\ok.png"
    resurection_path = "images\\base_res.png"
    check_in_fight_path = "images\\check_in_fight.jpg"
    accept_path = "images\\accept.jpg"
    in_game_icon_path = "images\\in_game_icon.jpg"
    portal_path = "images\\portal.jpg"

    not_in_game_count = 0



    def waitRandomizedTime(self, min, max):
        time.sleep(random.uniform(min, max))

    # load config
    text_file = open("config.txt", "r") ## load config files
    lines = text_file.read().split('\n')
    for row in lines:
        if "spells" in row:
            all_spells = row.replace("spells =","").replace(" ","")
        elif "spell/time" in row:
            duration = row[15:].split(" ")
        elif "song of escape" in row:
            song_of_escape = row[-1:]
        elif "repair" in row:
            repair = row.replace("repair:","").replace(" ","").lower()
    
    def focus_game_window(self):
        self.Lost_ark.minimize()
        self.Lost_ark.restore()
        self.Lost_ark.resizeTo(1920,1080)
        self.Lost_ark.moveTo(0,0)

    def check_available_spell(self, all_spells):  # check region what spells are available
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

    def cast_spell(self, spells):  ##check spells and cast first avalible
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

    ## exit from dungeon if finish
    def exit(self, song_of_escape):
        if self.find_pos(self.result_path, 0.95, cv2.TM_CCORR_NORMED) != False:
            while True:
                time.sleep(randint(2,3))
                pyautogui.press(song_of_escape)
                time.sleep(randint(8,10))
                if self.find_pos(self.ok2_button_path, 0.99, cv2.TM_CCORR_NORMED) == False:
                    self.MOVE = False
                    return True
        else:
            return False
            
    def check_res(self): ## check if character is dead
        x = self.find_pos(self.resurection_path, 0.98, cv2.TM_CCORR_NORMED)
        if x != False:
            try:
                pyautogui.moveTo(x[0] + randint(5,25), x[1 + randint(5, 10)])
                self.waitRandomizedTime(1,2)
                pyautogui.click()
            except:
                pass

    def is_in_game(self):
        icon = self.find_pos(self.in_game_icon_path, 0.99, cv2.TM_CCORR_NORMED)
        return icon

    def check_in_fight(self):  ##check if character is in city
        if self.find_pos(self.check_in_fight_path, 0.9, cv2.TM_CCORR_NORMED) != False:
            self.MOVE = False
            return False
        else:
            return True

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

    def repair_items(self):
        self.wincapture.focus_window()
        pyautogui.hotkey('alt', 'p')
        self.waitRandomizedTime(1, 2)
        repair_icon = self.repair_icon_range()
        pyautogui.moveTo(repair_icon[0], repair_icon[1], random.uniform(0.1, 0.5))
        pyautogui.click()
        self.waitRandomizedTime(1, 2)
        repair_equiped_gear = self.repair_equiped_gear_range()
        pyautogui.moveTo(repair_equiped_gear[0], repair_equiped_gear[1], random.uniform(0.1, 0.5))
        pyautogui.click()
        self.waitRandomizedTime(1, 2)
        pyautogui.press("esc")
        self.waitRandomizedTime(1, 2)
        pyautogui.press("esc")

    def alt_q_chaos(self):
        self.wincapture.focus_window()
        pyautogui.hotkey('alt', 'q')
        self.waitRandomizedTime(1, 2)
        chaos_pos = self.shortcut_range()
        pyautogui.moveTo(chaos_pos[0], chaos_pos[1], random.uniform(0.1, 0.5))
        pyautogui.click()
        self.waitRandomizedTime(1, 2)
        solo_pos = self.solo_range()
        pyautogui.moveTo(solo_pos[0], solo_pos[1], random.uniform(0.1, 0.5))
        pyautogui.click()

        self.check_accept()
        self.IN_CITY = False
        self.SHOULD_EXIT = False

    ## do chaos dungeon after finding one
    def do_chaos(self):
        start_time = time.time()
        while not self.IN_CITY and time.time() - start_time < self.TIMEOUT:
            if not self.MOVE:
                self.MOVE = True
                start_scan = Thread(target = self.scan_for_portal)
                start_scan.start()
            if self.is_in_game():
                self.check_res()
                self.cast_spell(self.all_spells)
            else:
                self.not_in_game_count += 1
                print("Not in game! Perhaps loading..." + str(self.not_in_game_count))
            if self.SHOULD_EXIT:
                exit_icon = self.exit_range()
                pyautogui.moveTo(exit_icon[0], exit_icon[1], random.uniform(0.1, 0.5))
                pyautogui.click()
                self.waitRandomizedTime(0.5, 0.8)
                self.check_ok()
                self.IN_CITY = True
                self.waitRandomizedTime(10, 12)
            # self.check_res()
            # self.check_accept()
            # self.IN_CITY = self.exit( self.song_of_escape)
            

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
    Esc = True
    count = 10
    while True:
        bot = Lost_bot()
        if Esc:
            Thread(target = kill_bot, args = ()).start()
            Esc = False
        if count >= 10:
            count = 0
            bot.repair_items()
        bot.waitRandomizedTime(1, 2)
        bot.alt_q_chaos()
        bot.do_chaos()
        count += 1
        
if __name__ == '__main__':
    run_bot()