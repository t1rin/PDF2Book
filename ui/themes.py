from __future__ import annotations
from typing import TYPE_CHECKING

import os
import dearpygui.dearpygui as dpg

from utils import resource_path, get_logger

if TYPE_CHECKING:
    from main import PDF2BookApp


log = get_logger(__name__)


class ThemeManager:
    def __init__(self, app: PDF2BookApp) -> None:
        self.app: PDF2BookApp = app
        self._cache_fonts: dict[tuple[str, int], str | int] = dict()

        log.info("Initialize ThemeManager...")

        self.registry_themes()

    def registry_themes(self) -> None:
        themes_names = self.app.conf.themes.keys()
        for theme_name in themes_names:
            if theme_name and dpg.does_item_exist(theme_name):
                continue

            themes = self._get_style_dict(theme_name)
            with dpg.theme(tag=theme_name):
                for component, theme in themes.items():
                    with dpg.theme_component(component):
                        for style in theme["styles"]:
                            dpg.add_theme_style(*style)
                        for color in theme["colors"]:
                            dpg.add_theme_color(*color)
        
            with dpg.theme(tag="drawlist_"+theme_name):
                component = dpg.mvAll
                with dpg.theme_component(component):
                    dpg.add_theme_color(dpg.mvThemeCol_ChildBg, 
                         self.app.conf.themes[theme_name]["window_color"])
                    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
                    dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0)

    def update(self) -> None:
        dpg.bind_theme(self.app.theme)
        if dpg.does_item_exist("drawlist_child_window"):
            dpg.bind_item_theme("drawlist_child_window",
                                "drawlist_" + self.app.theme)

        self._fonts_settings = [
            (None,            self.app.font,       14),
            ("loading_text",  self.app.font,       20),
            ("pdf2book_text", self.app.title_font, 48),
        ]
        for item, path, size in self._fonts_settings:
            font_tag = self._get_font(path, size)
            if font_tag is None:
                continue

            if item is None:
                dpg.bind_font(font_tag)
            elif dpg.does_item_exist(item):
                dpg.bind_item_font(item, font_tag)

        self.app.message()

    def _get_font(self, path: str, size: int) -> str | int | None:
        item = (path, size)
        if item not in self._cache_fonts:
            with dpg.font_registry(tag=dpg.generate_uuid()):
                _path = resource_path(path)
                if not os.path.exists(_path):
                    msg = f"Font file not found: {path}"
                    self.app.message(content=msg, mood=False)
                    log.warning(msg)
                    return None
                font_tag = dpg.generate_uuid()
                with dpg.font(_path, size, tag=font_tag):
                    self._cache_fonts[item] = font_tag
        return self._cache_fonts[item]

    def _get_style_dict(self, theme_name: str) -> dict[int, dict[str, list]]:
        settings = self.app.conf.themes[theme_name]
        return {
            dpg.mvAll: {
                "styles": [
                    (dpg.mvStyleVar_WindowPadding, 8, 8),
                    (dpg.mvStyleVar_FramePadding, 6, 4),
                    (dpg.mvStyleVar_CellPadding, 6, 3),
                    (dpg.mvStyleVar_ItemSpacing, 8, 10),
                    (dpg.mvStyleVar_ItemInnerSpacing, 8, 8),
                    (dpg.mvStyleVar_ScrollbarSize, 14),
                    (dpg.mvStyleVar_ChildRounding, 10),
                    (dpg.mvStyleVar_SeparatorTextBorderSize, 2),
                    (dpg.mvStyleVar_SeparatorTextAlign, 0.5, 0.5),
                    (dpg.mvStyleVar_SeparatorTextPadding, 0, 0),
                    (dpg.mvStyleVar_TabBarBorderSize, 0),
                ],
                "colors": [
                    (dpg.mvThemeCol_WindowBg, settings["window_color"]),
                    (dpg.mvThemeCol_ChildBg, settings["bg_color"]),
                    (dpg.mvThemeCol_PopupBg, settings["bg_color"]),
                    (dpg.mvThemeCol_MenuBarBg, settings["window_color"]),
                    (dpg.mvThemeCol_FrameBg, settings["widget_color"]),
                    (dpg.mvThemeCol_Button, settings["widget_color"]),
                    (dpg.mvThemeCol_TitleBg, settings["widget_color"]),
                    (dpg.mvThemeCol_TitleBgActive, settings["widget_color"]),
                    (dpg.mvThemeCol_Tab, settings["widget_color"]),
                    (dpg.mvThemeCol_Text, settings["text_color"]),
                    (dpg.mvThemeCol_Header, settings["hovered_color"]),
                    (dpg.mvThemeCol_TextDisabled, settings["text_disabled_color"]),
                    (dpg.mvThemeCol_ButtonHovered, settings["hovered_color"]),
                    (dpg.mvThemeCol_HeaderHovered, settings["hovered_color"]),
                    (dpg.mvThemeCol_TabHovered, settings["hovered_color"]),
                    (dpg.mvThemeCol_ButtonActive, settings["selected_color"]),
                    (dpg.mvThemeCol_HeaderActive, settings["selected_color"]),
                    (dpg.mvThemeCol_TabSelected, settings["selected_color"]),
                    (dpg.mvThemeCol_TabActive, settings["selected_color"]),
                    (dpg.mvThemeCol_Separator, settings["border_color"]),
                    (dpg.mvThemeCol_Border, settings["border_color"]),
                    (dpg.mvThemeCol_TableBorderLight, settings["border_color"]),
                    (dpg.mvThemeCol_TableBorderStrong, settings["border_color"]),
                    (dpg.mvThemeCol_ScrollbarBg, settings["bg_color"]),
                    (dpg.mvThemeCol_ScrollbarGrab, settings["widget_color"]),
                    (dpg.mvThemeCol_ScrollbarGrabHovered, settings["hovered_color"]),
                    (dpg.mvThemeCol_ScrollbarGrabActive, settings["selected_color"]),
                ]
            },
            dpg.mvTab: {
                "styles": [
                    (dpg.mvStyleVar_TabBorderSize, 1),
                    (dpg.mvStyleVar_TabRounding, 0),
                ],
                "colors": []
            },
            dpg.mvTable: {
                "styles": [
                    (dpg.mvStyleVar_CellPadding, 1, 0)
                ],
                "colors": [
                    (dpg.mvThemeCol_TableHeaderBg, settings["widget_color"])
                ]
            },
            dpg.mvPlot: {
                "styles": [
                    (dpg.mvStyleVar_TabBorderSize, 1),
                    (dpg.mvStyleVar_TabRounding, 0),
                ],
                "colors": [
                    (dpg.mvThemeCol_FrameBg, settings["bg_color"]),
                    (dpg.mvPlotCol_Selection, settings["plot_selection_color"]),
                ]
            }
        }
