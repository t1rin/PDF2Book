import numpy as np

import math


class Camera:
    def __init__(self):
        self.distance = 25.0
        self.yaw = math.pi / 4
        self.pitch = math.pi / 6
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 0.0

    def get_camera_vectors(self):
        forward = np.array([
            -math.cos(self.pitch) * math.sin(self.yaw),
            -math.sin(self.pitch),
            -math.cos(self.pitch) * math.cos(self.yaw)
        ])
        
        world_up = np.array([0, 1, 0])
        
        right = np.cross(forward, world_up)
        right = right / np.linalg.norm(right)
        
        up = np.cross(right, forward)
        up = up / np.linalg.norm(up)
        
        return right, up
