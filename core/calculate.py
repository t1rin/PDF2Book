import fitz
from dataclasses import dataclass

import core.config as conf


@dataclass
class BookParams:
    rows: int
    cols: int
    margin: int
    format: str
    show_cut_lines: bool
    show_margin_lines: bool
    show_blocks_lines: bool
    thickness_lines: int
    color_lines: tuple[int]
    dashes_pattern: str
    blocks_are_vertical: bool

def get_positions_pages(quentity, is_vertical=False, _list=None):
    """получение списка индексов для расположение в порядке для разреза"""
    if _list is None: _list = [3, 0, 1, 2]
    if quentity <= len(_list):
        if is_vertical:
            _list[2::4], _list[3::4] = _list[3::4], _list[2::4]
        return _list
    ind = _list.index(_list[-4])
    for i in range(4):
        _list.append(_list[ind+i]+2)
    for i in range(len(_list)-4):
        if (i % 4 == 0) or (i % 4 == 3):
            _list[i] += 4
    return get_positions_pages(quentity, is_vertical=is_vertical, _list=_list)

def get_cell_size(cols, rows, page_size):
    """получение размеров ячейки"""
    cell_width = page_size[0] / cols
    cell_height = page_size[1] / rows
    return (cell_width, cell_height)

def get_cords_rect(col, row, cols, rows, margin, page_size):
    """получение области размещения страницы"""
    cell_width, cell_height = get_cell_size(cols, rows, page_size)
    x0 = col * cell_width + margin
    y0 = row * cell_height + margin
    x1 = (col + 1) * cell_width - margin
    y1 = (row + 1) * cell_height - margin

    return (x0, y0, x1, y1)

def get_cords_vertical_line(col, cols, rows, page_size):
    """получение координат размещения вертикальной линии сетки"""
    cell_width, _ = get_cell_size(cols, rows, page_size)
    point0 = ((col + 1) * cell_width, 0)
    point1 = ((col + 1) * cell_width, page_size[1])
    return (point0, point1)

def get_cords_horizontal_line(row, cols, rows, page_size):
    """получение координат размещения горизонтальной линии сетки"""
    _, cell_height = get_cell_size(cols, rows, page_size)
    point0 = (0, (row + 1) * cell_height)
    point1 = (page_size[0], (row + 1) * cell_height)
    return (point0, point1)

def is_cut_line(cord, is_vertical, is_row=True):
    if is_row:
        return (is_vertical and (cord % 2 == 1)) or not is_vertical
    else:
        return (not is_vertical and (cord % 2 == 1)) or is_vertical
    
def calculate_doc(input_doc, params: BookParams, page_num=None):
    if input_doc is None:
        raise ValueError("No PDF document loaded")
    
    page_size = conf.formats[params.format]

    output_doc = fitz.open()

    is_vertical = params.blocks_are_vertical
    new_positions = get_positions_pages(len(input_doc), is_vertical=is_vertical)
    side0, side1 = [], []
    for i in range(len(new_positions)):
        if (i // 2) % 2 == 0:
            side0.append(new_positions[i])
        else:
            side1.append(new_positions[i])

    sheet_num = 0
    drawn_lines = None
    while side0 or side1:
        sheet_num += 1
        
        if (page_num is None) or (page_num == sheet_num):
            page = output_doc.new_page(width=page_size[0], height=page_size[1])

        def get_index():
            index = None
            if sheet_num % 2 == 1:
                if side0: index = side0.pop(0)
            elif side1: index = side1.pop(0)
            if index not in range(len(input_doc)):
                index = None
            return index

        def draw_page(row, col, index, page_size, rotate=False):
            if (page_num is not None) and (page_num != sheet_num):
                return
            
            rect = fitz.Rect(get_cords_rect(col, row, params.cols, 
                                            params.rows, params.margin, page_size))
        
            if index is not None:
                if rotate: page.show_pdf_page(rect, input_doc, index,
                                              keep_proportion=True, rotate=180)
                else: page.show_pdf_page(rect, input_doc, index, 
                                            keep_proportion=True)

            if params.show_margin_lines and params.margin:
                page.draw_rect(rect, color=params.color_lines, 
                               width=params.thickness_lines, fill=None)

                
            is_cut_lines = [params.show_cut_lines and is_cut_line(row, is_vertical, is_row=True),
                            params.show_cut_lines and is_cut_line(col, is_vertical, is_row=False)]
            cords_of_lines = [get_cords_horizontal_line(row, params.cols, params.rows, page_size),
                              get_cords_vertical_line(col, params.cols, params.rows, page_size)]
            for i, cord in enumerate([row, col]):
                if (cord not in drawn_lines[i]) and (is_cut_lines[i] or params.show_blocks_lines):
                    page.draw_line(*map(lambda p: fitz.Point(*p), cords_of_lines[i]),
                                    color=params.color_lines, width=params.thickness_lines,
                                    dashes=(params.dashes_pattern 
                                            if is_cut_lines[i] else None))
                    drawn_lines[i].append(cord)

        drawn_lines = [[], []]
        if is_vertical:
            if sheet_num % 2 == 1:
                for col in range(params.cols):
                    for row in range(params.rows):
                        index = get_index()
                        draw_page(row, col, index, page_size)
            else:
                for col in range(params.cols)[::-1]:
                    for row in range(params.rows):
                        index = get_index()
                        draw_page(row, col, index, page_size, rotate=True)
        else:      
            for row in range(params.rows):
                for col in range(params.cols):
                    index = get_index()
                    draw_page(row, col, index, page_size)
    if (page_num is not None) and (page_num > sheet_num):
        raise ValueError("Not found page #{n}".format(n=page_num))
    
    return output_doc, sheet_num