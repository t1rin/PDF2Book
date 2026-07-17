import dearpygui.dearpygui as dpg

import math

from .camera import Camera
from .core import VisualBook
from ..config import conf


class Scene:
    def __init__(self):
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0

        self._width = 500
        self._height = 500

        self.camera = Camera()
        self.visual_book = VisualBook()
    
    def set_clip_space(self, width, height):
        self._width = width
        self._height = height
        if dpg.does_item_exist("drawlayer_3d"):
            dpg.set_clip_space("drawlayer_3d", 0, 0, width, height, -1.0, 1.0)

    def clear(self):
        if dpg.does_item_exist("drawlist_window"):
            children = dpg.get_item_children("drawlist_window")
            
            if children and len(children) > 1:
                for child in children[1]:
                    dpg.delete_item(child)
            
        with dpg.group(parent="drawlist_window", pos=[conf.padding_drawlist, 
                                                      conf.padding_drawlist]):
            with dpg.drawlist(width=-1, height=-1, tag="drawlist_3d"):
                with dpg.draw_layer(depth_clipping=False, cull_mode=dpg.mvCullMode_Back, 
                                    perspective_divide=True, tag="drawlayer_3d"):
                    with dpg.draw_node(tag="plane_node"):
                        dpg.draw_line([0, 0, 0], [3, 0, 0], 
                                      color=[255, 0, 0, 255], 
                                      thickness=3)
                        dpg.draw_line([0, 0, 0], [0, 3, 0], 
                                      color=[0, 255, 0, 255], 
                                      thickness=3)
                        dpg.draw_line([0, 0, 0], [0, 0, 3], 
                                      color=[0, 0, 255, 255], 
                                      thickness=3)

    def update(self):
        rot_x = self.rot_x * math.pi / 180.0
        rot_y = self.rot_y * math.pi / 180.0
        rot_z = self.rot_z * math.pi / 180.0
        
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