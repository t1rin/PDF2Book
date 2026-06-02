import dearpygui.dearpygui as dpg

global_font_path = "./assets/fonts/DeleddaOpen.ttf"
menu_font_path = "./assets/fonts/DeleddaOpen.ttf"
about_font_path = "./assets/fonts/DeleddaOpen.ttf"

def register_themes():
    with dpg.font_registry():
        with dpg.font(global_font_path, size=14, tag="global_font"):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

        with dpg.font(menu_font_path, size=12, tag="menu_font"):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

        with dpg.font(about_font_path, size=16, tag="about_font"):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    with dpg.theme(tag="global_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 2, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 6, 3, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 10, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 8, 8, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 14, category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (16, 16, 16), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (50, 50, 55), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (28, 28, 28), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (28, 28, 28), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (28, 28, 28), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (225, 225, 225), category=dpg.mvThemeCat_Core)

        with dpg.theme_component(dpg.mvTable):
            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 1, 0, category=dpg.mvThemeCat_Core)

        with dpg.theme_component(dpg.mvPlot):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (28, 28, 28), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvPlotCol_Selection, (0, 120, 215), category=dpg.mvThemeCat_Plots)

def apply_theme():
    register_themes()
    dpg.bind_theme("global_theme")
    dpg.bind_font("global_font")