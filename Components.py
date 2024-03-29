import pgl as GraphicLib
import Graphics
import enum
import Bullet
import Buffs
import random


FlyingObjectKind = enum.Enum("FlyingObjectKind", ("SELF", "ENEMY"))


class FlyingObject(GraphicLib.GCompound):
    BLAST_START_1 = 5
    BLAST_START_2 = 27

    def __init__(self, main_window: Graphics.CustomizedMainWindow, identity,
                 flying_speed: float, appearance_file_path: str,
                 health: float, bullet_damage: float, attack_type,
                 object_level: int = 1,
                 attack_interval=250):
        """
        initiate a flying object.
        identity: the identity of this flying object
        flyingSpeed: flying speed of the object
        appearanceFilePath: the file path of the appearence
        health: the health of this object
        objectLevel: The level of this flying object, default level is 1
        damage: the damage that deliver to other objects
        attackType: the attack method of the object
        """
        super().__init__()

        # init attributes
        self.__identity = identity
        self.__flying_speed = flying_speed
        self.__health = health
        self.__max_health = self.health
        self.__bullet_damage = bullet_damage
        self.__object_level = object_level
        self.__main_window = main_window
        self.__attack_type = attack_type
        self.__attack_interval = attack_interval
        # self.attack_timer = None
        self.attack_timer = self.main_window.set_interval_with_param(self.attack_method, self.attack_interval, (self.attack_type,))

        image = GraphicLib.GImage(appearance_file_path)
        self.add(image)

        self.__move_flag = False

    # getter methods
    @property
    def main_window(self):
        """
        get the main window of this object
        """
        return self.__main_window

    @property
    def identity(self):
        """
        get the identity of this object
        """
        return self.__identity

    @property
    def flying_speed(self):
        """
        get flying speed
        """
        return self.__flying_speed

    @property
    def health(self):
        """
        get health
        """
        return self.__health

    @health.setter
    def health(self, value):
        self.__health = value

    def change_health_by(self, times):
        self.__health *= times

    def change_health_with(self, value):
        """
        change the health by a given value
        :param value: delta health
        """
        self.__health += value
        if self.__health <= 0:
            self.boom()
        elif self.__health > self.__max_health:
            self.max_health += (self.health-self.max_health)/2
            self.__health = self.__max_health

    @property
    def max_health(self):
        return self.__max_health

    @max_health.setter
    def max_health(self, value):
        self.__max_health = value

    @property
    def bullet_damage(self):
        """
        get damage
        """
        return self.__bullet_damage

    @bullet_damage.setter
    def bullet_damage(self, value):
        self.__bullet_damage = value

    def increase_damage_with(self, value):
        self.__bullet_damage += value

    @property
    def object_level(self):
        """
        get object's level
        """
        return self.__object_level

    def increase_object_level(self, level):
        """
        increase the level by a number
        :param level:
        :return:
        """
        self.__object_level += level

    @property
    def move_flag(self):
        """
        get the move flag
        """
        return self.__move_flag

    @move_flag.setter
    def move_flag(self, value):
        """
        set the move flag with the given value
        """
        self.__move_flag = value

    @property
    def attack_type(self):
        """
        getter of the attack type
        """
        return self.__attack_type

    @attack_type.setter
    def attack_type(self, value):
        """
        setter of the attack type
        :param value:
        :return:
        """
        self.__attack_type = value

    @property
    def attack_interval(self):
        return self.__attack_interval

    @attack_interval.setter
    def attack_interval(self, value):
        self.__attack_interval = value

    def attack(self):
        """
        method to start attack
        """
        self.attack_timer.start()

    def attack_method(self, attack_type):
        """
        helper of the attack method
        need to be extended by subclass
        """
        pass

    # TODO set buff class and enum
    def get_buff(self):
        """
        get buff
        not implemented
        :return:
        """
        pass

    def boom(self):
        """
            die method
        """
        self.move_flag = False
        self.put_blast_1()
        self.put_blast_2()
        self.del_itself()

    def put_blast_1(self):
        blast = Blast()

        self.add(blast, self.BLAST_START_1, self.BLAST_START_1)

    def put_blast_2(self):
        blast = Blast()
        self.add(blast, self.BLAST_START_2, self.BLAST_START_2)

    def del_itself(self):
        self.main_window.remove(self)
        del self

    def hit_others(self):
        """
        no implemented
        """
        pass


