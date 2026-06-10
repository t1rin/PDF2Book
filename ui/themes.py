import os
import dearpygui.dearpygui as dpg

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

def register_all(app):
    register_theme(app)
    dpg.bind_theme("global_theme")
    if not os.path.exists(app.font):
        app.log_message(f"Warning: Font file not found: {app.font}")
    else:
        register_font(app)
        dpg.bind_font("global_font")

def update_theme(app):
    if dpg.does_item_exist("global_theme"):
        dpg.delete_item("global_theme")
    
    if dpg.does_item_exist("global_font"):
        dpg.delete_item("global_font")
    
    register_all(app)
    
    dpg.split_frame()

    app.log_message()

def register_themes(app):
    register_all(app)