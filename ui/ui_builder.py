import dearpygui.dearpygui as dpg

from utils import *
from ui.callbacks import set_values, drop_handler
from ui.config import conf

if os_type() == "Windows":
    import ui.DearPyGui_DragAndDrop as dpg_dnd


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
      
def create_settings_panel(app):
    with dpg.child_window(tag="settings_panel"):

        dpg.add_separator(label="View")

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
                dpg.add_radio_button(("Слева", "Сверху"), tag="radio_btn", horizontal=True)
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

def create_drawlist_window(app):
    with dpg.child_window(tag="drawlist_window", show=False):
        with dpg.group(parent="drawlist_window", pos=[conf.padding_drawlist, 
                                                      conf.padding_drawlist]):
            with dpg.drawlist(width=-1, height=-1, tag="drawlist_3d"):
                with dpg.draw_layer(depth_clipping=False, cull_mode=dpg.mvCullMode_Back, 
                                    perspective_divide=True, tag="drawlayer_3d"):
                    with dpg.draw_node(tag="plane_node"): pass

def create_plot_window(app):
    with dpg.child_window(tag="plot_window"):
        with dpg.plot(width=-1, height=-1, equal_aspects=True, 
                        no_mouse_pos=True, no_menus=True):
            options = {"no_gridlines": True, "no_tick_marks": True, 
                       "no_tick_labels": True, "no_tick_labels": True}
            dpg.add_plot_axis(dpg.mvXAxis, tag="x_axis", **options) 
            with dpg.plot_axis(dpg.mvYAxis, tag="y_axis", **options):
                texture_tag = app.pdf_imposer.params.format
                _, size = app.tm.get_preview_data(texture_tag, only_size=True)
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

def create_menu_bar(app):
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
                              tag="preview_mode_button", user_data="preview")
            dpg.add_menu_item(label="Визуализация", check=True, 
                              tag="visualization_mode_button", 
                              user_data="visualization")
            
        with dpg.menu(label="Вид"):
            dpg.add_menu_item(label="Переместить панель", tag="move_panel_btn")
            dpg.add_separator()
            dpg.add_menu_item(label="Сменить тему", shortcut="F1",
                              tag="switch_theme_btn")
            dpg.add_menu_item(label="Сменить шрифт", shortcut="F2",
                              tag="switch_font_btn")
            dpg.add_separator()
            with dpg.menu(label="Детализация"):
                current_scale = app.scale
                for value in range(100, 300, 25):
                    scale = value / 100
                    tag = f"scale_{scale}_btn"
                    dpg.add_menu_item(label=str(scale), tag=tag, check=True,
                        default_value=(scale == current_scale), user_data=scale)
                dpg.add_separator()
                dpg.add_text("Изменение вступит в силу\nпосле перезапуска", 
                           color=(150, 150, 60), wrap=200)

def create_main_window(app):
    with dpg.window(tag="primary_window"):
        dpg.set_primary_window("primary_window", True)
        create_menu_bar(app)
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
                    with dpg.group():
                        create_drawlist_window(app)
                        create_plot_window(app)
                    if not app.pw_left:
                        create_settings_panel(app)
    create_loading_window(app)

    resize_update(app)

    set_values(app)

def create_drag_and_drop(app):
    if os_type() == "Windows":
        dpg_dnd.initialize()
        dpg_dnd.set_drop(lambda data, keys: 
                         drop_handler(app, data))
    
