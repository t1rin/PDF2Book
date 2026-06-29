import dearpygui.dearpygui as dpg

from utils import *
from ui.themes import update_theme
from core.config import formats
from ui.config import conf


def update_preview(app, align=False):
    texture_tag = app.pdf_imposer.params.format
    img_data, _ = app.pdf_imposer.get_preview(page_num=app.current_page, 
                                                 scale=app.scale)
    update_texture(texture_tag, img_data)
    if align:
        dpg.fit_axis_data("x_axis")
        dpg.fit_axis_data("y_axis")
    if app.pdf_imposer.output_doc is not None:
        dpg.set_value("quantity_page_label", app.pdf_imposer.quantity_page)

def is_ok_input_file(app):
    path = dpg.get_value("lineedit_input_file")
    _, err = PDFInfo.validate_and_get_info(path)
    if path:
        app.log_message(err)
    else:
        app.log_message()

def load_file(app):
    path = dpg.get_value("lineedit_input_file")
    _, err = PDFInfo.validate_and_get_info(path)
    app.log_message(err)
    if err: return

    def on_loading(success, error):
        if success:
            update_preview(app, align=True)
        else:
            app.pdf_path = None
            app.log_message(error)

    app.pdf_path = path
    app.pdf_imposer.update_params()
    app.pdf_imposer.load_doc(path, on_loading)

def open_file(app):
    path = FileDialogHelper.open_pdf_file()
    if path is None: return
    _, err = PDFInfo.validate_and_get_info(path)
    app.log_message(err)
    if not err:
        dpg.set_value("lineedit_input_file", path)
        load_file(app)
        
def drop_handler(app, data):
    path = data[0]
    if path is None: return
    _, err = PDFInfo.validate_and_get_info(path)
    app.log_message(err)
    if not err:
        dpg.set_value("lineedit_input_file", path)
        load_file(app)

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
    if app.pdf_path:
        dpg.set_value("lineedit_input_file", app.pdf_path)
    dpg.set_value("page_label", app.current_page)
    dpg.set_value("rows_input", app.pdf_imposer.params.rows)
    dpg.set_value("cols_input", app.pdf_imposer.params.cols)    
    dpg.set_value("margin_input", app.pdf_imposer.params.margin)
    dpg.set_value("radio_btn", "Сверху" 
                  if app.pdf_imposer.params.blocks_are_vertical else "Слева")
    dpg.set_value("show_margin_lines", app.pdf_imposer.params.show_margin_lines)
    dpg.set_value("show_blocks_lines", app.pdf_imposer.params.show_blocks_lines)
    dpg.set_value("show_cut_lines", app.pdf_imposer.params.show_cut_lines)
    dpg.set_value("color_picker", [int(c * 255) for c in app.pdf_imposer.params.color_lines])
    dpg.set_value("thickness_input", app.pdf_imposer.params.thickness_lines)
    dpg.set_value("lineedit_pattern", app.pdf_imposer.params.dashes_pattern[1:-3])
    dpg.set_value("split_file_checkbox", app.is_split_file)
    dpg.set_value("separate_checkbox", bool(app.pdf_imposer.params.quantity_pages_for_part))
    dpg.configure_item("part_options", show=bool(app.pdf_imposer.params.quantity_pages_for_part))

    items = [*formats.keys()]
    dpg.configure_item("combo_formats", items=items)
    dpg.set_value("combo_formats", app.pdf_imposer.params.format)

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
    format = dpg.get_value("combo_formats")
    size_part = dpg.get_value("size_part_input")
    show_margin_lines = dpg.get_value("show_margin_lines")
    show_blocks_lines = dpg.get_value("show_blocks_lines")
    show_cut_lines = dpg.get_value("show_cut_lines")
    color = [i/255 for i in list(dpg.get_value("color_picker"))[0:3]]
    blocks_are_vertical = dpg.get_value("radio_btn") == "Сверху"
    thickness = dpg.get_value("thickness_input")
    pattern = dpg.get_value("lineedit_pattern")
    
    if (margin < 0):
        dpg.set_value("margin_input", 0)
        return

    if size_part % 4 != 0:
        _round = lambda x: int(x) + (0 if x % 1 >= 0.5 else 1)
        size_part = int(_round(size_part / 4) * 4)
        dpg.set_value("size_part_input", size_part)
        
    if (size_part < 0):
        dpg.set_value("size_part_input", 0)
        return
    
    q_pages = len(app.pdf_imposer.input_doc)
    if q_pages < size_part:
        size_part = q_pages - (q_pages % 4)
        dpg.set_value("size_part_input", size_part)
        return
    
    if (thickness < 0):
        dpg.set_value("thickness_input", 0)
        return
    elif (thickness > 5):
        dpg.set_value("thickness_input", 5)
        return

    if (blocks_are_vertical and (rows % 2 == 1)):
        app.log_message("В указанное количество строк не помещаются блоки по два")
        return

    if (not blocks_are_vertical and (cols % 2 == 1)):
        app.log_message("В указанное количество столбцов не помещаются блоки по два")
        return

    align = (format != app.pdf_imposer.params.format)

    pattern_code = pattern.split()
    if (len(pattern_code) % 2 != 0) or not all(s.isdigit() for s in pattern_code):
        pattern = "4 2"

    pattern = f"[{pattern}] 0"

    app.log_message()
    app.pdf_imposer.update_params(rows=rows, cols=cols, margin=margin,
                                  format=format, show_cut_lines=show_cut_lines,
                                  show_margin_lines=show_margin_lines, 
                                  show_blocks_lines=show_blocks_lines, 
                                  blocks_are_vertical=blocks_are_vertical,
                                  thickness_lines=thickness, color_lines=color, 
                                  dashes_pattern=pattern, quantity_pages_for_part=size_part)
    update_preview(app, align)

