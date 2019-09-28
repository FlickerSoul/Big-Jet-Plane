import pgl as GraphicLib
import Components
import random


# Constant Pool
WINDOW_HEIGHT = 854
WINDOW_WIDTH = 512
MAX_ENEMY = 4
PUT_ENEMY_INTERVAL = 2000


class CustomizedMainWindow(GraphicLib.GWindow):

    def __init__(self, width, height):
        super().__init__(width, height)

        # insert info bar
        self.__top_info_bar = TopInfoBar()
        self.add(self.__top_info_bar, 0, 0)

        self.__start_flag = False
        self.__current_boss_on = False
        self.__current_huge_on = False

        self.start_prompt = GraphicLib.GLabel("Double Click To Start \n Click On The Plane To Control")
        self.start_prompt.setColor('blue')
        self.start_prompt_width = self.start_prompt.getWidth()
        self.start_prompt_height = self.start_prompt.getHeight()

        self.end_prompt = GraphicLib.GLabel("Double Click To Start")
        self.end_prompt.setColor('blue')
        self.end_prompt_width = self.end_prompt.getWidth()
        self.end_prompt_height = self.end_prompt.getHeight()

        self.__end_label = GraphicLib.GLabel("")

        self.interval_list = {}
        self.below_everything_list = []
        self.above_everything_list = []

        self.start_click_button = GraphicLib.GButton("Click To Strat", self.start_reset_handler)
        self.BUTTON_WIDTH = self.start_click_button.getWidth()
        self.BUTTON_HEIGHT = self.start_click_button.getHeight()
        # self.addEventListener('drag', self.start_reset_handler)
        self.add(self.start_click_button, (WINDOW_WIDTH - self.start_click_button.getWidth())/2, (WINDOW_HEIGHT - self.start_click_button.getHeight())/2)
        self.__clock = self.set_interval_with_param(self.add_enemy, PUT_ENEMY_INTERVAL, ())

        self.big_jet_plane = None

        self.max_enemy = MAX_ENEMY
        self.current_enemy_number = 0
        self.swift_num = 0
        self.normal_num = 0
        self.huge_num = 0
        self.boss_num = 0

        # self.reset()
        self.start()

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
        self.repaint_info_bar()
        self.reset_enemy_property()

    def repaint_info_bar(self):
        self.add(self.__top_info_bar, 0, 0)
        self.reset_info_bar_score()
        self.reset_damage_label(10)
        self.reset_level_label()
        self.reset_half_exp()

    def start(self):
        self.reset()
        self.remove(self.start_click_button)
        # self.__start_flag = True
        self.set_start()
        self.init()

    def add_start_button_at(self, x, y):
        self.add(self.start_click_button, x, y)

    def end(self):
        self.set_end()
        # self.add(self.end_prompt, (WINDOW_WIDTH - self.end_prompt_width)/2, (WINDOW_WIDTH - self.end_prompt_height)/2)
        # set up end label
        self.__end_label.setLabel("You Got " + str(self.get_score()) + " Score!!!")
        label_width = self.__end_label.getWidth()
        label_height = self.__end_label.getHeight()
        self.add(self.__end_label, (WINDOW_WIDTH - label_width)/2, (WINDOW_WIDTH - label_height)/2)
        # self.add(self.start_click_button, (WINDOW_WIDTH - self.BUTTON_WIDTH)/2, (WINDOW_WIDTH - self.BUTTON_HEIGHT)/2 + label_height)
        self.add_start_button_at((WINDOW_WIDTH - self.BUTTON_WIDTH) / 2, (WINDOW_WIDTH - self.BUTTON_HEIGHT) / 2 + label_height)


    def init(self):
        self.big_jet_plane = Components.BigJetPlane(self)
        self.add(self.big_jet_plane, (WINDOW_WIDTH - Components.BigJetPlane.TEST_SIZE)/2, (WINDOW_HEIGHT - Components.BigJetPlane.TEST_SIZE))
        self.addEventListener('click', self.big_jet_plane.move_flag_listener)
        self.addEventListener('mousemove', self.big_jet_plane.move_listener)

        self.__clock.start()

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

    def refill_health(self):
        self.__top_info_bar.set_health_percentage(1)

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

        # insert score bar
        score_prompt = GraphicLib.GLabel("SCORE/EXP: ")
        self.SCORE_LABEL_Y_COOR = self.BAR_HEIGHT / 3
        self.SCORE_X_COOR = self.LABEL_X_MARGIN + score_prompt.getWidth() + self.TEXT_INTERVAL
        self.SCORE_LABEL_HEIGHT = score_prompt.getHeight()

        self.__score_label = GraphicLib.GLabel("0")

        self.add(score_prompt, self.LABEL_X_MARGIN, self.SCORE_LABEL_Y_COOR)
        self.add(self.__score_label, self.SCORE_X_COOR, self.SCORE_LABEL_Y_COOR)

        # insert health bar
        self.__health_bar_frame = GraphicLib.GRect(self.HEALTH_BAR_LENGTH, self.SCORE_LABEL_HEIGHT)
        self.__health_bar_frame.setColor('red')
        self.__health_bar = GraphicLib.GRect(self.HEALTH_BAR_LENGTH, self.SCORE_LABEL_HEIGHT)
        self.__health_bar.setColor('darkred')
        self.__health_bar.setFilled(True)

        self.HEALTH_BAR_Y_COOR = score_prompt.getY() - score_prompt.getHeight() / 1.15
        self.HEALTH_BAR_X_COOR = self.BAR_WIDTH - self.HEALTH_BAR_MARGIN - self.HEALTH_BAR_LENGTH

        self.add(self.__health_bar_frame, self.HEALTH_BAR_X_COOR, self.HEALTH_BAR_Y_COOR)
        self.add(self.__health_bar, self.HEALTH_BAR_X_COOR, self.HEALTH_BAR_Y_COOR)

        # for reset health bar length
        self.BOUND_TUPLE = (self.BAR_WIDTH - self.HEALTH_BAR_MARGIN - self.HEALTH_BAR_LENGTH, self.HEALTH_BAR_Y_COOR)

        # damage info
        damage_prompt = GraphicLib.GLabel("DAMAGE: ")
        self.__damage_label = GraphicLib.GLabel("0")

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

        # buff info section

    @property
    def score_label(self):
        return self.__score_label

    def get_score(self):
        return self.__score_label.getLabel()

    def set_score(self, value: str):
        self.__score_label.setLabel(value)

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
    main_window.setWindowTitle("卡")

    # TODO pause button (optional)

    # set up background
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
