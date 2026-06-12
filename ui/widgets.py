import dearpygui.dearpygui as dpg

from utils import *
from ui.callbacks import set_default_values
from core.config import formats
from ui.config import conf


def resize_update(app):
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()
    widget_width = dpg.get_item_width("loading_window")
    widget_height = dpg.get_item_height("loading_window")
    pos_loading_window = ((viewport_width - widget_width) / 2, 
                          (viewport_height - widget_height) / 2)
    dpg.configure_item("loading_window", pos=pos_loading_window)

    padding = conf.padding_loading_text
    text_width, _ = dpg.get_item_rect_size("loading_text")
    pos_loading_text = ((widget_width - text_width) / 2, widget_width + padding)
    dpg.configure_item("loading_text", pos=pos_loading_text)

def create_context_menu(app):
    with dpg.window(tag="context_menu", popup=True, show=False, no_title_bar=True, 
                    no_move=True, no_resize=True, autosize=True):
        dpg.add_menu_item(label="Переместить панель", tag="move_panel_btn")
        dpg.add_text("Детализация: ", tag="scale_text")
        with dpg.group(horizontal=True):
            dpg.add_button(label="1.5", tag="scale_1.5_btn")
            dpg.add_button(label="1.75", tag="scale_1.75_btn")
            dpg.add_button(label="2", tag="scale_2.0_btn")
        with dpg.group(horizontal=True):
            dpg.add_button(label="2.25", tag="scale_2.25_btn")
            dpg.add_button(label="2.5", tag="scale_2.5_btn")
            dpg.add_button(label="3", tag="scale_2.75_btn")
        dpg.add_text("При выборе необходимо будет перезапустить программу", wrap=0)

def create_settings_panel(app):
    with dpg.child_window(tag="settings_panel"):
        dpg.add_separator(label="PDF2Book")
        dpg.add_text("Исходный файл PDF")
        dpg.add_input_text(tag="lineedit_input_file", hint="enter path to file")
        with dpg.group(horizontal=True):
            dpg.add_button(tag="open_file_btn", label="Открыть")
            dpg.add_button(tag="load_file_btn", label="Загрузить")
        
        dpg.add_separator(label="Export")
        dpg.add_text("Выходной файл PDF")
        dpg.add_input_text(tag="lineedit_output_file", hint="enter path")
        with dpg.group(horizontal=True):
            dpg.add_button(tag="save_as_file_btn", label="Сохранить как")
            dpg.add_button(tag="save_file_btn", label="Сохранить")

        dpg.add_separator(label="View")
        with dpg.group(horizontal=True):
            dpg.add_text("Страница: ")
            dpg.add_button(arrow=True, direction=dpg.mvDir_Left, tag="arrow_left")
            dpg.add_text("1", tag="page_label")
            dpg.add_button(arrow=True, direction=dpg.mvDir_Right, tag="arrow_right")
        with dpg.group(horizontal=True):
            dpg.add_text("Всего: ")
            dpg.add_text("0", tag="quantity_page_label")

        dpg.add_separator(label="Settings")

        with dpg.tab_bar():
            with dpg.tab(label="Основные"):
                dpg.add_combo(tag="combo_formats", height_mode=dpg.mvComboHeight_Largest)
                dpg.add_text("Количество строк:")
                dpg.add_input_int(tag="rows_input", min_value=1)
                dpg.add_text("Количество столбцов:")
                dpg.add_input_int(tag="cols_input", min_value=1)
                dpg.add_text("Отступ:")
                dpg.add_input_int(tag="margin_input", min_value=0)
                dpg.add_text("Место переплета:")
                dpg.add_radio_button(("Слева", "Сверху"), tag="radio_btn", horizontal=True)

            with dpg.tab(label="Линии"):
                dpg.add_checkbox(tag="show_margin_lines", label="Показ линии с отступом")
                dpg.add_checkbox(tag="show_blocks_lines", label="Показ линии блоков")
                dpg.add_checkbox(tag="show_cut_lines", label="Показ разделяющего пунктира")
                dpg.add_text("Цвет пунктира:")
                dpg.add_color_edit(tag="color_picker", no_alpha=True, no_picker=True, no_drag_drop=True)
                dpg.add_text("Толщина линий:")
                dpg.add_input_int(tag="thickness_input", min_value=1)
                dpg.add_text("Паттерн пунктира:")
                dpg.add_input_text(tag="lineedit_pattern", hint="enter pattern")

        dpg.add_text(color=(200, 50, 50), wrap=0, tag="log_output")

        set_default_values(app)

def create_plot_window(app):
    with dpg.child_window():
        with dpg.plot(width=-1, height=-1, equal_aspects=True, 
                        no_mouse_pos=True, no_menus=True):
            options = {"no_gridlines": True, "no_tick_marks": True, "no_tick_labels": True}
            dpg.add_plot_axis(dpg.mvXAxis, tag="x_axis", **options) 
            with dpg.plot_axis(dpg.mvYAxis, tag="y_axis", **options):
                create_dynamic_textures(formats, scale=app.scale)
                texture_tag = app.pdf_imposer.params.format
                _, size = get_dynamic_texture(texture_tag, only_size=True)
                dpg.add_image_series(texture_tag, [0, 0], size, tag="preview_pdf")
                dpg.fit_axis_data(dpg.top_container_stack())
            dpg.fit_axis_data("x_axis")

def create_loading_window(app):
    with dpg.window(tag="loading_window", autosize=True,
                    show=True, modal=True, no_title_bar=True, 
                    no_resize=True, no_move=True, no_background=True):
        with dpg.group(width=-1):
            dpg.add_loading_indicator(tag="loading_widget", style=2, radius=7)
            dpg.add_text("Loading...", tag="loading_text")

def create_main_window(app):
    create_context_menu(app)
    with dpg.window(tag="primary_window"):
        dpg.set_primary_window("primary_window", True)
        with dpg.group():
            with dpg.table(header_row=False, hideable=True, resizable=True):
                if app.pw_left:
                    dpg.add_table_column(width_fixed=True, 
                        init_width_or_weight=conf.default_panel_width)
                dpg.add_table_column()
                if not app.pw_left:
                        dpg.add_table_column(width_fixed=True, 
                            init_width_or_weight=conf.default_panel_width)
                with dpg.table_row():
                    if app.pw_left:
                        create_settings_panel(app)
                    create_plot_window(app)
                    if not app.pw_left:
                        create_settings_panel(app)
    create_loading_window(app)

    resize_update(app)
    
    
