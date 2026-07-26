import dearpygui.dearpygui as dpg

import math

import ui.callbacks as cb


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
    return (point0[0] < mouse_pos[0] < point1[0] and
            point0[1] < mouse_pos[1] < point1[1])

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
    
    if _is_dragging or _is_panning:
        camera_pos = app.scene.camera.get_position()
        if app.scene.visual_book.is_order_changed(camera_pos):
            cb.update(app)

        if _is_dragging:
            dx = -(dpg.get_mouse_pos()[0] - _last_mouse_pos[0])
            dy = dpg.get_mouse_pos()[1] - _last_mouse_pos[1]
            _last_mouse_pos = dpg.get_mouse_pos()
            
            app.scene.camera.update_camera_rotation(dx, dy)
            app.scene.update()

        else:
            dx = -(dpg.get_mouse_pos()[0] - _last_mouse_pos[0])
            dy = dpg.get_mouse_pos()[1] - _last_mouse_pos[1]
            _last_mouse_pos = dpg.get_mouse_pos()
            
            app.scene.camera.update_camera_pan(dx, dy)     
            app.scene.update()

def mouse_wheel_callback(app, sign):
    if not _is_mouse_over_drawlist(app):
        return
    
    app.scene.camera.update_camera_zoom(sign)
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