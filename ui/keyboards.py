from __future__ import annotations
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

import ui.callbacks as cb

if TYPE_CHECKING:
    from main import PDF2BookApp


def switch_theme(app: PDF2BookApp) -> None:
    cb.switch_theme(app)


def switch_font(app: PDF2BookApp) -> None:
    cb.switch_font(app)


def move_panel(app: PDF2BookApp) -> None:
    cb.move_panel(app)


def switch_mode(app: PDF2BookApp, mode: str) -> None:
    cb.switch_mode(app, mode)


def open_file(app: PDF2BookApp) -> None:
    if dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
        cb.open_file(app)


def save_file(app: PDF2BookApp) -> None:
    if (dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)) and \
        dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift):
        cb.save_as_file(app)
    elif dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
        cb.save_file(app)                                                     


def back_page(app: PDF2BookApp) -> None:
    cb.arrow_left_callback(app)


def next_page(app: PDF2BookApp) -> None:
    cb.arrow_right_callback(app)

def register_keyboards(app: PDF2BookApp) -> None:
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_F1, 
                                  callback=lambda: switch_mode(app,"preview"))
        dpg.add_key_press_handler(dpg.mvKey_F2, 
                                  callback=lambda: switch_mode(app, "visualization"))
        dpg.add_key_press_handler(dpg.mvKey_F3, callback=lambda: switch_theme(app))
        dpg.add_key_press_handler(dpg.mvKey_F4, callback=lambda: switch_font(app))
        dpg.add_key_press_handler(dpg.mvKey_F5, callback=lambda: move_panel(app))
        dpg.add_key_press_handler(dpg.mvKey_O, callback=lambda: open_file(app))
        dpg.add_key_press_handler(dpg.mvKey_S, callback=lambda: save_file(app))
        dpg.add_key_press_handler(dpg.mvKey_Left, callback=lambda: back_page(app))
        dpg.add_key_press_handler(dpg.mvKey_Right, callback=lambda: next_page(app))
