from __future__ import annotations
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg

from utils import *
from ui.config import MODE
from core import LEFT, TOP, RIGHT

if os_type() == "Windows":
    import ui.DearPyGui_DragAndDrop as dpg_dnd

if TYPE_CHECKING:
    from main import PDF2BookApp


def resize_update(app: PDF2BookApp) -> None:
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()
    if not dpg.does_item_exist("loading_window"):
        return
    widget_width = dpg.get_item_width("loading_window")
    widget_height = dpg.get_item_height("loading_window")
    pos_loading_window = ((viewport_width - widget_width) / 2, 
                          (viewport_height - widget_height) / 2)
    dpg.configure_item("loading_window", pos=pos_loading_window)

    padding = app.conf.padding_loading_text
    text_width, _ = dpg.get_item_rect_size("loading_text")
    pos_loading_text = ((widget_width - text_width) / 2, widget_width + padding)
    dpg.configure_item("loading_text", pos=pos_loading_text)
      
def create_settings_panel(app: PDF2BookApp) -> None:
    with dpg.child_window(tag="settings_panel"):

        dpg.add_text(tag="pdf2book_text", default_value="PDF2Book")

        with dpg.group():
            with dpg.group(tag="preview_view_settings"):
                dpg.add_checkbox(label="Индексы страниц", tag="indexes_pages_checkbox")
                with dpg.group(horizontal=True):
                    dpg.add_text("Страница: ")
                    dpg.add_button(arrow=True, direction=dpg.mvDir_Left, tag="arrow_left")
                    dpg.add_text("1", tag="page_label")
                    dpg.add_button(arrow=True, direction=dpg.mvDir_Right, tag="arrow_right")
                with dpg.group(horizontal=True):
                    dpg.add_text("Всего: ")
                    dpg.add_text("0", tag="quantity_page_label")
            with dpg.group(tag="visualiization_view_settings", show=False):
                with dpg.group(horizontal=True):
                    dpg.add_button(tag="reset_to_home_btn", label="Домой")
                    dpg.add_button(tag="detailed_visual_properties_btn", label="Подробнее")
                with dpg.group(horizontal=True):
                    dpg.add_text("Текущий элемент:")
                    dpg.add_text(tag="active_block_label")
                with dpg.group(horizontal=True):
                    dpg.add_text("Страниц всего: ")
                    dpg.add_text("0", tag="quantity_source_page_label")

        dpg.add_separator(label="Settings")

        with dpg.tab_bar(tag="tab_bar"):
            with dpg.tab(label="Основные"):
                dpg.add_combo(tag="combo_formats", height_mode=dpg.mvComboHeight_Largest)
                dpg.add_text("Количество строк:")
                dpg.add_input_int(tag="rows_input")
                dpg.add_text("Количество столбцов:")
                dpg.add_input_int(tag="cols_input")
                dpg.add_text("Отступ:")
                dpg.add_input_int(tag="margin_input")

            with dpg.tab(label="Линии"):
                dpg.add_checkbox(tag="show_margin_lines", label="Показ линии с отступом")
                dpg.add_checkbox(tag="show_blocks_lines", label="Показ линии блоков")
                dpg.add_checkbox(tag="show_cut_lines", label="Показ разделяющего пунктира")
                dpg.add_text("Цвет линий:")
                dpg.add_color_edit(tag="color_picker", no_alpha=True, no_picker=True, no_drag_drop=True)
                dpg.add_text("Толщина линий:")
                dpg.add_input_int(tag="thickness_input")
                dpg.add_text("Паттерн пунктира:")
                dpg.add_input_text(tag="lineedit_pattern", hint="enter pattern")

            with dpg.tab(label="Сшивка"):
                dpg.add_text("Место переплета:")
                dpg.add_radio_button(("Слева", "Сверху", "Справа"), tag="radio_btn", horizontal=True)
                dpg.add_checkbox(tag="separate_checkbox", label="Делить на секции")
                with dpg.group(tag="part_options"):
                    dpg.add_text("Размер секции:")
                    dpg.add_input_int(tag="size_part_input", step=4)

            with dpg.tab(label="Визуализация", tag="visualization_tab"):
                with dpg.group(horizontal=True):
                    dpg.add_text("Часть:")
                    dpg.add_combo(tag="combo_parts",
                                  height_mode=dpg.mvComboHeight_Largest)
                with dpg.group(horizontal=True):
                    dpg.add_text("Блок:")
                    dpg.add_combo(tag="combo_blocks", 
                                  height_mode=dpg.mvComboHeight_Largest)
                dpg.add_text("Угол первого листа:")
                dpg.add_input_int(tag="alpha_input", step=3)
                dpg.add_text("Угол второго листа:")
                dpg.add_input_int(tag="beta_input", step=3)

        dpg.add_text(wrap=0, tag="log_output")

