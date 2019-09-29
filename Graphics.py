import pgl as GraphicLib
import Components
import random
import threading


# Constant Pool
WINDOW_HEIGHT = 854
WINDOW_WIDTH = 512
MAX_ENEMY = 4
PUT_ENEMY_INTERVAL = 2000


class DoubleClickInterruptException(Exception):
    pass


class CTimer(threading.Timer):
    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__(interval, function, args, kwargs)

    def return_start(self):
        super().start()
        return self

    def cancel(self) -> None:
        super().cancel()
        raise DoubleClickInterruptException


class CustomizedMainWindow(GraphicLib.GWindow):
    def __init__(self, width, height):
        super().__init__(width, height)

        # insert info bar
        self.__top_info_bar = TopInfoBar()
        self.add(self.__top_info_bar, 0, 0)

        self.__start_flag = False
        self.__current_boss_on = False
        self.__current_huge_on = False

        self.__end_label = GraphicLib.GLabel("Double Click To Start \n Click On The Plane To Control")

        self.interval_list = {}
        self.below_everything_list = []
        self.above_everything_list = []

        self.start_click_button = GraphicLib.GButton("Click To Strat", self.first_start)
        self.BUTTON_WIDTH = self.start_click_button.getWidth()
        self.BUTTON_HEIGHT = self.start_click_button.getHeight()
        self.add(self.start_click_button, (WINDOW_WIDTH - self.start_click_button.getWidth())/2, (WINDOW_HEIGHT - self.start_click_button.getHeight())/2)
        self.__clock = self.set_interval_with_param(self.add_enemy, PUT_ENEMY_INTERVAL, ())

        self.big_jet_plane = None

        self.max_enemy = MAX_ENEMY
        self.current_enemy_number = 0
        self.swift_num = 0
        self.normal_num = 0
        self.huge_num = 0
        self.boss_num = 0

        self.click_timer = None
        self.init()

        # self.start()

    @property
    def start_flag(self):
        return self.__start_flag

    def set_start(self):
        self.__start_flag = True

    def set_end(self):
        self.__start_flag = False

    def flip_start_flag(self):
        self.__start_flag = not self.__start_flag

    @property
    def current_boss_on(self):
        return self.__current_boss_on

    def switch_boss_on(self):
        self.__current_boss_on = not self.__current_boss_on

    @property
    def current_huge_on(self):
        return self.__current_huge_on

    def switch_huge_on(self):
        self.__current_huge_on = not self.__current_huge_on

    def set_interval_with_param(self, fn, delay, params):
        timer = CustomizedTimer(self, fn, delay, params)
        timer.setRepeats(True)
        # timer.start()
        return timer

    def get_elements_at(self, x, y):
        content = []
        for gobj in reversed(self.base.contents):
            if gobj.contains(x, y):
                content.append(gobj)
        return content

    def start_reset_handler(self):
        if not self.__start_flag:
            self.start()

    def reset(self):
        self.clear()
        self.repaint_info_bar_and_plane()
        self.reset_enemy_property()

    def paint_plane(self):
        self.big_jet_plane = Components.BigJetPlane(self)
        self.add(self.big_jet_plane, (WINDOW_WIDTH - Components.BigJetPlane.TEST_SIZE) / 2,
                 (WINDOW_HEIGHT - Components.BigJetPlane.TEST_SIZE))
        self.addEventListener("click", self.click_listener)
        self.addEventListener("mousemove", self.big_jet_plane.move_listener)

    def repaint_info_bar_and_plane(self):
        self.add(self.__top_info_bar, 0, 0)
        self.reset_info_bar_score()
        self.reset_damage_label(10)
        self.reset_level_label()
        self.reset_half_exp()
        self.reset_normal_protector_time()
        self.reset_nuclear_protector_time()
        self.reset_nuclear_boom_remaining_num()

        self.paint_plane()

    def first_start(self):
        self.start_click_button.fn = self.start_reset_handler
        self.remove(self.__end_label)
        self.remove(self.start_click_button)
        self.remove(self.start_click_button)

        self.set_start()
        self.__clock.start()

    def start(self):
        self.reset()
        self.remove(self.start_click_button)
        self.set_start()

    def add_start_button_at(self, x, y):
        self.add(self.start_click_button, x, y)

    def end(self):
        self.set_end()
        # set up end label
        self.__end_label.setLabel("You Got " + str(self.get_score()) + " Score!!! \n\nAdd money to become stronger!!! \n(Not Implemented Yet)")
        # set up payment
        label_width = self.__end_label.getWidth()
        label_height = self.__end_label.getHeight()
        self.add(self.__end_label, (WINDOW_WIDTH - label_width/3)/2, (WINDOW_WIDTH - label_height)/2)
        self.add_start_button_at((WINDOW_WIDTH - self.BUTTON_WIDTH) / 2, (WINDOW_WIDTH - self.BUTTON_HEIGHT) / 2 + label_height)

        photo = GraphicLib.GImage("./resources/paypal.png")
        self.add(photo, (WINDOW_WIDTH - photo.getWidth()) / 2, (WINDOW_WIDTH - self.BUTTON_HEIGHT) / 2 + label_height + self.start_click_button.getHeight() + 20)

    def init(self):
        self.paint_plane()
        label_width = self.__end_label.getWidth()
        label_height = self.__end_label.getHeight()
        self.add(self.__end_label, (WINDOW_WIDTH - label_width / 3) / 2, (WINDOW_WIDTH - label_height) / 2)
        self.add_start_button_at((WINDOW_WIDTH - self.BUTTON_WIDTH) / 2,
                                 (WINDOW_WIDTH - self.BUTTON_HEIGHT) / 2 + label_height)

    def click_listener(self, e):
        if self.click_timer is None:
            self.click_timer = CTimer(0.2, self.single_click_manager, [e]).return_start()
        else:
            try:
                self.click_timer.cancel()
            except DoubleClickInterruptException:
                self.double_click_manager()
            except Exception:
                print("Unknown Exception")
                import sys
                sys.exit()

    def single_click_manager(self, e):
        self.click_timer = None
        self.big_jet_plane.move_flag_listener(e)

    def double_click_manager(self):
        self.click_timer = None
        self.big_jet_plane.nuclear_boom_attack()

    def add_enemy(self):
        if self.__start_flag:
            if self.current_enemy_number < self.max_enemy:
                enemy_type = random.randint(0, 9)
                if enemy_type % 2 == 0:
                    self.put_enemy_on_board(Components.FlyingObjectIdentity.NORMAL.cls)
                    self.increase_enemy_on_board()
                elif enemy_type < 4:
                    self.put_enemy_on_board(Components.FlyingObjectIdentity.SWIFT.cls)
                    self.increase_enemy_on_board()
                elif enemy_type < 9 and not (self.__current_boss_on or self.__current_huge_on):
                    self.put_enemy_on_board(Components.FlyingObjectIdentity.HUGE.cls)
                    self.switch_huge_on()
                    self.increase_enemy_on_board()
                elif not (self.__current_boss_on or self.__current_huge_on):
                    self.put_enemy_on_board(Components.FlyingObjectIdentity.BOSS.cls)
                    self.switch_boss_on()
                    self.increase_enemy_on_board()

    def put_enemy_on_board(self, enemy_type):
        while True:
            random_start_x = random.randint(0, self.getWidth() - Components.BigJetPlane.TEST_SIZE)
            flag = True
            for i in self.interval_list.values():
                if random_start_x in i or (random_start_x + Components.BigJetPlane.TEST_SIZE) in i:
                    flag = False
                    break
            if flag:
                break

        ene = enemy_type(self)

        self.interval_list[ene] = range(random_start_x, random_start_x + Components.BigJetPlane.TEST_SIZE + 1)
        self.add(ene, random_start_x, TopInfoBar.BAR_HEIGHT)   #start_y)

    def decrease_enemy_on_board(self):
        self.current_enemy_number -= 1

    def increase_enemy_on_board(self):
        self.current_enemy_number += 1

    def set_score(self, value):
        self.__top_info_bar.set_score(str(value))

    def reset_info_bar_score(self):
        self.__top_info_bar.set_score(0)

    def set_health_percentage(self, value):
        self.__top_info_bar.set_health_percentage(value)

    def refill_health(self, max_health):
        self.__top_info_bar.set_health_percentage(1)
        self.__top_info_bar.set_health_text(max_health)

    def get_score(self):
        return self.__top_info_bar.get_score()

    def set_damage_label(self, value):
        self.__top_info_bar.set_damage(value)

    def reset_damage_label(self, value=10):
        self.__top_info_bar.set_damage(value)

    def set_level_label(self, value):
        self.__top_info_bar.set_level(value)

    def reset_level_label(self):
        self.__top_info_bar.reset_level()

    def set_half_exp_X(self, value):
        self.__top_info_bar.set_half_exp_X(value)

    def reset_half_exp(self):
        self.__top_info_bar.reset_half_exp()

    def reset_enemy_property(self):
        for cls in Components.Enemy.__subclasses__():
            cls.reset_property()

    def set_normal_protector_time(self, value):
        self.__top_info_bar.set_normal_protector_buff_time(value)

    def reset_normal_protector_time(self):
        self.__top_info_bar.set_normal_protector_buff_time(0)

    def set_nuclear_protector_time(self, value):
        self.__top_info_bar.set_nuclear_protector_remaining_time(value)

    def reset_nuclear_protector_time(self):
        self.__top_info_bar.set_nuclear_protector_remaining_time(0)

    def set_health_text(self, value):
        self.__top_info_bar.set_health_text(value)

    def set_nuclear_boom_remaining_num(self, value):
        self.__top_info_bar.set_nuclear_boom_remaining_num(value)

    def reset_nuclear_boom_remaining_num(self):
        self.__top_info_bar.set_nuclear_boom_remaining_num(1)


