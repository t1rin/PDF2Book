import dearpygui.dearpygui as dpg



def register_callbacks(app):
    dpg.set_item_callback("lineedit_input_file", lambda: check_path_to_input_file(app))
    dpg.set_item_callback("choice_input_file_btn", lambda: choice_path_to_input_file(app))
    dpg.set_item_callback("load_file_btn", lambda: load_file(app))
    dpg.set_item_callback("rows_input", lambda: edit_params(app))
    dpg.set_item_callback("cols_input", lambda: edit_params(app))
    dpg.set_item_callback("margin_input", lambda: edit_params(app))
    dpg.set_item_callback("show_dividing_line", lambda: edit_params(app))
    dpg.set_item_callback("show_line_with_indentation", lambda: edit_params(app))
    dpg.set_item_callback("color_picker", lambda: edit_params(app))
    dpg.set_item_callback("radio_btn", lambda: edit_params(app))
    dpg.set_item_callback("lineedit_output_file", lambda: check_path_to_output_file(app))
    dpg.set_item_callback("choice_output_file_btn", lambda: choice_path_to_output_file(app))
    dpg.set_item_callback("export_file_btn", lambda: export_file(app))

def check_path_to_input_file(app):
    ...

def choice_path_to_input_file(app):
    ...

def load_file(app):
    ...

def edit_params(app):
    ...

def check_path_to_output_file(app):
    ...

def choice_path_to_output_file(app):
    ...

def export_file(app):
    ...