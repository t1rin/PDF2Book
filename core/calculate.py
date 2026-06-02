

PAGE_WIDTH = 595
PAGE_HEIGHT = 842


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