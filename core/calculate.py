import numpy as np
import pymupdf as fitz

from enum import IntEnum
from dataclasses import dataclass


class Side(IntEnum):
    LEFT = 0
    TOP = 1
    RIGHT = 2

LEFT = Side.LEFT
TOP = Side.TOP
RIGHT = Side.RIGHT

@dataclass
class BookParams:
    rows: int
    cols: int
    side: Side
    margin: int
    dashes_pattern: str
    thickness_lines: int
    show_cut_lines: bool
    show_margin_lines: bool
    show_blocks_lines: bool
    color_lines: tuple[int, ...]
    page_size: tuple[int, int]
    quantity_pages_for_part: int


_positions_cache = {}

def get_positions_pages(quentity: int, side: Side = Side.LEFT, 
                        _list: list | None = None) -> list:
    """получение списка индексов для расположение в порядке для разреза"""
    cache_key = (quentity, side)
    if cache_key in _positions_cache:
        return _positions_cache[cache_key].copy()
    if _list is None:
        _list = [3, 0, 1, 2]
        if side == Side.RIGHT:
            _list = get_positions_pages(quentity, Side.LEFT)
            _list[::4], _list[2::4] = _list[2::4], _list[::4]
            _list[1::4], _list[3::4] = _list[3::4], _list[1::4]
            _list = _list[::-1]
            _positions_cache[cache_key] = _list.copy()
            return _list
    if quentity <= len(_list):
        if side == Side.TOP:
            _list[2::4], _list[3::4] = _list[3::4], _list[2::4]
        _positions_cache[cache_key] = _list.copy()
        return _list
    ind = _list.index(_list[-4])
    for i in range(4):
        _list.append(_list[ind+i]+2)
    for i in range(len(_list)-4):
        if (i % 4 == 0) or (i % 4 == 3):
            _list[i] += 4
    return get_positions_pages(quentity, side=side, _list=_list)


def get_cell_size(page_size: tuple[int, int], cols: int, rows: int) -> tuple[int, int]:
    """получение размеров ячейки"""
    cell_width = page_size[0] / cols
    cell_height = page_size[1] / rows
    return (cell_width, cell_height)


def get_cords_rect(margin: int, page_size: tuple[int, int],
                   col: int = 0, row: int = 0,
                   cols: int = 1, rows: int = 1) -> tuple[int, int, int, int]:
    """получение области размещения страницы"""
    cell_width, cell_height = get_cell_size(page_size, cols, rows)
    x0 = col * cell_width + margin
    y0 = row * cell_height + margin
    x1 = (col + 1) * cell_width - margin
    y1 = (row + 1) * cell_height - margin

    return (x0, y0, x1, y1)


def get_cords_vertical_line(page_size: tuple[int, int], col: int, 
                            cols: int, rows: int) -> tuple[int, int]:
    """получение координат размещения вертикальной линии сетки"""
    cell_width, _ = get_cell_size(page_size, cols, rows)
    point0 = ((col + 1) * cell_width, 0)
    point1 = ((col + 1) * cell_width, page_size[1])
    return (point0, point1)


def get_cords_horizontal_line(page_size: tuple[int, int], row: int, 
                              cols: int, rows: int) -> tuple[tuple[int, int], ...]:
    """получение координат размещения горизонтальной линии сетки"""
    _, cell_height = get_cell_size(page_size, cols, rows)
    point0 = (0, (row + 1) * cell_height)
    point1 = (page_size[0], (row + 1) * cell_height)
    return (point0, point1)