def is_ok_output(app):
    path = dpg.get_value("lineedit_output")
    if not path:
        app.log_message()
        return False
    if (not app.is_split_file) and (not is_type(path, "pdf")):
        app.log_message("Файл некорректного типа")
        return False
    return True

def save_as_file(app):
    if app.is_split_file:
        path = FileDialogHelper.save_folder()
        if path is None: return
    else:
        path = FileDialogHelper.save_pdf_file()
        if path is None: return
        if not is_type(path, "pdf"):
            app.log_message("Файл некорректного типа")
            return
    dpg.set_value("lineedit_output", path)
    save_file(app)

def save_file(app):
    if not is_ok_output(app): return
    if app.pdf_path is None:
        app.log_message("Исходный файл не выбран")
        return
    path = dpg.get_value("lineedit_output")
    split = app.is_split_file
    app.pdf_imposer.export_doc(path, split)
    if split: app.log_message("Файлы сохранены")
    else: app.log_message("Файл сохранен")

def split_file(app):
    app.is_split_file = dpg.get_value("split_file_checkbox")

def lineedit_pattern_btn(app):
    pattern = dpg.get_value("lineedit_pattern")
    pattern_code = pattern.split()

    if app.pdf_path is None:
        dpg.set_value("lineedit_pattern", app.pdf_imposer.params.dashes_pattern[1:-3])
        app.log_message("Файл PDF не загружен")
        return

    if (len(pattern_code) % 2 == 0) and all(s.isdigit() for s in pattern_code):
        edit_params(app)
    else:
        app.log_message("Некорректный формат паттерна")

def move_panel(app):
    app.pw_left = not app.pw_left
    update_theme(app, rebuild=True)

def switch_theme(app):
    themes = list(conf.theme.keys())
    app.theme = themes[themes.index(app.theme)-1]
    update_theme(app)

def switch_font(app):
    fonts = get_fonts()
    app.font = fonts[fonts.index(normalize_path(app.font))-1]
    update_theme(app)

def separate(app):
    if app.pdf_path is None:
        app.log_message("Файл PDF не загружен")
        set_default_values(app)
        return
    value = dpg.get_value("separate_checkbox")
    dpg.configure_item("part_options", show=value)
    if not value:
        app.pdf_imposer.params.quantity_pages_for_part = 0
    else:
        app.pdf_imposer.params.quantity_pages_for_part = \
            dpg.get_value("size_part_input")
    update_preview(app)

def edit_scale(app, sender):
    scale = float(dpg.get_item_label(sender))
    app.scale = scale
    dpg.hide_item("context_menu")
    #update_theme(app, rebuild=True)
    app.on_exit()

def register_callbacks(app):
    dpg.set_item_callback("lineedit_input_file", lambda: is_ok_input_file(app))
    dpg.set_item_callback("load_file_btn", lambda: load_file(app))
    dpg.set_item_callback("open_file_btn", lambda: open_file(app))
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
    dpg.set_item_callback("lineedit_output", lambda: is_ok_output(app))
    dpg.set_item_callback("save_as_file_btn", lambda: save_as_file(app))
    dpg.set_item_callback("save_file_btn", lambda: save_file(app))
    dpg.set_item_callback("split_file_checkbox", lambda: split_file(app))
    dpg.set_item_callback("thickness_input", lambda: edit_params(app))
    dpg.set_item_callback("lineedit_pattern", lambda: lineedit_pattern_btn(app))
    dpg.set_item_callback("move_panel_btn", lambda: move_panel(app))
    dpg.set_item_callback("switch_theme_btn", lambda: switch_theme(app))
    dpg.set_item_callback("switch_font_btn", lambda: switch_font(app))
    dpg.set_item_callback("combo_formats", lambda: edit_params(app))
    dpg.set_item_callback("separate_checkbox", lambda: separate(app))
    dpg.set_item_callback("size_part_input", lambda: edit_params(app))
    for det in range(150, 300, 25):
        btn = f"scale_{det/100}_btn"
        dpg.set_item_callback(
            btn, lambda s, a, d: 
            edit_scale(app, s)
        )