from .camera import Camera

class Scene:
    def __init__(self):
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0

        self.camera = Camera()