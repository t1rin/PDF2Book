import os
import dearpygui.dearpygui as dpg

import ui.config as conf

global_font_path = "./assets/fonts/DeleddaOpen.ttf"
if not os.path.exists(global_font_path):
    print(f"Warning: Font file not found: {global_font_path}")

def register_theme(name):
    with dpg.font_registry():
        with dpg.font(global_font_path, size=14, tag="global_font"): pass

    with dpg.theme(tag="global_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)
            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 6, 3)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 10)
            dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 8, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 14)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 10)
            dpg.add_theme_style(dpg.mvStyleVar_SeparatorTextBorderSize, 2)
            dpg.add_theme_style(dpg.mvStyleVar_SeparatorTextAlign, 0.5, 0.5)
            dpg.add_theme_style(dpg.mvStyleVar_SeparatorTextPadding, 0, 0)
            dpg.add_theme_style(dpg.mvStyleVar_TabBarBorderSize, 0)

            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, conf.theme[name]["window_color"])
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, conf.theme[name]["bg_color"])
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, conf.theme[name]["bg_color"])
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, conf.theme[name]["bg_color"])
            
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, conf.theme[name]["widget_color"])
            dpg.add_theme_color(dpg.mvThemeCol_Button, conf.theme[name]["widget_color"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, conf.theme[name]["widget_color"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, conf.theme[name]["widget_color"])
            dpg.add_theme_color(dpg.mvThemeCol_Tab, conf.theme[name]["widget_color"])
            
            dpg.add_theme_color(dpg.mvThemeCol_Text, conf.theme[name]["text_color"])
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, conf.theme[name]["text_disabled_color"])
            
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, conf.theme[name]["hovered_color"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, conf.theme[name]["hovered_color"])
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, conf.theme[name]["hovered_color"])
            
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, conf.theme[name]["selected_color"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, conf.theme[name]["selected_color"])
            dpg.add_theme_color(dpg.mvThemeCol_TabSelected, conf.theme[name]["selected_color"])
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, conf.theme[name]["selected_color"])
            
            dpg.add_theme_color(dpg.mvThemeCol_Separator, conf.theme[name]["border_color"])
            dpg.add_theme_color(dpg.mvThemeCol_Border, conf.theme[name]["border_color"])
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, conf.theme[name]["border_color"])
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, conf.theme[name]["border_color"])
  
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, conf.theme[name]["bg_color"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, conf.theme[name]["widget_color"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, conf.theme[name]["hovered_color"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, conf.theme[name]["selected_color"])

        with dpg.theme_component(dpg.mvTab):
            dpg.add_theme_style(dpg.mvStyleVar_TabBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 0)

        with dpg.theme_component(dpg.mvTable):
            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 1, 0)
            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, conf.theme[name]["widget_color"])

        with dpg.theme_component(dpg.mvPlot):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, conf.theme[name]["bg_color"])
            dpg.add_theme_color(dpg.mvPlotCol_Selection, conf.theme[name]["plot_selection_color"])
    
def switch_theme(name):
    if dpg.does_item_exist("global_theme"):
        dpg.delete_item("global_theme")
    
    if dpg.does_item_exist("global_font"):
        dpg.delete_item("global_font")
    
    register_theme(name)
    
    dpg.bind_theme("global_theme")
    dpg.bind_font("global_font")
    
    dpg.split_frame()

"""
def key_callback():
    themes = list(conf.theme.keys())
    new_theme = themes[themes.index(conf.selected_theme)-1]
    switch_theme(new_theme)

def register_keyboards():
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_F1, callback=key_callback)"""

def apply_theme():
    register_theme(conf.selected_theme)
    #register_keyboards()
    dpg.bind_theme("global_theme")
    dpg.bind_font("global_font")