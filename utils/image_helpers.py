import dearpygui.dearpygui as dpg


_data = None
_scale = None
_textures_register = []

def _clean_paper(width, height):
    return [220, 220, 220, 255] * (width * height)

def create_preview_textures(papers_data, scale=1):
    global _data, _scale, _textures_register
    if dpg.does_item_exist("preview_textures"):
        return
    _data, _scale = dict(), scale
    with dpg.texture_registry(tag="preview_textures"):
        _textures_register.append("preview_textures")
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

def get_dynamic_textures(image_datas):
    global _textures_register
    texture_registry_tag = dpg.generate_uuid()
    _textures_register.append(texture_registry_tag)

    textures = []
    with dpg.texture_registry(tag=texture_registry_tag):
        for img_data, size in image_datas:
            textures.append(
                dpg.add_dynamic_texture(*size, img_data)
            )

    return textures

def update_texture(tag, img_data=None, size=None):
    global _data
    if size is None:
        size = _data[tag]
    if img_data is None:
        img_data = [220, 220, 220, 255] * (size[0] * size[1])
    if dpg.does_item_exist("preview_pdf"):
        dpg.configure_item("preview_pdf", texture_tag=tag, bounds_max=size)
    if dpg.does_item_exist(tag):
        dpg.set_value(tag, img_data)

def delete_textures():
    global _textures_register
    for texture_registry in _textures_register:
        if dpg.does_item_exist(texture_registry):
            ...
