import dearpygui.dearpygui as dpg

from utils import *
import ui.config as conf


def register_callbacks(app):
    dpg.set_item_callback("lineedit_input_file", lambda: check_path_to_input_file(app))
    dpg.set_item_callback("choice_input_file_btn", lambda: choice_path_to_input_file(app))
    dpg.set_item_callback("load_file_btn", lambda: load_file(app))
    dpg.set_item_callback("arrow_left", lambda: arrow_left_callback(app))
    dpg.set_item_callback("arrow_right", lambda: arrow_right_callback(app))
    dpg.set_item_callback("rows_input", lambda: edit_rows_and_cols_inputs(app))
    dpg.set_item_callback("cols_input", lambda: edit_rows_and_cols_inputs(app))
    dpg.set_item_callback("margin_input", lambda: edit_params(app))
    dpg.set_item_callback("show_dividing_line", lambda: edit_params(app))
    dpg.set_item_callback("show_line_with_indentation", lambda: edit_params(app))
    dpg.set_item_callback("color_picker", lambda: edit_params(app))
    dpg.set_item_callback("radio_btn", lambda: edit_params(app))
    dpg.set_item_callback("lineedit_output_file", lambda: check_path_to_output_file(app))
    dpg.set_item_callback("choice_output_file_btn", lambda: choice_path_to_output_file(app))
    dpg.set_item_callback("export_file_btn", lambda: export_file(app))

def log_message(msg=None):
    if msg: dpg.set_value("log_output", msg)
    else: dpg.set_value("log_output", "")

def update_preview(app):
    img_data, _ = app.pdf_imposer.get_preview(page_num=app.current_page, scale=conf.scale)
    dpg.set_value("preview_pdf_texture", img_data)
    if app.pdf_imposer.output_doc is not None:
        dpg.set_value("quantity_page_label", app.pdf_imposer.quantity_page)

def check_path_to_input_file(app):
    path = dpg.get_value("lineedit_input_file")
    _, err = PDFInfo.validate_and_get_info(path)
    log_message(err)

def choice_path_to_input_file(app):
    path = FileDialogHelper.open_pdf_file()
    if path is None: return
    _, err = PDFInfo.validate_and_get_info(path)
    log_message(err)
    if not err: dpg.set_value("lineedit_input_file", path)

def load_file(app):
    path = dpg.get_value("lineedit_input_file")
    _, err = PDFInfo.validate_and_get_info(path)
    log_message(err)
    if err: return
    app.pdf_path = path
    app.pdf_imposer.load_doc(path)
    update_preview(app)

def arrow_left_callback(app):
    if (app.current_page == 1): 
        return
    if (app.pdf_path is None):
        log_message("Файл PDF не загружен")
        return
    dpg.set_value("page_label", int(dpg.get_value("page_label"))-1)
    app.current_page -= 1
    update_preview(app)

def arrow_right_callback(app):
    if (app.pdf_path is None):
        log_message("Файл PDF не загружен")
        return
    if (app.pdf_imposer.output_doc is not None) and \
        (app.current_page == app.pdf_imposer.quantity_page): 
        return
    dpg.set_value("page_label", int(dpg.get_value("page_label"))+1)
    app.current_page += 1
    update_preview(app)

def edit_rows_and_cols_inputs(app):
    rows = dpg.get_value("rows_input")
    cols = dpg.get_value("cols_input")
    if (rows <= 0):
        dpg.set_value("rows_input", 1)
        return
    if (cols <= 0):
        dpg.set_value("cols_input", 1)
        return
    if app.pdf_path is None:
        log_message("Файл PDF не загружен")
        dpg.set_value("rows_input", 2)
        dpg.set_value("cols_input", 2)
        return
    edit_params(app)

def edit_params(app):
    rows = dpg.get_value("rows_input")
    cols = dpg.get_value("cols_input")
    margin = dpg.get_value("margin_input")
    show_div_line = dpg.get_value("show_dividing_line")
    show_line_indent = dpg.get_value("show_line_with_indentation")
    color = [i/255 for i in list(dpg.get_value("color_picker"))[0:3]]
    blocks_are_vertical = dpg.get_value("radio_btn") == "Сверху"
    
    
    if (margin < 0):
        dpg.set_value("margin_input", 0)
        return
    

    if (blocks_are_vertical and (rows % 2 == 1)):
        log_message("В указанное количество строк не помещаются блоки по два")
        return
    if (not blocks_are_vertical and (cols % 2 == 1)):
        log_message("В указанное количество столбцов не помещаются блоки по два")
        return

    if app.pdf_path is None:
        log_message("Файл PDF не загружен")
        return
    
    log_message()
    app.pdf_imposer.update_params(rows, cols, margin, 
                                  show_line_indent, color, blocks_are_vertical)
    update_preview(app)

def check_path_to_output_file(app):
    path = dpg.get_value("lineedit_output_file")
    if not path: return
    if not is_type(path, "pdf"):
        log_message("Файл некорректного типа")
        return

def choice_path_to_output_file(app):
    path = FileDialogHelper.save_pdf_file()
    if path is None: return
    if not is_type(path, "pdf"):
        log_message("Файл некорректного типа")
        return
    dpg.set_value("lineedit_output_file", path)

def export_file(app):
    check_path_to_output_file(app)
    if app.pdf_path is None:
        log_message("Исходный файл не выбран")
        return
    path = dpg.get_value("lineedit_output_file")
    app.pdf_imposer.export_doc(path)