class Background(GraphicLib.GCompound):
    def __init__(self):
        super().__init__()
        #  not implemented


# Global Variables
main_window: CustomizedMainWindow


class TopInfoBar(GraphicLib.GCompound):
    BAR_WIDTH = WINDOW_WIDTH
    BAR_HEIGHT = WINDOW_HEIGHT * 0.1
    LABEL_X_MARGIN = 10
    TEXT_INTERVAL = 3
    HEALTH_BAR_LENGTH = 250

    HEALTH_BAR_MARGIN = 5

    def __init__(self):
        super().__init__()

        # insert background
        background = GraphicLib.GRect(WINDOW_WIDTH, self.BAR_HEIGHT)
        background.setColor("grey")
        background.setFilled(True)
        self.add(background, 0, 0)

        # left part

        # insert score bar
        score_prompt = GraphicLib.GLabel("SCORE/EXP: ")
        self.SCORE_LABEL_Y_COOR = self.BAR_HEIGHT / 3
        self.SCORE_X_COOR = self.LABEL_X_MARGIN + score_prompt.getWidth() + self.TEXT_INTERVAL
        self.SCORE_LABEL_HEIGHT = score_prompt.getHeight()

        self.__score_label = GraphicLib.GLabel("0")

        self.add(score_prompt, self.LABEL_X_MARGIN, self.SCORE_LABEL_Y_COOR)
        self.add(self.__score_label, self.SCORE_X_COOR, self.SCORE_LABEL_Y_COOR)

        # nuclear protector buff info

        nuclear_protector_buff_prompt_head = GraphicLib.GLabel("N: ")
        nuclear_protector_buff_prompt_head.setFont("bold 20px 'Times New Roman'")

        self.__nuclear_protector_buff_time_label = GraphicLib.GLabel("0")

        self.NUCLEAR_PROTECTOR_BUFF_PROMPT_H_X_COOR = self.LABEL_X_MARGIN
        self.NUCLEAR_PROTECTOR_PROMPT_N_X_COOR = self.NUCLEAR_PROTECTOR_BUFF_PROMPT_H_X_COOR + nuclear_protector_buff_prompt_head.getWidth()
        self.NUCLEAR_PROTECTOR_PROMPT_Y_COOR = nuclear_protector_buff_prompt_head.getHeight() + self.SCORE_LABEL_Y_COOR

        self.add(nuclear_protector_buff_prompt_head, self.NUCLEAR_PROTECTOR_BUFF_PROMPT_H_X_COOR, self.NUCLEAR_PROTECTOR_PROMPT_Y_COOR)
        self.add(self.__nuclear_protector_buff_time_label, self.NUCLEAR_PROTECTOR_PROMPT_N_X_COOR, self.NUCLEAR_PROTECTOR_PROMPT_Y_COOR)

        # nuclear boom info

        nuclear_boom_remaining_prompt = GraphicLib.GLabel("NBoom: ")
        self.__nuclear_boom_remaining_num_label = GraphicLib.GLabel("1")

        self.NUCLEAR_BOOM_PROMPT_X_COOR = self.NUCLEAR_PROTECTOR_PROMPT_N_X_COOR + \
                                          self.__nuclear_protector_buff_time_label.getWidth()+ \
                                          self.TEXT_INTERVAL * 3
        self.NUCLEAR_BOOM_NUM_LABEL_X_COOR = self.NUCLEAR_BOOM_PROMPT_X_COOR + nuclear_boom_remaining_prompt.getWidth()
        self.NUCLEAR_BOOM_PROMPT_Y_COOR = self.NUCLEAR_PROTECTOR_PROMPT_Y_COOR

        self.add(nuclear_boom_remaining_prompt, self.NUCLEAR_BOOM_PROMPT_X_COOR, self.NUCLEAR_BOOM_PROMPT_Y_COOR)
        self.add(self.__nuclear_boom_remaining_num_label, self.NUCLEAR_BOOM_NUM_LABEL_X_COOR, self.NUCLEAR_BOOM_PROMPT_Y_COOR)

        # normal protector buff info

        protector_buff_prompt_head = GraphicLib.GLabel("P: ")
        protector_buff_prompt_head.setFont("bold 20px 'Times New Roman'")

        self.__protector_buff_time_label = GraphicLib.GLabel("0")

        self.PROTECTOR_BUFF_H_X_COOR = self.NUCLEAR_PROTECTOR_BUFF_PROMPT_H_X_COOR
        self.PROTECTOR_BUFF_PROMPT_Y_COOR = self.NUCLEAR_PROTECTOR_PROMPT_Y_COOR + protector_buff_prompt_head.getHeight()
        self.PROTECTOR_BUFF_N_X_COOR = self.PROTECTOR_BUFF_H_X_COOR + protector_buff_prompt_head.getWidth()

        self.add(protector_buff_prompt_head, self.PROTECTOR_BUFF_H_X_COOR, self.PROTECTOR_BUFF_PROMPT_Y_COOR)
        self.add(self.__protector_buff_time_label, self.PROTECTOR_BUFF_N_X_COOR, self.PROTECTOR_BUFF_PROMPT_Y_COOR)

        # right part

        # insert health bar
        self.__health_bar_frame = GraphicLib.GRect(self.HEALTH_BAR_LENGTH, self.SCORE_LABEL_HEIGHT)
        self.__health_bar_frame.setColor('red')
        self.__health_bar = GraphicLib.GRect(self.HEALTH_BAR_LENGTH, self.SCORE_LABEL_HEIGHT)
        self.__health_bar.setColor('darkred')
        self.__health_bar.setFilled(True)
        self.__health_num_text = GraphicLib.GLabel("100")

        self.HEALTH_BAR_Y_COOR = score_prompt.getY() - score_prompt.getHeight() / 1.15
        self.HEALTH_BAR_X_COOR = self.BAR_WIDTH - self.HEALTH_BAR_MARGIN - self.HEALTH_BAR_LENGTH
        self.HEALTH_NUM_TEXT_X_COOR = self.HEALTH_BAR_X_COOR - self.__health_num_text.getWidth() - self.TEXT_INTERVAL*2
        self.HEALTH_NUM_TEXT_Y_COOR = score_prompt.getY()

        self.add(self.__health_num_text, self.HEALTH_NUM_TEXT_X_COOR, self.HEALTH_NUM_TEXT_Y_COOR)
        self.add(self.__health_bar_frame, self.HEALTH_BAR_X_COOR, self.HEALTH_BAR_Y_COOR)
        self.add(self.__health_bar, self.HEALTH_BAR_X_COOR, self.HEALTH_BAR_Y_COOR)

        # for reset health bar length
        self.BOUND_TUPLE = (self.BAR_WIDTH - self.HEALTH_BAR_MARGIN - self.HEALTH_BAR_LENGTH, self.HEALTH_BAR_Y_COOR)

        # damage info
        damage_prompt = GraphicLib.GLabel("DAMAGE: ")
        self.__damage_label = GraphicLib.GLabel("10")

        self.DAMAGE_PROMPT_X_COOR = self.HEALTH_BAR_X_COOR
        self.DAMAGE_PROMPT_Y_COOR = self.HEALTH_BAR_Y_COOR + self.health_bar.getHeight() + damage_prompt.getHeight()
        self.DAMAGE_LABEL_X_COOR = self.DAMAGE_PROMPT_X_COOR + damage_prompt.getWidth() + self.TEXT_INTERVAL

        self.add(damage_prompt, self.HEALTH_BAR_X_COOR, self.DAMAGE_PROMPT_Y_COOR)
        self.add(self.__damage_label, self.DAMAGE_LABEL_X_COOR, self.DAMAGE_PROMPT_Y_COOR)

        # level info
        level_prompt = GraphicLib.GLabel("LEVEL: ")
        self.__level_lable = GraphicLib.GLabel("1")

        self.LEVEL_PROMPT_X_COOR = self.DAMAGE_LABEL_X_COOR + self.__damage_label.getWidth() + 10 * self.TEXT_INTERVAL
        self.LEVEL_PROMPT_Y_COOR = self.DAMAGE_PROMPT_Y_COOR
        self.LEVEL_LABEL_X_COOR = self.LEVEL_PROMPT_X_COOR + level_prompt.getWidth() + self.TEXT_INTERVAL

        self.add(level_prompt, self.LEVEL_PROMPT_X_COOR, self.LEVEL_PROMPT_Y_COOR)
        self.add(self.__level_lable, self.LEVEL_LABEL_X_COOR, self.LEVEL_PROMPT_Y_COOR)

        # half exp/score
        half_exp_prompt = GraphicLib.GLabel("HALF SCORE/EXP × ")
        self.__half_exp_label = GraphicLib.GLabel("0")

        self.HALF_EXP_PROMPT_X_COOR = self.DAMAGE_PROMPT_X_COOR
        self.HALF_EXP_PROMPT_Y_COOR = self.DAMAGE_PROMPT_Y_COOR + damage_prompt.getHeight() + self.TEXT_INTERVAL
        self.HALF_EXP_LABEL_X_COOR = self.HALF_EXP_PROMPT_X_COOR + half_exp_prompt.getWidth() + self.TEXT_INTERVAL

        self.add(half_exp_prompt, self.HALF_EXP_PROMPT_X_COOR, self.HALF_EXP_PROMPT_Y_COOR)
        self.add(self.__half_exp_label, self.HALF_EXP_LABEL_X_COOR, self.HALF_EXP_PROMPT_Y_COOR)
        
    @property
    def get_nuclear_protector_time_label(self):
        return self.__nuclear_protector_buff_time_label

    def get_nuclear_protector_time(self):
        return self.__nuclear_protector_buff_time_label.getLabel()

    def set_nuclear_protector_remaining_time(self, value):
        self.__nuclear_protector_buff_time_label.setLabel(value)

    @property
    def get_nuclear_boom_remaining_num_label(self):
        return self.__nuclear_boom_remaining_num_label

    def get_nuclear_boom_remaining_num(self):
        return self.__nuclear_boom_remaining_num_label.getLabel()

    def set_nuclear_boom_remaining_num(self, value):
        self.__nuclear_boom_remaining_num_label.setLabel(str(value))

    @property
    def get_normal_protector_time_label(self):
        return self.__protector_buff_time_label

    def get_normal_protector_buff_time(self):
        return self.__protector_buff_time_label.getLabel()

    def set_normal_protector_buff_time(self, value):
        self.__protector_buff_time_label.setLabel(str(value))

    @property
    def score_label(self):
        return self.__score_label

    def get_score(self):
        return self.__score_label.getLabel()

    def set_score(self, value: str):
        self.__score_label.setLabel(value)

    @property
    def health_text(self):
        return self.__health_num_text

    def set_health_text(self, value):
        value = int(value)
        if value < 0:
            value = 0
        self.__health_num_text.setLabel(str(value))

    @property
    def health_bar(self):
        return self.__health_bar

    def set_health_percentage(self, health_percent):
        if health_percent < 0:
            health_percent = 0
        self.__health_bar.setBounds(*self.BOUND_TUPLE, health_percent * self.HEALTH_BAR_LENGTH, self.SCORE_LABEL_HEIGHT)

    @property
    def damage_label(self):
        return self.__damage_label

    def set_damage(self, value):
        self.__damage_label.setLabel(str(value))

    @property
    def level_label(self):
        return self.__level_lable

    def set_level(self, value):
        self.__level_lable.setLabel(str(value))

    def reset_level(self):
        self.__level_lable.setLabel("1")

    @property
    def half_exp_label(self):
        return self.__half_exp_label

    def set_half_exp_X(self, value):
        self.__half_exp_label.setLabel(str(value))

    def reset_half_exp(self):
        self.__half_exp_label.setLabel("0")


def init():
    """
        initiate main window.
    """
    # set up main window
    global main_window
    main_window = CustomizedMainWindow(WINDOW_WIDTH, WINDOW_HEIGHT)
    main_window.setWindowTitle("Big Jet Plane(卡)")

    # TODO pause button (optional)
    # TODO add background rocks
    # TODO add background moving animation


class CustomizedTimer(GraphicLib.GTimer):
    def __init__(self, gw, fn, delay, params):
        super().__init__(gw, fn, delay)
        self.params = params

    def timerTicked(self):
        self.fn(*self.params)
        if self.repeats:
            tkc = self.gw.canvas
            tkc.after(self.delay, self.timerTicked)


if __name__ == "__main__":
    init()