class Blast(GraphicLib.GImage):
    BLAST_IMAGE_PATH = "./resources/boom_64.png"

    def __init__(self):
        super().__init__(Blast.BLAST_IMAGE_PATH)


class BigJetPlane(FlyingObject):
    NORMAL_PROTECTOR_COLOR = GraphicLib.convertRGBToColor(0xf6aeae)
    NUCLEAR_PROTECTOR_COLOR = GraphicLib.convertRGBToColor(0xb5ec81)
    SHIELD_SIZE = 90

    HALF_WIDTH = 32
    HALF_HEIGHT = 32
    TEST_SIZE = 64
    BULLET_DAMAGE = 10
    LEVEL_UP_RANGE = (100, 150)  # lower, lower + 50
    next_score_range = range(*LEVEL_UP_RANGE)
    LEVEL_UP_SCALE = 2
    DETECT_RANGE = 50
    NB_RANGE = 10

    START_SHIELD_CYCLE_COUNT = 3

    def __init__(self, main_window: Graphics.CustomizedMainWindow):
        super().__init__(main_window, FlyingObjectIdentity.BIG_JET_PLANE,
                         flying_speed=0, appearance_file_path="./resources/big_jet_plane_64.png",
                         health=100, bullet_damage=self.BULLET_DAMAGE, attack_type=2,
                         object_level=1)

        self.protector = GraphicLib.GOval(self.SHIELD_SIZE, self.SHIELD_SIZE)
        self.protector.setColor(self.NORMAL_PROTECTOR_COLOR)
        self.protector.setLineWidth(5)

        self.__is_normal_shield_on = False
        self.__is_nuclear_shield_on = False

        self.__score = 0
        self.main_window.refill_health(self.max_health)

        self.__normal_shield_timer = None
        self.__nuclear_shield_timer = None
        self.nuclear_effect_timer = None

        self.__nuclear_boom_remaining = 1

        self.__normal_protector_time = 0
        self.__nuclear_protector_time = 0
        self.__nuclear_effect_cycle = 0

        self.attack()

        self.set_normal_shield_on(self.START_SHIELD_CYCLE_COUNT)

    def change_normal_protector_time(self, value):
        self.__normal_protector_time = value
        self.main_window.set_normal_protector_time(value)

    def change_normal_protector_time_with(self, delta):
        self.__normal_protector_time += delta
        self.main_window.set_normal_protector_time(self.__normal_protector_time)

    @property
    def is_normal_shield_on(self):
        return self.__is_normal_shield_on

    def set_normal_shield_on(self, cycle_count):
        if not self.__is_nuclear_shield_on:
            if not self.__is_normal_shield_on:
                self.change_normal_protector_time(cycle_count)
                self.__normal_shield_timer = self.main_window.setInterval(self.normal_shield_count, 1000)
                self.__is_normal_shield_on = True
                self.protector.setColor(self.NORMAL_PROTECTOR_COLOR)
                self.add(self.protector, -(self.SHIELD_SIZE - self.TEST_SIZE)/2, -(self.SHIELD_SIZE - self.TEST_SIZE)/2)
            else:
                self.change_normal_protector_time_with(cycle_count)
        else:
            self.update_score(3)

    def normal_shield_count(self):
        self.change_normal_protector_time_with(-1)

        if self.__normal_protector_time == 0:
            self.set_normal_shield_off()
            self.__normal_shield_timer.stop()

    def set_normal_shield_off(self):
        if self.__is_normal_shield_on:
            self.__is_normal_shield_on = False
            self.remove(self.protector)

    @property
    def is_nuclear_shield_on(self):
        return self.__is_nuclear_shield_on

    def change_nuclear_protector_time(self, value):
        self.__nuclear_protector_time = value
        self.main_window.set_nuclear_protector_time(value)

    def change_nuclear_protector_time_with(self, delta):
        self.__nuclear_protector_time += delta
        self.main_window.set_nuclear_protector_time(self.__nuclear_protector_time)

    def set_nuclear_shield_on(self, cycle_count):
        if not self.__is_normal_shield_on:
            if not self.__is_nuclear_shield_on:
                self.change_nuclear_protector_time(cycle_count)
                self.__nuclear_shield_timer = self.main_window.setInterval(self.nuclear_shield_count, 1000)
                self.__is_nuclear_shield_on = True
                self.protector.setColor(self.NUCLEAR_PROTECTOR_COLOR)
                self.add(self.protector, -(self.SHIELD_SIZE - self.TEST_SIZE)/2, -(self.SHIELD_SIZE - self.TEST_SIZE)/2)
            else:
                self.change_nuclear_protector_time_with(cycle_count)
        self.update_score(5)

    def nuclear_shield_count(self):
        self.change_nuclear_protector_time_with(-1)

        if self.__nuclear_protector_time == 0:
            self.set_nuclear_shield_off()
            self.__nuclear_shield_timer.stop()

    def set_nuclear_shield_off(self):
        if self.__is_nuclear_shield_on:
            self.__is_nuclear_shield_on = False
            self.remove(self.protector)

    @property
    def nuclear_boom_remaining(self):
        return self.__nuclear_boom_remaining

    def nuclear_boom_increase(self):
        self.__nuclear_boom_remaining += 1
        self.main_window.set_nuclear_boom_remaining_num(self.__nuclear_boom_remaining)

    def nuclear_boom_decrease(self):
        self.__nuclear_boom_remaining -= 1
        self.main_window.set_nuclear_boom_remaining_num(self.__nuclear_boom_remaining)

    @property
    def score(self):
        return self.__score

    def update_score(self, point):
        self.__score += point
        self.main_window.set_score(self.__score)
        if self.__score in self.next_score_range:
            if self.score < 400:
                lower = int((self.next_score_range.stop - self.DETECT_RANGE) * self.LEVEL_UP_SCALE)
                self.next_score_range = range(lower, lower + self.DETECT_RANGE)
            else:
                lower = (self.next_score_range.stop - self.DETECT_RANGE) + self.NB_RANGE
                self.next_score_range = range(lower, lower + self.DETECT_RANGE)
                self.nuclear_boom_increase()
            self.upgrade_level()

    def reset_score(self):
        self.__score = 0

    def increase_object_level(self, level):
        super().increase_object_level(level)
        self.main_window.set_level_label(self.object_level)

    def increase_damage_with(self, value):
        super().increase_damage_with(value)
        self.main_window.set_damage_label(self.bullet_damage)

    def upgrade_level(self, upgraded_level=1):
        self.increase_object_level(upgraded_level)
        self.increase_damage_with(10)
        self.level_to_health_conversion()
        self.get_harder()
        self.upgrade_bullet_num()

    def level_to_health_conversion(self):
        self.health += self.object_level * 50
        self.max_health = self.health
        self.main_window.refill_health(self.max_health)

    def get_harder(self):
        for cls in Enemy.__subclasses__():
            cls.level_up(self.main_window.big_jet_plane.object_level,
                         self.main_window.big_jet_plane.object_level,
                         1.1)

        self.main_window.set_half_exp_X(self.object_level - 1)

    def change_health_with(self, value):
        super().change_health_with(value)
        self.main_window.set_health_text(self.health)
        # print(self.health)
        if self.health == self.max_health:
            self.update_score(2)
        self.main_window.set_health_percentage(self.health / self.max_health)

    def upgrade_bullet_num(self):
        if self.attack_type == 5:
            self.increase_damage_with(5)
        else:
            self.attack_type += 1

    # TODO combine with text modifiers
    def move_flag_listener(self, e):
        if self.contains(e.getX(), e.getY()):
            self.move_flag = not self.move_flag
            if self.move_flag:
                self.move_to(e.getX(), e.getY())

    def move_listener(self, e: GraphicLib.GMouseEvent):
        if self.move_flag:
            self.move_to(e.getX(), e.getY())

    def move_to(self, x, y):
        self.move(x - self.getX() - BigJetPlane.HALF_WIDTH, y - self.getY() - BigJetPlane.HALF_HEIGHT)

    def attack_method(self, attack_type):  # TODO change the start position of the bullets
        if self.move_flag:
            bullet = Bullet.NMG(self.bullet_damage, self.main_window, self.attack_type)
            self.main_window.add(bullet, self.getX() + bullet.com_width, self.getY()-bullet.getHeight())
            bullet.move_animation()

    def nuclear_effect(self):
        self.__nuclear_effect_cycle -= 1
        if self.__nuclear_effect_cycle == 0:
            self.nuclear_effect_timer.stop()
        else:
            if not self.is_nuclear_shield_on:
                self.change_health_with(-0.1)

    def nuclear_boom_attack(self):
        if self.__nuclear_boom_remaining > 0:
            self.nuclear_boom_decrease()
            self.__nuclear_effect_cycle = 350
            self.nuclear_effect_timer = self.main_window.setInterval(self.nuclear_effect, 15)  # 8.5S radioactive effect
            for ele in self.main_window.base.contents:
                if issubclass(ele.__class__, Enemy):
                    ele.boom()

    def shield_timer_end(self):
        self.__nuclear_shield_timer.stop()
        self.__normal_shield_timer.stop()
        self.change_nuclear_protector_time(0)
        self.change_normal_protector_time(0)

    def boom(self):
        super().boom()
        self.main_window.end()

    def bullet_num_increase_buff(self):
        self.upgrade_bullet_num()

    def add_protector_buff(self):
        self.set_normal_shield_on(10)

    def add_nuclear_protector_buff(self):
        self.set_nuclear_shield_on(10)

    def add_health_buff(self):
        self.change_health_with(20 * self.object_level)


