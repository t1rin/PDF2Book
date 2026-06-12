import dearpygui.dearpygui as dpg


_data = None
_scale = None

def create_dynamic_textures(papers_data, scale=1):
    global _data, _scale
    if dpg.does_item_exist("textures"):
        return
    _data, _scale = dict(), scale
    with dpg.texture_registry(tag="textures"):
        for tag, size in papers_data.items():
            width = int(size[0] * scale)
            height = int(size[1] * scale)
            _data[tag] = (width, height)
            img_data = [220, 220, 220, 255] * (width * height)
            dpg.add_dynamic_texture(width, height, img_data, tag=tag)

def get_dynamic_texture(tag):
    global _data, _scale
    if (_data is None) or (_scale is None) or (tag not in _data.keys()):
        return None, None
    width, height = _data[tag]
    img_data = [220, 220, 220, 255] * (width * height)
    return img_data, (width, height)

def update_texture(tag, img_data):
    if dpg.does_item_exist("preview_pdf"):
        dpg.configure_item("preview_pdf", texture_tag=tag, bounds_max=_data[tag])
    if dpg.does_item_exist(tag):
        dpg.set_value(tag, img_data)
