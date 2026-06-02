import dearpygui.dearpygui as dpg

import ui.config as conf


def create_parametrs_window():
    with dpg.child_window():
        dpg.add_separator(label="PDF2Book")
        dpg.add_text("Исходный файл PDF")
        dpg.add_input_text(tag="lineedit_input_file", hint="enter path to file")
        with dpg.group(horizontal=True):
            dpg.add_button(tag="choice_input_file_btn", label="Выбрать")
            dpg.add_button(tag="load_file_btn", label="Загрузить")
        
        dpg.add_separator(label="Параметры")
        dpg.add_text("Количество строк:")
        dpg.add_input_int(tag="rows_input")
        dpg.add_text("Количество столбцов:")
        dpg.add_input_int(tag="cols_input")
        dpg.add_text("Отступ:")
        dpg.add_input_int(tag="margin_input")
        dpg.add_checkbox(tag="show_dividing_line", label="Показ разделяющего пунктира")
        dpg.add_checkbox(tag="show_line_with_indentation", label="Показ пунктира с отступом")
        dpg.add_text("Цвет пунктира:")
        dpg.add_color_edit((125, 125, 125), tag="color_picker", no_alpha=True, no_picker=True, no_drag_drop=True)
        dpg.add_text("Место переплета:")
        dpg.add_radio_button(("Слева", "Сверху"), tag="radio_btn", horizontal=True)

        dpg.add_separator(label="Export")
        dpg.add_text("Выходной файл PDF")
        dpg.add_input_text(tag="lineedit_output_file", hint="enter path to directory")
        with dpg.group(horizontal=True):
            dpg.add_button(tag="choice_output_file_btn", label="Выбрать")
            dpg.add_button(tag="export_file_btn", label="Экспорт")
        dpg.add_text("w", color=(200, 50, 50), tag="log_output")

def create_plot_window():
    with dpg.child_window():
        with dpg.plot(width=-1, height=-1, equal_aspects=True, 
                        no_mouse_pos=True, no_menus=True):
            options = {"no_gridlines": True, "no_tick_marks": True, "no_tick_labels": True}
            dpg.add_plot_axis(dpg.mvXAxis, **options) 
            with dpg.plot_axis(dpg.mvYAxis, **options): 
                ...
                #dpg.add_image_series(
                #    create_texture(),
                    #   [0, 0], [0, 0],
                    #   tag=VIEWER_IMAGE_ID)

def create_main_window(app):
    with dpg.window(tag="primary_window"):
        with dpg.group():
            with dpg.table(header_row=False, hideable=True, resizable=True):
                if conf.parametrs_window_on_the_left:
                    dpg.add_table_column(width_fixed=True, 
                        init_width_or_weight=conf.default_panel_width)
                dpg.add_table_column()
                if not conf.parametrs_window_on_the_left:
                        dpg.add_table_column(width_fixed=True, 
                            init_width_or_weight=conf.default_panel_width)
                with dpg.table_row():
                    if conf.parametrs_window_on_the_left:
                        create_parametrs_window()
                    create_plot_window()
                    if not conf.parametrs_window_on_the_left:
                        create_parametrs_window()
