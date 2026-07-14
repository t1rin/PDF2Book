import dearpygui.dearpygui as dpg

import math


_is_dragging = False
_is_panning = False
_last_mouse_pos = [0, 0]

def _is_mouse_over_drawlist():
    ...

def mouse_click_callback(app):
    global _is_dragging, _last_mouse_pos
    _is_dragging = True
    _last_mouse_pos = dpg.get_mouse_pos()
    
def mouse_release_callback(app):
    global _is_dragging, _is_panning
    _is_dragging = False
    _is_panning = False

def mouse_move_callback(app):
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

def mouse_wheel_callback(app, data):
    app.scene.camera.distance -= data * 2
    app.scene.camera.distance = max(5.0, min(50.0, app.scene.camera.distance))
    app.scene.update()

def mouse_middle_click_callback(app):
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