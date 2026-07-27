import dearpygui.dearpygui as dpg

import math

from .camera import Camera
from .visual_book import VisualBook


class Scene:
    def __init__(self, scale, **vb_kwargs):
        self._width = 500
        self._height = 500

        self.camera = Camera(scale=scale)
        self.visual_book = VisualBook(scale=scale, **vb_kwargs)
    
    def set_clip_space(self, width, height):
        self._width = width
        self._height = height
        if dpg.does_item_exist("drawlayer_3d"):
            dpg.set_clip_space("drawlayer_3d", 0, 0, width, height, -1.0, 1.0)

    def update(self):
        rot = self.camera.get_radian_angles()
        
        model_matrix = (dpg.create_rotation_matrix(rot[0], [1, 0, 0]) *
                        dpg.create_rotation_matrix(rot[1], [0, 1, 0]) *
                        dpg.create_rotation_matrix(rot[2], [0, 0, 1]))
        
        camera_position = self.camera.get_position()
        target_position = self.camera.get_target_pos()
        
        view_matrix = dpg.create_lookat_matrix(
            [*camera_position],
            [*target_position],
            [0, 1, 0]
        )
        
        proj_matrix = dpg.create_perspective_matrix(
            math.pi * 45.0 / 180.0, self._width/self._height, 0.1, 100)
        
        if dpg.does_item_exist("plane_node"):
            transform_matrix = proj_matrix * view_matrix * model_matrix
            dpg.apply_transform("plane_node", transform_matrix)