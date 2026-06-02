

PAGE_WIDTH = 595
PAGE_HEIGHT = 842

def get_positions_pages(quentity, _list=[3, 0, 1, 2]):
    """получение списка индексов для расположение в порядке для разреза"""
    if quentity <= len(_list):
        return _list
    ind = _list.index(_list[-4])
    for i in range(4):
        _list.append(_list[ind+i]+2)
    for i in range(len(_list)-4):
        if (i % 4 == 0) or (i % 4 == 3):
            _list[i] += 4
    return get_positions_pages(quentity, _list)

def get_cell_size(cols, rows):
    """получение размеров ячейки"""
    cell_width = PAGE_WIDTH / cols
    cell_height = PAGE_HEIGHT / rows
    return (cell_width, cell_height)

def get_cords_rect(col, row, cols, rows, margin):
    """получение области размещения страницы"""
    cell_width, cell_height = get_cell_size(cols, rows)
    x0 = col * cell_width + margin
    y0 = row * cell_height + margin
    x1 = (col + 1) * cell_width - margin
    y1 = (row + 1) * cell_height - margin

    return (x0, y0, x1, y1)

def get_cords_vertical_line(col, cols, rows):
    """получение координат размещения вертикальной линии сетки"""
    cell_width, _ = get_cell_size(cols, rows)
    point0 = ((col + 1) * cell_width, 0)
    point1 = ((col + 1) * cell_width, PAGE_HEIGHT)
    return (point0, point1)

def get_cords_horizontal_line(row, cols, rows):
    """получение координат размещения горизонтальной линии сетки"""
    _, cell_height = get_cell_size(cols, rows)
    point0 = (0, (row + 1) * cell_height)
    point1 = (PAGE_WIDTH, (row + 1) * cell_height)
    return (point0, point1)