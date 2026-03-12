from .world_state import WorldSystem


class Pipeline:

    def __init__(self):

        self.world = WorldSystem()
        self.data = {}

    def tick(self):

        self.world.tick()

    def export(self):

        data = {}

        data.update(self.world.export())

        self.data = data

        return data
