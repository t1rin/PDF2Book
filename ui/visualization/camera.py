import numpy as np

import math


class Camera:
    def __init__(self):
        self.distance = 20.0
        self.yaw = 0.0
        self.pitch = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 0.0
