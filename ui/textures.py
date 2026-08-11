from __future__ import annotations
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg
import pymupdf as fitz
import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from main import PDF2BookApp



class TextureManager:
    def __init__(self, app: PDF2BookApp) -> None:
        self.app: PDF2BookApp = app
        self._formats: dict[str, tuple[int, int]] = app.conf.formats

        self._registers_and_textures: dict[str | int, list[str | int]] = dict()

        self.start()

    def start(self):
        self.create_preview_textures()
        images_datas = self._get_datas_using_formats()['images_datas']
        self.create_dynamic_textures(
            images_datas, texture_register="visual_textures")

    def _clean_img_data(self, width: int, height: int) -> NDArray:
        return np.array([220, 220, 220, 255] * (width * height), dtype=np.uint8)
    
    def _get_scaled_size(self, size: tuple[int, int]) -> tuple[int, int]:
        zoom = self.app.conf.dpi / 72
        rect = fitz.Rect(0, 0, *size)
        irect = (rect * fitz.Matrix(zoom, zoom)).irect
        return (irect.width, irect.height)

    def _get_datas_using_formats(self) -> dict:
        images_datas = []
        for size in self._formats.values():
            scaled_size = self._get_scaled_size(size)
            img_data = self._clean_img_data(*scaled_size)
            images_datas.append((img_data, scaled_size))
        textures_tags = [*self._formats.keys()]
        return {'images_datas': images_datas, 'textures_tags': textures_tags}

    def create_preview_textures(self) -> None:
        params = self._get_datas_using_formats()
        self.create_dynamic_textures(
            **params, texture_register="preview_textures")
        
    def create_dynamic_textures(
            self, images_datas: list[tuple[NDArray, tuple[int, int]]],
            textures_tags: list[str | int] | None = None,
            texture_register: str | int | None = None
            ) -> str | int | None:
        if texture_register:
            if not dpg.does_item_exist(texture_register):
                texture_register_tag = texture_register
            else:
                return None
        else: texture_register_tag = dpg.generate_uuid()

        if textures_tags and len(textures_tags) != len(images_datas):
            return None

        textures = []
        with dpg.texture_registry(tag=texture_register_tag):
            for index in range(len(images_datas)):
                img_data, size = images_datas[index]
                tag: str | int = 0
                if textures_tags and not dpg.does_item_exist(textures_tags[index]):
                    tag = textures_tags[index]
                texture = dpg.add_dynamic_texture(*size, img_data, tag=tag)
                textures.append(texture)
        self._registers_and_textures[texture_register_tag] = textures

        return texture_register_tag
    
    def get_dynamic_textures(
            self, texture_register: str | int) -> list[str | int]:
        textures = []
        if texture_register in self._registers_and_textures:
            textures = self._registers_and_textures[texture_register]
        return textures
             
    def get_preview_data(
            self, format_size: tuple[int, int], only_size: bool = False
            ) -> tuple[NDArray | None, tuple[int, int] | None]:
        if format_size not in self._formats.values():
            return None, None
        scaled_size = self._get_scaled_size(format_size)
        if only_size:
            return None, scaled_size
        img_data = self._clean_img_data(*scaled_size)
        return img_data, scaled_size

    def get_clean_texture(self, format_size: tuple[int, int]) -> str | int:
        sizes = list(self._formats.values())
        if format_size not in sizes:
            raise ValueError("Uncorrectly format size")
        index = sizes.index(format_size)
        textures = self.get_dynamic_textures("visual_textures")
        return textures[index]

    def update_preview_texture(self, format_name: str, 
                       img_data: NDArray | None = None, 
                       size: tuple[int, int] | None = None) -> None:
        if size is None:
            size = self._get_scaled_size(self._formats[format_name])
        if img_data is None:
            img_data = self._clean_img_data(*size)
        if dpg.does_item_exist("preview_pdf"):
            dpg.configure_item("preview_pdf", 
                               texture_tag=format_name, 
                               bounds_max=size)
        self.update_dynamic_texture(tag=format_name, img_data=img_data)

    def update_dynamic_texture(self, tag: str | int, img_data: NDArray) -> None:
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, img_data)

    def delete_textures(self, texture_register: str | int | None = None) -> None:
        registers_to_delete = []
        if texture_register:
            registers_to_delete.append(texture_register)
        else:
            all_registers = list(self._registers_and_textures.keys())
            registers_to_delete.extend(all_registers)
        
        for register in registers_to_delete:
            if dpg.does_item_exist(register):
                textures = self._registers_and_textures.get(register, [])
                for texture in textures:
                    if dpg.does_item_exist(texture):
                        dpg.delete_item(texture)
                
                dpg.delete_item(register)
                
                if register in self._registers_and_textures:
                    del self._registers_and_textures[register]