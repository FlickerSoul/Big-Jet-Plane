import enum

import Components
import pgl as GraphicLib

HEIGHT = 15
WIDTH = 2
FLYING_SPEED = 20
MOVE_DELAY = 20


# class SingleMG(GraphicLib.GCompound):
class SingleMG(GraphicLib.GRect):
    def __init__(self, damage, main_window):
        super().__init__(WIDTH, HEIGHT)

        self.__main_window = main_window
        self.__flying_speed = FLYING_SPEED
        self.__appearance_file_path = ""
        self.__damage = damage

        self.setColor('orange')
        self.setFilled(True)

        self.com_height = HEIGHT
        self.com_width = (Components.BigJetPlane.TEST_SIZE - WIDTH) / 2

    @property
    def main_window(self):
        return self.__main_window

    @property
    def flying_speed(self):
        return self.__flying_speed

    @property
    def damage(self):
        return self.__damage

    def move_animation(self):
        self.timer = self.main_window.set_interval_with_param(self.move_to, MOVE_DELAY, (0, -self.flying_speed))
        self.timer.start()

    def move_to(self, dx, dy):
        if self.getY() + HEIGHT < 0:
            self.timer.stop()
            self.main_window.remove(self)
            del self
        else:
            self.move(dx, dy)
            self.__is_hit()

    def __is_hit(self):
        elem: Components.FlyingObject = self.main_window.getElementAt(self.getX() + 1, self.getY() - HEIGHT / 10)
        if issubclass(elem.__class__, Components.Enemy):
            self.timer.stop()
            elem.change_health_with(-self.damage)
            self.main_window.remove(self)
            del self
            return True
        return False

    def is_hit_out(self, x, y):
        elem: Components.FlyingObject = self.main_window.getElementAt(self.getX() + x + 1, y - HEIGHT / 10)
        if issubclass(elem.__class__, Components.Enemy):
            elem.change_health_with(-self.damage)
            self.getParent().remove(self)
            del self
            return True
        return False


class NMG(GraphicLib.GCompound):
    def __init__(self, damage, main_window, n_bullet):
        super().__init__()

        self.__n_bullet = n_bullet

        for i in range(n_bullet):
            temp_bullet = SingleMG(damage, main_window)
            self.add(temp_bullet, i * (4 - 1) * WIDTH, 0)

        self.main_window = main_window

        self.com_height = HEIGHT
        self.com_width = (Components.BigJetPlane.TEST_SIZE - self.getWidth()) / 2

    def move_animation(self):
        self.timer = self.main_window.set_interval_with_param(self.move_to, MOVE_DELAY, (0, -FLYING_SPEED))
        self.timer.start()

    def move_to(self, dx, dy):
        if self.getY() < 85.4:  # info bar height
            self.timer.stop()
            self.main_window.remove(self)
            del self
        else:
            self.move(dx, dy)
            eles = [self.getElement(i) for i in range(0, self.getElementCount())]
            for i in range(self.getElementCount()):
                eles[i].is_hit_out(self.getX() + i * self.__n_bullet * WIDTH, self.getY())


class NuclearBoom:

    @staticmethod
    def release_boom(main_window: GraphicLib.GWindow):
        for ele in main_window.base.contents:
            if issubclass(ele.__class__, Components.Enemy):
                ele.boom()


class LightBall(GraphicLib.GOval):
    NORMAL_SIZE = 5

    def __init__(self, damage, main_window, color, size=(NORMAL_SIZE, NORMAL_SIZE)):
        super().__init__(*size)

        self.__main_window = main_window
        self.__appearance_file_path = ""
        self.__damage = damage

        self.setColor(color)
        self.setFilled(True)

        # where you should put your ball
        self.com_height = Components.BigJetPlane.TEST_SIZE
        self.com_width = (Components.BigJetPlane.TEST_SIZE - self.getWidth()) / 2

    @property
    def main_window(self):
        return self.__main_window

    @property
    def damage(self):
        return self.__damage

    def is_hit_out(self, x, y):
        elem: Components.BigJetPlane = self.main_window.getElementAt(self.getX() + x + 1, y - HEIGHT / 5)
        if issubclass(elem.__class__, Components.BigJetPlane):
            # self.timer.stop()
            if elem.is_nuclear_shield_on:
                elem.change_health_with(-self.damage/4)
            elif not elem.is_normal_shield_on:
                elem.change_health_with(-self.damage)
            self.getParent().remove(self)
            del self
            return True
        return False


class LightBallStringCompound(GraphicLib.GCompound):
    LIGHT_BALL_MOVE_DELAY = int(15 * 4 / 3)
    LIGHT_BALL_INTERVAL = 2
    LIGHT_BALL_FLYING_SPEED = 5 * 4 / 3

    def __init__(self, main_window, num, damage, flying_speed=LIGHT_BALL_FLYING_SPEED):
        super().__init__()

        self.main_window = main_window

        # where you should put your ball
        for i in range(num):
            ball = LightBall(damage, main_window, 'red')
            self.add(ball, 0, i * LightBallStringCompound.LIGHT_BALL_INTERVAL * LightBall.NORMAL_SIZE)

        self.com_height = Components.BigJetPlane.TEST_SIZE
        self.com_width = (Components.BigJetPlane.TEST_SIZE - self.getWidth()) / 2

        # speed is positive, moving downward
        self.timer = self.main_window.set_interval_with_param(self.move_to, LightBallStringCompound.LIGHT_BALL_MOVE_DELAY, (0, flying_speed))
        self.move_animation()

    def move_animation(self):
        self.timer.start()

    def move_to(self, dx, dy):
        if not self.main_window.start_flag:
            self.timer.stop()
            return
        if self.getY() >= self.main_window.getHeight():
            self.timer.stop()
            self.main_window.remove(self)
            del self
        else:
            self.move(dx, dy)
            eles = [self.getElement(i) for i in range(0, self.getElementCount())]
            for i in range(self.getElementCount()):
                eles[i].is_hit_out(self.getX() + i * 3 * WIDTH, self.getY())

class BulletIdentity(enum.Enum):

    SINGLE_MG = "BULLET", SingleMG
    N_MG = "BULLET", NMG
    NUCLEAR_BOOM = "BULLET", NuclearBoom
    LIGHT_BALL = "BULLET", LightBallStringCompound

    def __init__(self, kind, cls):
        self.__kind = kind
        self.__cls = cls

    @property
    def kind(self):
        return self.__kind

    @property
    def cls(self):
        return self.__cls