class Enemy(FlyingObject):
    SPEED = 3
    speed = SPEED
    MOVE_DELAY = 10

    BULLET_DAMAGE = 10
    enemy_bullet_damage = BULLET_DAMAGE

    HEALTH = 30.0
    health = HEALTH

    WORTH_EXP = 10
    worth_exp = WORTH_EXP

    BULLET_NUMBER = 1
    bullet_number = BULLET_NUMBER

    ENEMY_LEVEL = 0
    enemy_level = ENEMY_LEVEL

    IMAGE_PATH = None
    DAMAGE_SCALE = 1.5
    HEALTH_SCALE = 1.9
    ATTACK_INTERVAL = 600

    def __init__(self, main_window, attack_type):
        pass
        super().__init__(main_window, FlyingObjectKind.ENEMY,
                         flying_speed=0, appearance_file_path=self.IMAGE_PATH,
                         health=self.health, bullet_damage=1E+10, attack_type=attack_type,
                         object_level=1, attack_interval=self.ATTACK_INTERVAL)

        self.move_timer = self.main_window.set_interval_with_param(self.move_to, self.MOVE_DELAY, ())
        self.buff = self.generate_buff()

        self.move_animation()
        self.attack()

    def generate_buff(self):
        # TODO change the probability of buff drop
        indicator = random.random()
        if 0 <= indicator < 1/4:
            return Buffs.BuffBase.add_health_buff_factory(self.main_window, BigJetPlane)
        elif 1/4 <= indicator < 5/12:
            return Buffs.BuffBase.add_protector_buff_factory(self.main_window, BigJetPlane)
        elif 26/36 <= indicator < 8/9:
            return Buffs.BuffBase.add_nuclear_protector_buff_factory(self.main_window, BigJetPlane)
        elif 8/9 <= indicator < 1:
            return Buffs.BuffBase.add_bullet_buff_factory(self.main_window, BigJetPlane)

    def attack_method(self, attack_type):
        if self.move_flag and self.main_window.start_flag:
            attack_type = attack_type(self.main_window, self.bullet_number, self.enemy_bullet_damage)
            self.main_window.add(attack_type, self.getX() + attack_type.com_width, self.getY() + attack_type.com_height)
            attack_type.move_animation()
        elif not self.main_window.start_flag:
            self.attack_timer.stop()

    def move_animation(self):
        self.move_timer.start()
        self.move_flag = True

    def remove_process(self):
        self.main_window.remove(self)
        self.main_window.decrease_enemy_on_board()
        self.main_window.interval_list.pop(self)

    def move_to(self):
        if self.move_flag and self.main_window.start_flag:
            if self.getY() >= Graphics.WINDOW_HEIGHT:
                self.move_timer.stop()
                self.move_flag = False
                self.remove_process()
                del self
            else:
                self.move(0, self.speed)

    def boom(self):
        self.drop_buff()
        self.remove_process()
        if self.main_window.big_jet_plane is not None:
            self.main_window.big_jet_plane.update_score(self.worth_exp)

        super().boom()

    @classmethod
    def subtract_exp(cls):
        if cls.worth_exp >= 10:
            cls.worth_exp //= 2

    @classmethod
    def reset_worth_point(cls):
        cls.worth_exp = cls.WORTH_EXP

    @classmethod
    def increase_damage_by(cls, value):
        cls.enemy_bullet_damage *= value

    @classmethod
    def reset_damage(cls):
        cls.enemy_bullet_damage = cls.BULLET_DAMAGE

    @classmethod
    def increase_bullet_num(cls):
        if cls.enemy_level % 2 == 0 and cls.bullet_number < 2:
            cls.bullet_number += 1

    @classmethod
    def reset_bullet_num(cls):
        cls.bullet_number = cls.BULLET_NUMBER

    @classmethod
    def increase_health_by(cls, times):
        cls.health *= times

    @classmethod
    def reset_health(cls):
        cls.health = cls.HEALTH

    @classmethod
    def change_speed_by(cls, times):
        cls.speed *= times

    @classmethod
    def reset_speed(cls):
        cls.speed = cls.SPEED

    @classmethod
    def increase_enemy_level(cls):
        cls.enemy_level += 1

    @classmethod
    def reset_enemy_level(cls):
        cls.enemy_level = cls.ENEMY_LEVEL

    @classmethod
    def level_up(cls, damage_delta_value, health_times, speed_times):
        cls.increase_enemy_level()
        cls.subtract_exp()
        cls.increase_damage_by(damage_delta_value)
        cls.increase_bullet_num()
        cls.increase_health_by(health_times)
        cls.change_speed_by(speed_times)

    @classmethod
    def reset_property(cls):
        cls.reset_enemy_level()
        cls.reset_worth_point()
        cls.reset_damage()
        cls.reset_health()
        cls.reset_speed()
        cls.reset_bullet_num()

    def drop_buff(self):
        center = (self.getX() + BigJetPlane.TEST_SIZE/2, self.getY() + BigJetPlane.TEST_SIZE/2)
        if self.buff is not None:
            self.main_window.add(self.buff, *center)
            self.buff.sendToBack()
            self.buff.animation()