def create_drawlist_window(app: PDF2BookApp) -> None:
    with dpg.child_window(tag="drawlist_window", show=False):
        with dpg.group(parent="drawlist_window", 
                       pos=[app.conf.padding_drawlist,
                            app.conf.padding_drawlist]):
            with dpg.child_window(tag="drawlist_child_window", no_scrollbar=True):
                with dpg.drawlist(width=-1, height=-1, tag="drawlist_3d"):
                    with dpg.draw_layer(depth_clipping=False, cull_mode=dpg.mvCullMode_Back, 
                                        perspective_divide=True, tag="drawlayer_3d"):
                        with dpg.draw_node(tag="plane_node"): pass

def create_plot_window(app: PDF2BookApp) -> None:
    with dpg.child_window(tag="plot_window"):
        with dpg.plot(width=-1, height=-1, equal_aspects=True, 
                        no_mouse_pos=True, no_menus=True):
            options = {"no_gridlines": True, "no_tick_marks": True, 
                       "no_tick_labels": True, "no_tick_labels": True}
            dpg.add_plot_axis(dpg.mvXAxis, tag="x_axis", **options) 
            with dpg.plot_axis(dpg.mvYAxis, tag="y_axis", **options):
                page_size = app.pdf_imposer.params.page_size
                index_format = list(app.conf.formats.values()).index(page_size)
                texture_tag = list(app.conf.formats.keys())[index_format]
                _, size = app.texture_manager.get_preview_data(page_size, only_size=True)
                dpg.add_image_series(texture_tag, [0, 0], size, tag="preview_pdf")
                dpg.fit_axis_data(dpg.top_container_stack())
            dpg.fit_axis_data("x_axis")

def create_loading_window(app: PDF2BookApp) -> None:
    with dpg.window(tag="loading_window", autosize=True,
                    show=True, modal=True, no_title_bar=True, 
                    no_resize=True, no_move=True, no_background=True):
        with dpg.group(width=-1):
            dpg.add_loading_indicator(tag="loading_widget", style=2, radius=7)
            dpg.add_text("Loading...", tag="loading_text")

def create_menu_bar(app: PDF2BookApp) -> None:
    with dpg.menu_bar():
        with dpg.menu(label="Файл"):
            dpg.add_menu_item(label="Открыть PDF", tag="open_file_btn",
                              shortcut="Ctrl+O")
            dpg.add_separator()
            dpg.add_menu_item(label="Сохранить", tag="save_file_btn",
                              shortcut="Ctrl+S")
            dpg.add_menu_item(label="Сохранить как...", tag="save_as_file_btn",
                              shortcut="Ctrl+Shift+S")
            with dpg.menu(label="Параметры"):
                dpg.add_checkbox(tag="split_file_checkbox", 
                                label="Разделять файл для печати")
            dpg.add_separator()
            with dpg.menu(label="Пути"):
                dpg.add_text("Исходный")
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="lineedit_input_file", enabled=False)
                    dpg.add_button(tag="open_input_folder_btn",
                                   label="Показать")
                dpg.add_text("Выходной")
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="lineedit_output", enabled=False)
                    dpg.add_button(tag="open_output_folder_btn", 
                                   label="Показать")
            
        with dpg.menu(label="Режим"):
            dpg.add_menu_item(label="Просмотр", check=True, default_value=True,
                              tag="preview_mode_button", user_data="preview",
                              shortcut="F1")
            dpg.add_menu_item(label="Визуализация", check=True, 
                              tag="visualization_mode_button", 
                              user_data="visualization",
                              shortcut="F2")
            
        with dpg.menu(label="Вид"):
            dpg.add_menu_item(label="Переместить панель", tag="move_panel_btn")
            dpg.add_separator()
            dpg.add_menu_item(label="Сменить тему", shortcut="F3",
                              tag="switch_theme_btn")
            dpg.add_menu_item(label="Сменить шрифт", shortcut="F4",
                              tag="switch_font_btn")
            dpg.add_separator()
            with dpg.menu(label="Детализация"):
                dpg.add_text("Включен автоматический\nперезапуск", 
                    color=app.conf.themes[app.theme]["negative_color"], wrap=200)
                dpg.add_separator()
                for dpi in app.conf.defaults_dpi:
                    tag = f"dpi_{dpi}_btn"
                    dpg.add_menu_item(label=str(dpi), tag=tag, check=True,
                        default_value=(dpi == app.conf.dpi), user_data=dpi)

def create_drag_and_drop(app: PDF2BookApp) -> None:
    if os_type() == "Windows":
        from ui.callbacks import drop_handler

        dpg_dnd.initialize()
        dpg_dnd.set_drop(lambda data, _: 
                         drop_handler(app, data))

