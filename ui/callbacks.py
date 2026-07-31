import dearpygui.dearpygui as dpg

from utils import *
from ui import MODE, SIDE, RULE
from core.config import formats as formats_sizes


BLOCK_SIZE = 4

def require_pdf(func):
    def wrapper(app, *args, **kwargs):
        if app.pdf_path:
            app.message()
        if app.pdf_path is None:
            app.message("Файл PDF не загружен", mood=False)
            set_values(app)
            return
        return func(app, *args, **kwargs)
    return wrapper

# __ Updating and setting __

def update(app, align=False):
    match app.mode:
        case MODE.PREVIEW:
            update_preview(app, align)
        case MODE.VISUALIZATION:
            update_visualization(app)  
            if app.scene.visual_book.need_reload:
                app.scene.visual_book.load_textures(_get_textures(app))
                app.scene.visual_book.need_reload = False
            update_visualization(app)        

@require_pdf
def update_preview(app, align=False):
    texture_tag = app.pdf_imposer.params.format
    indexation_size = (app.conf.default_indexation_size 
                       if app.is_indexation else 0)
    img_data, _ = app.pdf_imposer.get_preview(page_num=app.current_page, 
                                              scale=app.scale, 
                                              indexation_size=indexation_size)
    app.texture_manager.update_preview_texture(texture_tag, img_data=img_data)
    if align:
        dpg.fit_axis_data("x_axis")
        dpg.fit_axis_data("y_axis")
    if app.pdf_imposer.output_doc is not None:
        dpg.set_value("quantity_page_label", app.pdf_imposer.quantity_page)

def update_visualization(app):
    camera_pos = app.scene.camera.get_position()
    sheets_vertices = app.scene.visual_book.solve_visualization(camera_pos)

    cache = app.scene.visual_book.cache_planes
    cache_index = 0

    for sheet in sheets_vertices:
        vertices = sheet["vertices"]
        texture_tag = sheet["texture"]
        uv_coords = sheet["uv_coords"]

        quad_params = {
            'p1': vertices[0], 'p2': vertices[1],
            'p3': vertices[2], 'p4': vertices[3],
            'uv1': uv_coords[0], 'uv2': uv_coords[1], 
            'uv3': uv_coords[2], 'uv4': uv_coords[3],
            'parent': "plane_node", 'texture_tag': texture_tag
        }

        if cache_index < len(cache):
            if dpg.does_item_exist(item := cache[cache_index]):
                dpg.configure_item(item=item, show=True, **quad_params)
            else:
                dpg.draw_image_quad(tag=item, **quad_params)
        else:
            item = dpg.draw_image_quad(**quad_params)
            cache.append(item)
        cache_index += 1

    while cache_index < len(cache):
        dpg.configure_item(item=cache[cache_index], show=False)
        cache_index += 1

    if app.pdf_imposer.input_doc is not None:
        dpg.set_value("quantity_source_page_label", 
                      len(app.pdf_imposer.input_doc))

    app.scene.update()

def reset_visual_book(app):
    q_parts, q_blocks = _calculate_parts_blocks(
        q_pages=len(app.pdf_imposer.input_doc), 
        size_part=app.pdf_imposer.params.quantity_pages_for_part)
    format_size = formats_sizes[app.pdf_imposer.params.format]
    blocks_are_vertical = app.pdf_imposer.params.blocks_are_vertical
    side = SIDE.TOP if blocks_are_vertical else SIDE.LEFT
    
    app.scene.visual_book.new_book(q_parts, q_blocks, format_size, side)
    app.scene.visual_book.need_reload = True
    app.scene.visual_book.active_block = (0, 0)

    _set_values_of_visualization(app)

def _get_textures(app):
    q_pages = len(app.pdf_imposer.input_doc)
    format = app.pdf_imposer.params.format
    index_format = list(formats_sizes.keys()).index(format)
    cache_textures = app.scene.visual_book.cache_textures[index_format]

    index = 0
    textures = []
    datas_for_creating = []
    while index < min(q_pages, len(cache_textures)):
        img_data, _ = app.pdf_imposer.get_formatted_source_page(
            page_num=index, scale=app.scale)
        texture = cache_textures[index]
        app.texture_manager.update_dynamic_texture(texture, img_data=img_data)
        textures.append(texture)
        index += 1
    while index < q_pages:
        datas_for_creating.append(app.pdf_imposer.get_formatted_source_page(
            page_num=index, scale=app.scale))
        index += 1
    if datas_for_creating:
        texture_register = app.texture_manager.create_dynamic_textures(datas_for_creating)
        new_textures = app.texture_manager.get_dynamic_textures(texture_register)
        cache_textures += new_textures
        textures += new_textures
        
    return textures

