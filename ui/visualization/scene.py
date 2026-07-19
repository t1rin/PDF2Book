import dearpygui.dearpygui as dpg

import math

from .camera import Camera
from .visual_book import VisualBook
from ..config import conf


class Scene:
    def __init__(self):
        self._width = 500
        self._height = 500
        self._axis_size = 5

        self.camera = Camera()
        self.visual_book = VisualBook()
    
    def set_clip_space(self, width, height):
        self._width = width
        self._height = height
        if dpg.does_item_exist("drawlayer_3d"):
            dpg.set_clip_space("drawlayer_3d", 0, 0, width, height, -1.0, 1.0)

    def update(self):
        rot_x = self.camera.rot_x * math.pi / 180.0
        rot_y = self.camera.rot_y * math.pi / 180.0
        rot_z = self.camera.rot_z * math.pi / 180.0
        
        model_matrix = (dpg.create_rotation_matrix(rot_x, [1, 0, 0]) *
                        dpg.create_rotation_matrix(rot_y, [0, 1, 0]) *
                        dpg.create_rotation_matrix(rot_z, [0, 0, 1]))
        
        cam_x = self.camera.distance * math.cos(self.camera.pitch) * math.sin(self.camera.yaw) + self.camera.target_x
        cam_y = self.camera.distance * math.sin(self.camera.pitch) + self.camera.target_y
        cam_z = self.camera.distance * math.cos(self.camera.pitch) * math.cos(self.camera.yaw) + self.camera.target_z
        
        view_matrix = dpg.create_lookat_matrix(
            [cam_x, cam_y, cam_z],
            [self.camera.target_x, self.camera.target_y, self.camera.target_z],
            [0, 1, 0]
        )
        
        proj_matrix = dpg.create_perspective_matrix(math.pi * 45.0 / 180.0, self._width/self._height, 0.1, 100)
        
        if dpg.does_item_exist("plane_node"):
            dpg.apply_transform("plane_node", proj_matrix * view_matrix * model_matrix)