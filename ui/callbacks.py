import dearpygui.dearpygui as dpg

from utils import *
import ui.config as conf


def update_preview(app):
    img_data, _ = app.pdf_imposer.get_preview(page_num=app.current_page, scale=conf.scale)
    dpg.set_value("preview_pdf_texture", img_data)
    if app.pdf_imposer.output_doc is not None:
        dpg.set_value("quantity_page_label", app.pdf_imposer.quantity_page)

def check_path_to_input_file(app):
    path = dpg.get_value("lineedit_input_file")
    _, err = PDFInfo.validate_and_get_info(path)
    app.log_message(err)

def open_file(app):
    path = FileDialogHelper.open_pdf_file()
    if path is None: return
    _, err = PDFInfo.validate_and_get_info(path)
    app.log_message(err)
    if not err:
        dpg.set_value("lineedit_input_file", path)
        load_file(app)

def load_file(app):
    path = dpg.get_value("lineedit_input_file")
    _, err = PDFInfo.validate_and_get_info(path)
    app.log_message(err)
    if err: return
    app.pdf_path = path
    app.pdf_imposer.load_doc(path)
    update_preview(app)

def arrow_left_callback(app):
    if (app.current_page == 1): 
        return
    if (app.pdf_path is None):
        app.log_message("Файл PDF не загружен")
        return
    dpg.set_value("page_label", int(dpg.get_value("page_label"))-1)
    app.current_page -= 1
    update_preview(app)

def arrow_right_callback(app):
    if (app.pdf_path is None):
        app.log_message("Файл PDF не загружен")
        return
    if (app.pdf_imposer.output_doc is not None) and \
        (app.current_page == app.pdf_imposer.quantity_page): 
        return
    dpg.set_value("page_label", int(dpg.get_value("page_label"))+1)
    app.current_page += 1
    update_preview(app)

def set_default_values(app):
    dpg.set_value("rows_input", 2)
    dpg.set_value("cols_input", 2)    
    dpg.set_value("margin_input", 15)
    dpg.set_value("radio_btn", "Слева")
    dpg.set_value("show_margin_lines", True)
    dpg.set_value("show_blocks_lines", False)
    dpg.set_value("show_cut_lines", True)
    dpg.set_value("color_picker", (125, 125, 125))
    dpg.set_value("lineedit_pattern", "4 2")

def edit_params(app):
    rows = dpg.get_value("rows_input")
    cols = dpg.get_value("cols_input")

    if (rows <= 0):
        dpg.set_value("rows_input", 1)
        return
    if (cols <= 0):
        dpg.set_value("cols_input", 1)
        return
    if app.pdf_path is None:
        app.log_message("Файл PDF не загружен")
        set_default_values(app)
        return

    margin = dpg.get_value("margin_input")
    show_margin_lines = dpg.get_value("show_margin_lines")
    show_blocks_lines = dpg.get_value("show_blocks_lines")
    show_cut_lines = dpg.get_value("show_cut_lines")
    color = [i/255 for i in list(dpg.get_value("color_picker"))[0:3]]
    blocks_are_vertical = dpg.get_value("radio_btn") == "Сверху"
    pattern = dpg.get_value("lineedit_pattern")
    
    if (margin < 0):
        dpg.set_value("margin_input", 0)
        return

    if (blocks_are_vertical and (rows % 2 == 1)):
        app.log_message("В указанное количество строк не помещаются блоки по два")
        return

    if (not blocks_are_vertical and (cols % 2 == 1)):
        app.log_message("В указанное количество столбцов не помещаются блоки по два")
        return

    if app.pdf_path is None:
        app.log_message("Файл PDF не загружен")
        return

    pattern_code = pattern.split()
    if (len(pattern_code) % 2 != 0) or not all(s.isdigit() for s in pattern_code):
        pattern = "4 2"

    pattern = f"[{pattern}] 0"

    app.log_message()
    app.pdf_imposer.update_params(rows=rows, cols=cols, margin=margin, 
                                  show_cut_lines=show_cut_lines,
                                  show_margin_lines=show_margin_lines, 
                                  show_blocks_lines=show_blocks_lines, 
                                  blocks_are_vertical=blocks_are_vertical,
                                  lines_color=color, dashes_pattern=pattern)
    update_preview(app)

def check_path_to_output_file(app):
    path = dpg.get_value("lineedit_output_file")
    if not path: return
    if not is_type(path, "pdf"):
        app.log_message("Файл некорректного типа")
        return

def save_as_file_btn(app):
    path = FileDialogHelper.save_pdf_file()
    if path is None: return
    if not is_type(path, "pdf"):
        app.log_message("Файл некорректного типа")
        return
    dpg.set_value("lineedit_output_file", path)
    save_file_btn(app)

def save_file_btn(app):
    check_path_to_output_file(app)
    if app.pdf_path is None:
        app.log_message("Исходный файл не выбран")
        return
    path = dpg.get_value("lineedit_output_file")
    app.pdf_imposer.export_doc(path)
    app.log_message("Файл сохранен")

def lineedit_pattern_btn(app):
    pattern = dpg.get_value("lineedit_pattern")
    pattern_code = pattern.split()
    if (len(pattern_code) % 2 == 0) and all(s.isdigit() for s in pattern_code):
        edit_params(app)
    else:
        app.log_message("Некорректный формат паттерна")


def register_callbacks(app):
    dpg.set_item_callback("lineedit_input_file", lambda: check_path_to_input_file(app))
    dpg.set_item_callback("open_file_btn", lambda: open_file(app))
    dpg.set_item_callback("load_file_btn", lambda: load_file(app))
    dpg.set_item_callback("arrow_left", lambda: arrow_left_callback(app))
    dpg.set_item_callback("arrow_right", lambda: arrow_right_callback(app))
    dpg.set_item_callback("rows_input", lambda: edit_params(app))
    dpg.set_item_callback("cols_input", lambda: edit_params(app))
    dpg.set_item_callback("margin_input", lambda: edit_params(app))
    dpg.set_item_callback("show_margin_lines", lambda: edit_params(app))
    dpg.set_item_callback("show_blocks_lines", lambda: edit_params(app))
    dpg.set_item_callback("show_cut_lines", lambda: edit_params(app))
    dpg.set_item_callback("color_picker", lambda: edit_params(app))
    dpg.set_item_callback("radio_btn", lambda: edit_params(app))
    dpg.set_item_callback("lineedit_output_file", lambda: check_path_to_output_file(app))
    dpg.set_item_callback("save_as_file_btn", lambda: save_as_file_btn(app))
    dpg.set_item_callback("save_file_btn", lambda: save_file_btn(app))
    dpg.set_item_callback("lineedit_pattern", lambda: lineedit_pattern_btn(app))