class Swift(Enemy):
    MOVE_DELAY = 10
    speed = SPEED = 4
    enemy_bullet_damage = BULLET_DAMAGE = 10
    health = HEALTH = 30.0
    worth_exp = WORTH_EXP = 10
    bullet_number = BULLET_NUMBER = 1
    ATTACK_INTERVAL = 400 + 100
    IMAGE_PATH = "./resources/swift_64.png"

    def __init__(self, main_window):
        super().__init__(main_window, Bullet.BulletIdentity.LIGHT_BALL.cls)


class Normal(Enemy):
    MOVE_DELAY = 10
    speed = SPEED = 3
    enemy_bullet_damage = BULLET_DAMAGE = 7
    health = HEALTH = 60
    worth_exp = WORTH_EXP = 20
    bullet_number = BULLET_NUMBER = 1
    ATTACK_INTERVAL = 600 + 100
    IMAGE_PATH = "./resources/normal_64.png"

    def __init__(self, main_window):
        super().__init__(main_window, Bullet.BulletIdentity.LIGHT_BALL.cls)


class Huge(Enemy):
    MOVE_DELAY = 10
    speed = SPEED = 2
    enemy_bullet_damage = BULLET_DAMAGE = 11
    health = HEALTH = 150
    worth_exp = WORTH_EXP = 30
    bullet_number = BULLET_NUMBER = 2
    ATTACK_INTERVAL = 700 + 100
    IMAGE_PATH = "./resources/huge_64.png"

    def __init__(self, main_window):
        super().__init__(main_window, Bullet.BulletIdentity.LIGHT_BALL.cls)

    def remove_process(self):
        self.main_window.switch_huge_on()
        super().remove_process()

    def boom(self):
        super().boom()


class Boss(Enemy):
    MOVE_DELAY = 10
    speed = SPEED = 2
    enemy_bullet_damage = BULLET_DAMAGE = 15
    health = HEALTH = 200
    worth_exp = WORTH_EXP = 30
    bullet_number = BULLET_NUMBER = 2
    ATTACK_INTERVAL = 750 + 100
    IMAGE_PATH = "./resources/boss_64.png"

    def __init__(self, main_window):
        super().__init__(main_window, Bullet.BulletIdentity.LIGHT_BALL.cls)

    def remove_process(self):
        self.main_window.switch_boss_on()
        super().remove_process()

    def boom(self):
        super().boom()


class FlyingObjectIdentity(enum.Enum):
    BIG_JET_PLANE = FlyingObjectKind.SELF, BigJetPlane
    SWIFT = FlyingObjectKind.ENEMY, Swift
    NORMAL = FlyingObjectKind.ENEMY, Normal
    HUGE = FlyingObjectKind.ENEMY, Huge
    BOSS = FlyingObjectKind.ENEMY, Boss

    def __init__(self, kind, cls):
        self.__kind = kind
        self.__cls = cls

    @property
    def kind(self):
        return self.__kind

    @property
    def cls(self):
        return self.__cls
