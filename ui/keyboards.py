import dearpygui.dearpygui as dpg

import ui.callbacks as cb


def switch_theme(app):
    cb.switch_theme(app)

def switch_font(app):
    cb.switch_font(app)

def open_file(app):
    if dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
        cb.open_file(app)

def save_file(app):
    if (dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)) and \
        dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift):
        cb.save_as_file(app)
    elif dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
        cb.save_file(app)                                                     

def back_page(app):
    cb.arrow_left_callback(app)

def next_page(app):
    cb.arrow_right_callback(app)

def register_keyboards(app):
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_F1, callback=lambda: switch_theme(app))
        dpg.add_key_press_handler(dpg.mvKey_F2, callback=lambda: switch_font(app))
        dpg.add_key_press_handler(dpg.mvKey_O, callback=lambda: open_file(app))
        dpg.add_key_press_handler(dpg.mvKey_S, callback=lambda: save_file(app))
        dpg.add_key_press_handler(dpg.mvKey_Left, callback=lambda: back_page(app))
        dpg.add_key_press_handler(dpg.mvKey_Right, callback=lambda: next_page(app))