import pgl as GraphicLib

class BuffBase(GraphicLib.GCompound):
    DIAMETER = 20
    RADIUS = DIAMETER / 2
    STAGE_COUNT = 6
    REFRESH_RATE = 15

    STAGE_1 = GraphicLib.convertRGBToColor(0x75C38A)
    STAGE_2 = GraphicLib.convertRGBToColor(0xB5D16D)
    STAGE_3 = GraphicLib.convertRGBToColor(0xF7C443)
    STAGE_4 = GraphicLib.convertRGBToColor(0xED6242)
    STAGE_5 = GraphicLib.convertRGBToColor(0xB7263D)
    FINAL_STAGE = GraphicLib.convertRGBToColor(0xFFFFFF)

    COLOR_STAGE = {1: STAGE_1, 2: STAGE_2, 3: STAGE_3, 4: STAGE_4, 5: STAGE_5, 6: FINAL_STAGE}

    def __init__(self, main_window, method, name, stage_time=1000):
        super().__init__()

        self.under = GraphicLib.GOval(self.DIAMETER, self.DIAMETER)
        self.under.setFilled(True)
        self.under.setColor(self.STAGE_2)

        self.upper = GraphicLib.GArc(self.DIAMETER+1, self.DIAMETER+1, 90, 360)
        self.upper.setFilled(True)
        self.upper.setColor(self.STAGE_2)

        self.text_indicator = GraphicLib.GLabel(name)
        self.text_indicator.setColor("white")

        self.add(self.under)
        self.add(self.upper)
        self.add(self.text_indicator, self.RADIUS/2, self.RADIUS * 1.7)

        self.main_window = main_window
        self.buff_method = method
        self.stage_time = stage_time
        self.loop_times = stage_time // self.REFRESH_RATE
        self.sweep_angel_delta = 360 / self.loop_times
        self.CENTER_POINT = None

        self.current_stage = 1
        self.current_loop = 0
        self.spin_clock = None

    def animation(self):
        self.animation_helper()
        self.sendBackward()

    def spin(self):
        self.is_hit()
        if self.current_loop > self.loop_times:
            self.spin_clock.stop()
            self.current_loop = 0
            self.animation_helper()
        else:
            self.upper.setSweepAngle(self.upper.getSweepAngle() - self.sweep_angel_delta)
            self.current_loop += 1

    def animation_helper(self):
        if self.current_stage == BuffBase.STAGE_COUNT:
            self.main_window.remove(self)
            del self
        else:
            self.CENTER_POINT = (self.getX() + self.RADIUS, self.getY() + self.RADIUS)
            self.upper.setColor(BuffBase.COLOR_STAGE[self.current_stage])
            self.upper.setSweepAngle(359)
            self.under.setColor(BuffBase.COLOR_STAGE[self.current_stage + 1])

            self.spin_clock = self.main_window.setInterval(self.spin, self.REFRESH_RATE)

            self.current_stage += 1

    def is_hit(self):
        import Components
        eles = self.main_window.get_elements_at(*self.CENTER_POINT)
        if len(eles) > 1:
            for ele in eles:
                if issubclass(ele.__class__, Components.BigJetPlane):
                    self.buff_method(ele)
                    self.main_window.remove(self)
                    # del self

    @staticmethod
    def add_bullet_buff_factory(main_window, entity):
        return BuffBase(main_window, entity.bullet_num_increase_buff, "B")

    @staticmethod
    def add_protector_buff_factory(main_window, entity):
        return BuffBase(main_window, entity.add_protector_buff, "P")

    @staticmethod
    def add_nuclear_protector_buff_factory(main_window, entity):
        return BuffBase(main_window, entity.add_nuclear_protector_buff, "N")

    @staticmethod
    def add_health_buff_factory(main_window, entity):
        return BuffBase(main_window, entity.add_health_buff, "H")


if __name__ == "__main__":
    import Components
    gw = GraphicLib.GWindow(600, 400)
    buff = BuffBase.add_health_buff_factory(gw, Components.BigJetPlane)
    gw.add(buff, 300, 200)
    buff.animation()