# __ Working with files __

def load_file(app):
    path = dpg.get_value("lineedit_input_file")
    _, err = PDFInfo.validate_and_get_info(path)
    app.message(err, mood=False)
    if err: return

    def on_loading(success, error):
        if success:
            reset_visual_book(app)
            update(app, align=True)
            set_values(app)
            app.message("Файл успешно загружен", mood=True)
        else:
            app.pdf_path = None
            app.message(error, mood=False)

    app.pdf_path = path
    app.pdf_imposer.update_params()
    app.pdf_imposer.load_doc(path, on_loading)

def open_file(app):
    path = FileDialogHelper.open_pdf_file()
    if path is None: return
    _, err = PDFInfo.validate_and_get_info(path)
    app.message(err, mood=False)
    if not err:
        dpg.set_value("lineedit_input_file", path)
        load_file(app)
        
def drop_handler(app, data):
    path = data[0]
    if path is None: return
    _, err = PDFInfo.validate_and_get_info(path)
    app.message(err, mood=False)
    if not err:
        dpg.set_value("lineedit_input_file", path)
        load_file(app)

def save_as_file(app):
    if app.is_split_file:
        path = FileDialogHelper.save_folder()
        if path is None: return
    else:
        path = FileDialogHelper.save_pdf_file()
        if path is None: return
        if not is_type(path, "pdf"):
            app.message("Файл некорректного типа")
            return
    dpg.set_value("lineedit_output", path)
    save_file(app)

@require_pdf
def save_file(app):
    messages = []
    path = dpg.get_value("lineedit_output")

    if path and not app.is_split_file and not is_type(path, "pdf"):
        messages.append("Файл некорректного типа")
        path = None
    if path and app.is_split_file and not is_directory(path):
        messages.append("Путь не директория")
        path = None
    
    if not path:
        source_dir, source_name = split_path(app.pdf_path)
        if app.is_split_file:
            path = join_path(source_dir, f"book_{source_name}")
        else:
            path = join_path(source_dir, f"book_{source_name}.pdf")
        dpg.set_value("lineedit_output", path)
        messages.append(f"Путь автоматически установлен: {path}")

    app.pdf_imposer.export_doc(path, app.is_split_file)

    messages.append("Файлы сохранены" if app.is_split_file else "Файл сохранен")
    app.message(messages, mood=True)

def split_file(app):
    app.is_split_file = dpg.get_value("split_file_checkbox")

@require_pdf
def open_input_folder(app):
    path = dpg.get_value("lineedit_input_file")

    if not start_path(path):
        app.message(f"Папка не существует", mood=False)

@require_pdf
def open_output_folder(app):
    path = dpg.get_value("lineedit_output")
    if not path:
        app.message("Файл не был сохранён", mood=False)
        return
    
    if not start_path(path):
        app.message(f"Папка не существует", mood=False)

# __ Working with params __

def set_values(app):
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
    dpg.set_value("indexes_pages_checkbox", app.is_indexation)
    dpg.configure_item("part_options", show=bool(app.pdf_imposer.params.quantity_pages_for_part))

    items = [*formats_sizes.keys()]
    dpg.configure_item("combo_formats", items=items)
    dpg.set_value("combo_formats", app.pdf_imposer.params.format)

    _set_values_of_modes(app)
    _set_values_of_visualization(app)

def _set_values_of_modes(app):
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

def _set_values_of_visualization(app):
    if app.pdf_imposer.input_doc is not None:
        q_parts = app.scene.visual_book.get('q_parts')
        q_blocks = app.scene.visual_book.get('q_blocks')
        dpg.configure_item("combo_parts", items=list(range(q_parts)))
        dpg.configure_item("combo_blocks", items=list(range(q_blocks)))

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