def get_point_center(rect: fitz.Rect) -> tuple[int, int]:
    return (min(rect.x0, rect.x1) + (rect.x1-rect.x0)//2,
            min(rect.y0, rect.y1) + (rect.y1-rect.y0)//2)


def is_cut_line(cord: int, side: Side, is_row: bool = True) -> bool:
    if is_row:
        return (cord % 2 == 1) or (side == LEFT) or (side == RIGHT)
    else:
        return (cord % 2 == 1) or (side == TOP)


def draw_formatting_page(
        output_page: fitz.Page, params: BookParams, input_doc: fitz.Document, 
        index: int | None, row=None, col=None, drawn_lines: list | None = None, 
        indexation_size: int | None = None, rotate=False) -> list[list[int]]:
    """Отрисовка страницы с форматированием"""
    if drawn_lines is None:
        drawn_lines = [[], []]

    rect_params = {'margin': params.margin, 'page_size': params.page_size}
    if (row is not None) and (col is not None):
        rect_params.update({'col': col, 'row': row, 
                            'cols': params.cols, 'rows': params.rows})
    rect = fitz.Rect(get_cords_rect(**rect_params))

    if index is not None and index not in range(len(input_doc)):
        index = None

    if index is not None:
        if rotate: 
            output_page.show_pdf_page(rect, input_doc, index,
                                      keep_proportion=True, rotate=180)
        else: 
            output_page.show_pdf_page(rect, input_doc, index, 
                                      keep_proportion=True)
        if indexation_size:
            output_page.insert_text(get_point_center(rect), str(index), 
                                    fontsize=indexation_size)

    if params.show_margin_lines and params.margin:
        output_page.draw_rect(rect, color=params.color_lines, 
                              width=params.thickness_lines, fill=None)

    if (row is not None) and (col is not None):
        is_cut_lines = [params.show_cut_lines and is_cut_line(row, params.side, is_row=True),
                        params.show_cut_lines and is_cut_line(col, params.side, is_row=False)]
        cords_of_lines = [
            get_cords_horizontal_line(params.page_size, row, params.cols, params.rows),
            get_cords_vertical_line(params.page_size, col, params.cols, params.rows)]
        for i, cord in enumerate([row, col]):
            if (cord not in drawn_lines[i]) and (is_cut_lines[i] or params.show_blocks_lines):
                output_page.draw_line(*map(lambda p: fitz.Point(*p), cords_of_lines[i]),
                                      color=params.color_lines, width=params.thickness_lines,
                                      dashes=(f"[{params.dashes_pattern}] 0"
                                              if is_cut_lines[i] else None))
                drawn_lines[i].append(cord)
    return drawn_lines


def calculate_texture_data(
        page: fitz.Page, dpi: int,
        page_size: tuple[int, int]
        ) -> tuple[list, tuple[int, int]]:
    zoom = dpi / 72
    target_rect = fitz.Rect(0, 0, *page_size)
    irect = (target_rect * fitz.Matrix(zoom, zoom)).irect
    right_width, right_height = irect.width, irect.height

    scale_x = right_width / page.rect.width
    scale_y = right_height / page.rect.height

    matrix = fitz.Matrix(scale_x, scale_y)
    pix = page.get_pixmap(matrix=matrix, alpha=False)

    width, height = pix.width, pix.height

    if right_width != width or right_height != height:
        print("Sizes are not equel")

    img_array = np.frombuffer(pix.samples, dtype=np.uint8)
    img_array = img_array.reshape(height, width, 3)

    img_float = img_array.astype(np.float32) / 255.0

    if pix.n == 3:
        alpha = np.ones((height, width, 1), dtype=np.float32)
        img_float = np.concatenate([img_float, alpha], axis=2)

    texture_data = img_float.flatten().tolist()

    return texture_data, (width, height)


def calculate_doc(input_doc: fitz.Document, params: BookParams, 
                  page_num=None, indexation_size: int | None = None,
                  ) -> tuple[fitz.Document, int]:
    """Расчёт и создание документа с брошюровкой"""
    if input_doc is None:
        raise ValueError("No PDF document loaded")
    
    page_size = params.page_size
    output_doc = fitz.open()
    
    if params.quantity_pages_for_part and (len(input_doc) < params.quantity_pages_for_part):
        raise ValueError("Incorrectly specified quantity_pages_for_part")
    
    new_positions = []
    if params.quantity_pages_for_part:
        positions_pages = get_positions_pages(params.quantity_pages_for_part, side=params.side)
        for i in range((len(input_doc) - 1) // params.quantity_pages_for_part + 1):
            positions = [params.quantity_pages_for_part*i+page for page in positions_pages]
            new_positions += positions
    else:
        positions_pages = get_positions_pages(len(input_doc), side=params.side)
        new_positions += positions_pages
        
    side0, side1 = [], []
    for i in range(len(new_positions)):
        if (i // 2) % 2 == 0:
            side0.append(new_positions[i])
        else:
            side1.append(new_positions[i])

    sheet_num = 0

    def get_index():
        nonlocal sheet_num
        index = None
        if sheet_num % 2 == 1:
            if side0: index = side0.pop(0)
        elif side1: index = side1.pop(0)
        if index not in range(len(input_doc)):
            index = None
        return index
    
    while side0 or side1:
        sheet_num += 1

        if (page_num is None) or (page_num == sheet_num):
            page = output_doc.new_page(width=page_size[0], height=page_size[1])
            
        drawn_lines = [[], []]
        if params.side == TOP:
            if sheet_num % 2 == 1:
                for col in range(params.cols):
                    for row in range(params.rows):
                        index = get_index()
                        if (page_num is None) or (page_num == sheet_num):
                            drawn_lines = draw_formatting_page(
                                page, params, input_doc, index, row, col, 
                                drawn_lines, indexation_size
                            )
            else:
                for col in range(params.cols)[::-1]:
                    for row in range(params.rows):
                        index = get_index()
                        if (page_num is None) or (page_num == sheet_num):
                            drawn_lines = draw_formatting_page(
                                page, params, input_doc, index, row, col,
                                drawn_lines, indexation_size, rotate=True
                            )
        else:
            for row in range(params.rows):
                for col in range(params.cols):
                    index = get_index()
                    if (page_num is None) or (page_num == sheet_num):
                        drawn_lines = draw_formatting_page(
                            page, params, input_doc, index, row, col, 
                            drawn_lines, indexation_size
                        )
    
    if (page_num is not None) and (page_num > sheet_num):
        raise ValueError("Not found page #{n}".format(n=page_num))
    
    return output_doc, sheet_num