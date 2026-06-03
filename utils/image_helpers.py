import dearpygui.dearpygui as dpg
import fitz

PAGE_WIDTH = 595
PAGE_HEIGHT = 842

   
def get_dynamic_texture(width, height, data, tag):
    while dpg.does_item_exist(tag):
        dpg.delete_item(tag)
    with dpg.texture_registry():
        return dpg.add_dynamic_texture(width, height, data, tag=tag)
    
def get_clean_texture(tag, scale=1):
    width = PAGE_WIDTH * scale
    height = PAGE_HEIGHT * scale

    data = [220, 220, 220, 255] * (width * height)
    
    with dpg.texture_registry():
        texture = get_dynamic_texture(width, height, data, tag=tag)
        return texture, (width, height)