@require_pdf
def edit_params(app):
    params = {
        'rows': dpg.get_value("rows_input"),
        'cols': dpg.get_value("cols_input"),
        'margin': dpg.get_value("margin_input"),
        'format': dpg.get_value("combo_formats"),
        'show_cut_lines': dpg.get_value("show_cut_lines"),
        'show_margin_lines': dpg.get_value("show_margin_lines"),
        'show_blocks_lines': dpg.get_value("show_blocks_lines"),
        'quantity_pages_for_part': dpg.get_value("size_part_input"),
        'color_lines': [i/255 for i in list(dpg.get_value("color_picker"))[0:3]],
        'blocks_are_vertical': dpg.get_value("radio_btn") == "Сверху",
        'thickness_lines': dpg.get_value("thickness_input"),
        'dashes_pattern': dpg.get_value("lineedit_pattern"),
    }
    
    if not (_validate_params(app, params) and _is_size_part_normal(app, params)):
        return
    
    params['dashes_pattern'] = _prepare_pattern(app, params['dashes_pattern'])

    app.message()
    app.pdf_imposer.update_params(**params)

    q_parts, q_blocks = _calculate_parts_blocks(
        q_pages=len(app.pdf_imposer.input_doc),
        size_part=params['quantity_pages_for_part'])
    page_size = formats_sizes[params['format']]
    side = SIDE.TOP if params['blocks_are_vertical'] else SIDE.LEFT

    if app.scene.visual_book.get('page_size') != page_size:
        default_texture = app.texture_manager.get_clean_texture(params['format'])
        app.scene.visual_book.set(default_texture=default_texture)
    if (app.scene.visual_book.get('page_size') != page_size or
        app.scene.visual_book.get('q_parts') != q_parts or
        app.scene.visual_book.get('q_blocks') != q_blocks or
        app.scene.visual_book.get('side') != side):
        reset_visual_book(app)

    align = (params['format'] != app.pdf_imposer.params.format)
    app.scene.visual_book.need_reload = True
    update(app, align=align)

def _is_size_part_normal(app, params):
    q_pages = len(app.pdf_imposer.input_doc)
    if q_pages < params['quantity_pages_for_part']:
        params['quantity_pages_for_part'] = q_pages - (q_pages % BLOCK_SIZE)
        dpg.set_value("size_part_input", params['quantity_pages_for_part'])
        return False
    if params['quantity_pages_for_part'] < 0:
        params['quantity_pages_for_part'] = 0
        dpg.set_value("size_part_input", params['quantity_pages_for_part'])
        return False
    return True

def _validate_params(app, params):
    if params['rows'] <= 0:
        dpg.set_value("rows_input", 1)
        return False
    if params['cols'] <= 0:
        dpg.set_value("cols_input", 1)
        return False
    if params['margin'] < 0:
        dpg.set_value("margin_input", 0)
        return False
    if params['quantity_pages_for_part'] < 0:
        dpg.set_value("size_part_input", 0)
        return False
    if params['thickness_lines'] < 0:
        dpg.set_value("thickness_input", 0)
        return False
    if params['thickness_lines'] > app.conf.max_line_thickness:
        dpg.set_value("thickness_input", app.conf.max_line_thickness)
        return False
    if params['blocks_are_vertical'] and (params['rows'] % 2 == 1):
        app.message(
            content="В указанное количество строк не помещаются блоки по два", 
            mood=False)
        return False
    if not params['blocks_are_vertical'] and (params['cols'] % 2 == 1):
        app.message(
            content="В указанное количество столбцов не помещаются блоки по два", 
            mood=False)
        return False
    return True

def _prepare_pattern(app, pattern):
    pattern_code = pattern.split()
    if (len(pattern_code) % 2 != 0) or not all(s.isdigit() for s in pattern_code):
        pattern = app.conf.default_pattern
    return f"[{pattern}] 0"
    
