import dearpygui.dearpygui as dpg

import math

from .geometry import get_scale_multiplier


_is_dragging = False
_is_panning = False
_last_mouse_pos = [0, 0]


def _is_mouse_over_drawlist(app):
    if not dpg.does_item_exist("drawlist_3d"):
        return False
    if not dpg.is_item_shown("drawlist_window"):
        return False
    pos = dpg.get_item_pos("drawlist_3d")
    size = dpg.get_item_rect_size("drawlist_3d")
    point0, point1 = pos, [pos[0]+size[0], pos[1]+size[1]]
    mouse_pos = dpg.get_mouse_pos()
    if not (point0[0] < mouse_pos[0] < point1[0] and 
        point0[1] < mouse_pos[1] < point1[1]):
        return False
    return True

def mouse_click_callback(app):
    if not _is_mouse_over_drawlist(app):
        return
    global _is_dragging, _last_mouse_pos
    _is_dragging = True
    _last_mouse_pos = dpg.get_mouse_pos()
    
def mouse_release_callback(app):
    global _is_dragging, _is_panning
    _is_dragging = False
    _is_panning = False

def mouse_move_callback(app):
    if not _is_mouse_over_drawlist(app):
        return
    
    global _is_dragging, _is_panning, _last_mouse_pos
    
    if _is_dragging:
        dx = -(dpg.get_mouse_pos()[0] - _last_mouse_pos[0])
        dy = dpg.get_mouse_pos()[1] - _last_mouse_pos[1]
        
        app.scene.camera.yaw += dx * 0.01
        app.scene.camera.pitch += dy * 0.01
        app.scene.camera.pitch = max(-math.pi/2 + 0.01, 
            min(math.pi/2 - 0.01, app.scene.camera.pitch))
        
        _last_mouse_pos = dpg.get_mouse_pos()
        app.scene.update()
    
    elif _is_panning:
        right, up = app.scene.camera.get_camera_vectors()
        
        dx = -(dpg.get_mouse_pos()[0] - _last_mouse_pos[0])
        dy = dpg.get_mouse_pos()[1] - _last_mouse_pos[1]
        
        scale = app.scene.camera.distance * 0.001
        
        app.scene.camera.target_x += (right[0] * dx + up[0] * dy) * scale
        app.scene.camera.target_y += (right[1] * dx + up[1] * dy) * scale
        app.scene.camera.target_z += (right[2] * dx + up[2] * dy) * scale
        
        _last_mouse_pos = dpg.get_mouse_pos()
        app.scene.update()

def mouse_wheel_callback(app, sign):
    if not _is_mouse_over_drawlist(app):
        return
    
    min_d = app.scene.camera.min_distance
    max_d = app.scene.camera.max_distance
    app.scene.camera.distance -= sign * get_scale_multiplier(app.scene.camera.distance)
    app.scene.camera.distance = max(min_d, min(max_d, app.scene.camera.distance))
    app.scene.update()

def mouse_middle_click_callback(app):
    if not _is_mouse_over_drawlist(app):
        return
    
    global _is_panning, _last_mouse_pos
    _is_panning = True
    _last_mouse_pos = dpg.get_mouse_pos()

def register_mouse_handlers(app):
    with dpg.handler_registry():
        dpg.add_mouse_click_handler(dpg.mvMouseButton_Left, callback=lambda: mouse_click_callback(app))
        dpg.add_mouse_click_handler(dpg.mvMouseButton_Middle, callback=lambda: mouse_middle_click_callback(app))
        dpg.add_mouse_release_handler(dpg.mvMouseButton_Left, callback=lambda: mouse_release_callback(app))
        dpg.add_mouse_release_handler(dpg.mvMouseButton_Middle, callback=lambda: mouse_release_callback(app))
        dpg.add_mouse_move_handler(callback=lambda: mouse_move_callback(app))
        dpg.add_mouse_wheel_handler(callback=lambda _, data: mouse_wheel_callback(app, data))