import os
import dearpygui.dearpygui as dpg

from ui.widgets import create_main_window
from ui.callbacks import register_callbacks
from ui.config import conf


def register_theme(app):
    name = app.theme
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
    
def register_font(app):
    with dpg.font_registry():
        with dpg.font(app.font, size=14, tag="global_font"): pass
        with dpg.font(app.font, size=20, tag="loading_font"): pass

def register_themes(app):
    register_theme(app)
    dpg.bind_theme("global_theme")
    if not os.path.exists(app.font):
        app.log_message(f"Warning: Font file not found: {app.font}")
    else:
        register_font(app)
        dpg.bind_font("global_font")
        #dpg.bind_item_font("loading_text", "loading_font")

def update_theme(app, rebuild=False):
    to_delete = ["global_theme", "global_font", "loading_font"]
    for item in to_delete:
        if dpg.does_item_exist(item):
            dpg.delete_item(item)
        
    if rebuild:
        to_delete = ["primary_window", "loading_window"]
        for item in to_delete:
            if dpg.does_item_exist(item):
                dpg.delete_item(item)

        create_main_window(app)
        register_callbacks(app)
    
    register_themes(app)
    
    dpg.split_frame()

    app.log_message()
    