def _calculate_parts_blocks(q_pages, size_part):
    if size_part:
        q_parts = ((q_pages - 1) // size_part + 1)
        q_blocks = size_part // BLOCK_SIZE
    else:
        q_parts = 1
        q_blocks = ((q_pages - 1) // BLOCK_SIZE + 1)
    return q_parts, q_blocks

# __ Callbacks __

@require_pdf
def arrow_left_callback(app):
    if (app.current_page == 1): 
        return
    dpg.set_value("page_label", int(dpg.get_value("page_label"))-1)
    app.current_page -= 1
    update(app)

@require_pdf
def arrow_right_callback(app):
    if (app.pdf_imposer.output_doc is not None) and \
        (app.current_page == app.pdf_imposer.quantity_page): 
        return
    dpg.set_value("page_label", int(dpg.get_value("page_label"))+1)
    app.current_page += 1
    update(app)

@require_pdf
def selection_block(app):
    part_index = int(dpg.get_value("combo_parts"))
    block_index = int(dpg.get_value("combo_blocks"))
    alpha = app.scene.visual_book.get('alpha', part_index, block_index)
    beta = app.scene.visual_book.get('beta', part_index, block_index)
    dpg.set_value("alpha_input", alpha)
    dpg.set_value("beta_input", beta)
    dpg.set_value("active_block_label", f"({part_index}, {block_index})")
    app.scene.visual_book.active_block = (part_index, block_index)

@require_pdf
def edit_visualization(app):
    part_index = int(dpg.get_value("combo_parts"))
    block_index = int(dpg.get_value("combo_blocks"))
    alpha = dpg.get_value("alpha_input")
    beta = dpg.get_value("beta_input")
    if app.scene.visual_book.get('alpha', part_index, block_index) != alpha or \
       app.scene.visual_book.get('beta', part_index, block_index) != beta:
        app.scene.visual_book.set(part_index=part_index, 
                                  block_index=block_index, 
                                  alpha=alpha, beta=beta)
    update(app)

def check_lineedit_pattern(app):
    pattern = dpg.get_value("lineedit_pattern")
    pattern_code = pattern.split()

    if app.pdf_path is None:
        dpg.set_value("lineedit_pattern", app.pdf_imposer.params.dashes_pattern[1:-3])
        app.message("Файл PDF не загружен", mood=False)
        return

    if (len(pattern_code) % 2 == 0) and all(s.isdigit() for s in pattern_code):
        edit_params(app)
    else:
        app.message("Некорректный формат паттерна", mood=False)

def move_panel(app):
    app.pw_left = not app.pw_left
    app.create_ui()

def switch_theme(app):
    themes = list(app.conf.themes.keys())
    app.theme = themes[themes.index(app.theme)-1]
    app.theme_manager.update()

def switch_font(app):
    fonts = get_fonts()
    app.font = fonts[fonts.index(normalize_path(app.font))-1]
    app.theme_manager.update()

def switch_mode(app, mode):
    if mode == "preview": app.mode = MODE.PREVIEW
    if mode == "visualization": app.mode = MODE.VISUALIZATION
    _set_values_of_modes(app)
    update(app)

@require_pdf
def separate(app):
    value = dpg.get_value("separate_checkbox")
    dpg.configure_item("part_options", show=value)
    if not value:
        app.pdf_imposer.params.quantity_pages_for_part = 0
    else:
        app.pdf_imposer.params.quantity_pages_for_part = \
            dpg.get_value("size_part_input")
    if app.pdf_imposer.params.quantity_pages_for_part != \
       app.scene.visual_book.get('q_blocks') * BLOCK_SIZE:
        reset_visual_book(app)
    update(app)

@require_pdf
def edit_indexation(app):
    app.is_indexation = dpg.get_value("indexes_pages_checkbox")
    update(app)

def edit_scale(app, sender):
    scale = float(dpg.get_item_label(sender))
    app.scale = scale
    app.create_ui()

def reset_to_home(app):
    app.scene.camera.home()
    app.scene.update()

def show_visual_settings(app):
    dpg.configure_item("visualization_tab", show=True)
    dpg.set_value("tab_bar", "visualization_tab")
    dpg.configure_item("detailed_visual_properties_btn", show=False)

def register_callbacks(app):
    callbacks = {
        "open_file_btn": lambda: open_file(app),
        "arrow_left": lambda: arrow_left_callback(app),
        "arrow_right": lambda: arrow_right_callback(app),
        "rows_input": lambda: edit_params(app),
        "cols_input": lambda: edit_params(app),
        "margin_input": lambda: edit_params(app),
        "show_margin_lines": lambda: edit_params(app),
        "show_blocks_lines": lambda: edit_params(app),
        "show_cut_lines": lambda: edit_params(app),
        "color_picker": lambda: edit_params(app),
        "radio_btn": lambda: edit_params(app),
        "save_as_file_btn": lambda: save_as_file(app),
        "save_file_btn": lambda: save_file(app),
        "split_file_checkbox": lambda: split_file(app),
        "thickness_input": lambda: edit_params(app),
        "lineedit_pattern": lambda: check_lineedit_pattern(app),
        "move_panel_btn": lambda: move_panel(app),
        "switch_theme_btn": lambda: switch_theme(app),
        "switch_font_btn": lambda: switch_font(app),
        "combo_formats": lambda: edit_params(app),
        "separate_checkbox": lambda: separate(app),
        "size_part_input": lambda: edit_params(app),
        "indexes_pages_checkbox": lambda: edit_indexation(app),
        "preview_mode_button": lambda _, __, d: switch_mode(app, d),
        "visualization_mode_button": lambda _, __, d: switch_mode(app, d),
        "detailed_visual_properties_btn": lambda: show_visual_settings(app),
        "reset_to_home_btn": lambda: reset_to_home(app),
        "combo_parts": lambda: selection_block(app),
        "combo_blocks": lambda: selection_block(app),
        "alpha_input": lambda: edit_visualization(app),
        "beta_input": lambda: edit_visualization(app),
        "open_input_folder_btn": lambda: open_input_folder(app),
        "open_output_folder_btn": lambda: open_output_folder(app),
    }

    for det in range(100, 300, 25):
        callbacks[f"scale_{det/100}_btn"] = lambda s, a, d: edit_scale(app, s)

    for item, callback in callbacks.items():
        dpg.set_item_callback(item, callback)
