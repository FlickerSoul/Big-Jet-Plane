import pgl as GraphicLib



class BuffBase(GraphicLib.GOval):
    DIAMETER = 10
    RADIUS = DIAMETER / 2

    def __init__(self, main_window, method):
        super().__init__(self.DIAMETER, self.DIAMETER)
        self.main_window = main_window
        self.buff_method = method

    def move_motion(self):
        pass

    def move_to(self):
        pass

    def is_hit(self):
        pass

    import Components
    @staticmethod
    def add_bullet_buff_factory(main_window, entity: Components.BigJetPlane):
        return BuffBase(main_window, entity.bullet_num_increase_buff)

    @staticmethod
    def add_protector_buff_factory(main_window, entity: Components.BigJetPlane):
        return BuffBase(main_window, entity.add_protector_buff)

    @staticmethod
    def add_NB_protector_buff_factory(main_window, entity: Components.BigJetPlane):
        return BuffBase(main_window, entity.add_NB_protector_buff)

    @staticmethod
    def add_health_buff_factory(main_window, entity: Components.BigJetPlane):
        return BuffBase(main_window, entity.add_health_buff)
