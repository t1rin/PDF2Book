from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

import math

from .geometry import get_scale_multiplier

if TYPE_CHECKING:
    from main import PDF2BookApp


class Camera:
    def __init__(self, app: PDF2BookApp) -> None:
        self.app: PDF2BookApp = app
        self._min_distance: float = 10.0
        self._max_distance: float = 20000.0
        
        self.home()

    def home(self) -> None:
        zoom = self.app.conf.dpi / 72
        self._distance: float = zoom * 3500.0
        self._yaw: float = math.pi / 4
        self._pitch: float = math.pi / 6
        self._target_x: float = 0.0
        self._target_y: float = 0.0
        self._target_z: float = 0.0
        self._rot_x: float = 0.0
        self._rot_y: float = 0.0
        self._rot_z: float = 0.0
    
    def update_camera_rotation(self, dx: int, dy: int) -> None:
        self._yaw += dx * 0.01
        self._pitch += dy * 0.01
        self._pitch = max(
            -math.pi / 2 + 0.01,
            min(math.pi / 2 - 0.01, self._pitch)
        )
        
    def update_camera_pan(self, dx: int, dy: int) -> None:
        right, up = self.get_camera_vectors()
        scale = self._distance * 0.001
        
        self._target_x += (right[0] * dx + up[0] * dy) * scale
        self._target_y += (right[1] * dx + up[1] * dy) * scale
        self._target_z += (right[2] * dx + up[2] * dy) * scale

    def update_camera_zoom(self, sign: int) -> None:
        self._distance -= sign * get_scale_multiplier(self._distance)
        self._distance = max(
            self._min_distance, 
            min(self._max_distance, self._distance)
        )
    
    def get_camera_vectors(self) -> tuple:
        forward = np.array([
            -math.cos(self._pitch) * math.sin(self._yaw),
            -math.sin(self._pitch),
            -math.cos(self._pitch) * math.cos(self._yaw)
        ])
        
        world_up = np.array([0, 1, 0])
        
        right = np.cross(forward, world_up)
        right = right / np.linalg.norm(right)
        
        up = np.cross(right, forward)
        up = up / np.linalg.norm(up)
        
        return right, up

    def get_position(self) -> NDArray:
        cam_x = (self._distance * math.cos(self._pitch) * math.sin(self._yaw) + 
                 self._target_x)
        cam_y = (self._distance * math.sin(self._pitch) + 
                 self._target_y)
        cam_z = (self._distance * math.cos(self._pitch) * math.cos(self._yaw) + 
                 self._target_z)
        return np.array([cam_x, cam_y, cam_z])
    
    def get_radian_angles(self) -> NDArray:
        _rot_x = self._rot_x * math.pi / 180.0
        _rot_y = self._rot_y * math.pi / 180.0
        _rot_z = self._rot_z * math.pi / 180.0
        return np.array([_rot_x, _rot_y, _rot_z])

    def get_target_pos(self) -> NDArray:
        return np.array(
            [self._target_x, self._target_y, self._target_z]
        )
