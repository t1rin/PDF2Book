import dearpygui.dearpygui as dpg


_data = None
_scale = None

def _clean_paper(width, height):
    return [220, 220, 220, 255] * (width * height)

def create_preview_textures(papers_data, scale=1):
    global _data, _scale
    if dpg.does_item_exist("preview_textures"):
        return
    _data, _scale = dict(), scale
    with dpg.texture_registry(tag="preview_textures"):
        for tag, size in papers_data.items():
            _data[tag] = (int(size[0] * scale), int(size[1] * scale))
            img_data = _clean_paper(*_data[tag])
            dpg.add_dynamic_texture(*_data[tag], img_data, tag=tag)

def get_preview_texture(tag, only_size=False):
    global _data, _scale
    if (_data is None) or (_scale is None) or (tag not in _data.keys()):
        return None, None
    if only_size:
        return None, _data[tag]
    return _clean_paper(*_data[tag]), _data[tag]

def create_dynamic_texture(img_data, size, tag=None):
    with dpg.texture_registry(tag="textures"):
        if tag and not dpg.does_item_exist(tag):
            return dpg.add_dynamic_texture(*size, img_data, tag=tag)
        return dpg.add_dynamic_texture(*size, img_data)

def update_texture(tag, img_data=None):
    if img_data is None:
        img_data = [220, 220, 220, 255] * (_data[tag][0] * _data[tag][1])
    if dpg.does_item_exist("preview_pdf"):
        dpg.configure_item("preview_pdf", texture_tag=tag, bounds_max=_data[tag])
    if dpg.does_item_exist(tag):
        dpg.set_value(tag, img_data)