def build_table_layout(app: PDF2BookApp) -> None:
    order = ("settings_panel", "content_group") if app.pw_left else \
            ("content_group", "settings_panel")

    for tag in order:
        dpg.move_item(tag, parent="primary_window")

    if dpg.does_item_exist("layout_table"):
        dpg.delete_item("layout_table")

    with dpg.table(tag="layout_table", header_row=False, hideable=True,
                   resizable=True, parent="primary_window"):
        if app.pw_left:
            dpg.add_table_column(width_fixed=True,
                                  init_width_or_weight=app.conf.default_panel_width)
            dpg.add_table_column()
        else:
            dpg.add_table_column()
            dpg.add_table_column(width_fixed=True,
                                  init_width_or_weight=app.conf.default_panel_width)

        with dpg.table_row(tag="layout_row"):
            pass

    for tag in order:
        dpg.move_item(tag, parent="layout_row")

def create_main_window(app: PDF2BookApp) -> None:
    with dpg.window(tag="primary_window"):
        dpg.set_primary_window("primary_window", True)
        create_menu_bar(app)

        create_settings_panel(app)
        with dpg.group(tag="content_group"):
            create_drawlist_window(app)
            create_plot_window(app)

        build_table_layout(app)

    create_loading_window(app)

    resize_update(app)

    set_values(app)
    
def set_values(app: PDF2BookApp) -> None:
    if app.pdf_path:
        dpg.set_value("lineedit_input_file", app.pdf_path)
    dpg.set_value("page_label", app.current_page)
    dpg.set_value("rows_input", app.pdf_imposer.params.rows)
    dpg.set_value("cols_input", app.pdf_imposer.params.cols)    
    dpg.set_value("margin_input", app.pdf_imposer.params.margin)
    dpg.set_value("radio_btn", {LEFT: "Слева", TOP: "Сверху", RIGHT: "Справа"}[app.pdf_imposer.params.side])
    dpg.set_value("show_margin_lines", app.pdf_imposer.params.show_margin_lines)
    dpg.set_value("show_blocks_lines", app.pdf_imposer.params.show_blocks_lines)
    dpg.set_value("show_cut_lines", app.pdf_imposer.params.show_cut_lines)
    dpg.set_value("color_picker", [int(c * 255) for c in app.pdf_imposer.params.color_lines])
    dpg.set_value("thickness_input", app.pdf_imposer.params.thickness_lines)
    dpg.set_value("lineedit_pattern", app.pdf_imposer.params.dashes_pattern)
    dpg.set_value("split_file_checkbox", app.is_split_file)
    dpg.set_value("separate_checkbox", bool(app.pdf_imposer.params.quantity_pages_for_part))
    dpg.set_value("indexes_pages_checkbox", app.is_indexation)
    dpg.configure_item("part_options", show=bool(app.pdf_imposer.params.quantity_pages_for_part))

    page_size = app.pdf_imposer.params.page_size
    items = [*app.conf.formats.keys()]
    select = items[list(app.conf.formats.values()).index(page_size)]
    dpg.configure_item("combo_formats", items=items)
    dpg.set_value("combo_formats", select)

    set_values_of_modes(app)
    set_values_of_visualization(app)

def set_values_of_modes(app: PDF2BookApp) -> None:
    is_preview_mode = app.mode == MODE.PREVIEW
    is_visualization_mode = app.mode == MODE.VISUALIZATION
    dpg.set_value("preview_mode_button", is_preview_mode)
    dpg.set_value("visualization_mode_button", is_visualization_mode)
    dpg.configure_item("plot_window", show=is_preview_mode)
    dpg.configure_item("drawlist_window", show=is_visualization_mode)
    dpg.configure_item("preview_view_settings", show=is_preview_mode)
    dpg.configure_item("visualiization_view_settings", 
                       show=is_visualization_mode)
    if is_preview_mode:
        dpg.configure_item("visualization_tab", show=False)
        dpg.configure_item("detailed_visual_properties_btn", show=True)

def set_values_of_visualization(app: PDF2BookApp) -> None:
    if app.pdf_imposer.input_doc is not None:
        q_pages = len(app.pdf_imposer.input_doc)
        q_parts = app.scene.visual_book.get('q_parts')
        q_blocks = app.scene.visual_book.get('q_blocks')
        dpg.configure_item("combo_parts", items=list(range(q_parts)))
        dpg.configure_item("combo_blocks", items=list(range(q_blocks)))
        dpg.set_value("quantity_source_page_label", q_pages)
    part_index = app.scene.visual_book.active_block[0]
    block_index = app.scene.visual_book.active_block[1]
    alpha = app.scene.visual_book.get('alpha', part_index, block_index)
    beta = app.scene.visual_book.get('beta', part_index, block_index)
    dpg.set_value("combo_parts", part_index)
    dpg.set_value("combo_blocks", block_index)
    dpg.set_value("alpha_input", alpha)
    dpg.set_value("beta_input", beta)
    dpg.set_value("active_block_label", 
                  f"({part_index}, {block_index})")

    app.scene.update()
