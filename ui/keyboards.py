import glob
import dearpygui.dearpygui as dpg

from ui.themes import update_theme
from ui.config import conf
import ui.callbacks as cb


def switch_theme(app):
    themes = list(conf.theme.keys())
    app.theme = themes[themes.index(app.theme)-1]
    update_theme(app)

def switch_font(app):
    fonts = glob.glob("./assets/fonts/*.ttf")
    app.font = fonts[fonts.index(app.font)-1]
    update_theme(app)

def open_file(app):
    if dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
        cb.open_file(app)

def save_file(app):
    if (dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)) and \
        dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift):
        cb.save_as_file_btn(app)
    elif dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
        cb.save_file_btn(app)                                                     

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