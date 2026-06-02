
import fitz
from dataclasses import dataclass

from core.calculate import *


@dataclass
class BookParams:
    rows: int
    cols: int
    margin: int
    cut_lines: bool
    cut_color: tuple[int]
    blocks_are_vertical: bool

class PDFImposer():
    def __init__(self):
        self.input_doc = None
        self.output_doc = None
        self.update_params()

    def __delete__(self, instance):
        if self.input_doc is None: return
        self.input_doc.close()

    def load_doc(self, path):
        self.input_doc = fitz.open(path)
        self.update_doc()

    def update_params(self, rows=2, cols=2, margin=2, cut_lines=True, 
                      cut_color=(0.5, 0.5, 0.5), blocks_are_vertical=False):
        if rows*cols % 2 == 1:
            raise ValueError("Not found blocks of pages")
        if (blocks_are_vertical and (rows % 2 == 1)) or \
            (not blocks_are_vertical and (cols % 2 == 1)):
            raise ValueError("Incorrectly specified blocks_are_vertical")
        self.params = BookParams(rows, cols, margin, cut_lines, cut_color,
                                 blocks_are_vertical)

    def get_preview(self, index):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        ...

    def update_doc(self):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        if self.output_doc:
            self.output_doc.close()
        self.output_doc = fitz.open()

        is_vertical = self.params.blocks_are_vertical
        new_positions = get_positions_pages(len(self.input_doc), is_vertical=is_vertical)
        side0, side1 = [], []
        for i in range(len(new_positions)):
            if (i // 2) % 2 == 0:
                side0.append(new_positions[i])
            else:
                side1.append(new_positions[i])
        

        sheet_num = 0
        while side0 or side1:
            page = self.output_doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        
            def draw_page(row, col, rotate=False):
                index = None
                if sheet_num % 2 == 0:
                    if side0: index = side0.pop(0)
                elif side1: index = side1.pop(0)
                if index not in range(len(self.input_doc)):
                    index = None
                    
                rect = fitz.Rect(
                    get_cords_rect(col, row, self.params.cols, 
                                    self.params.rows, self.params.margin)
                )
            
                if index is not None:
                    if rotate:
                        page.show_pdf_page(rect, self.input_doc, index, 
                                           keep_proportion=True, rotate=180)
                    else: page.show_pdf_page(rect, self.input_doc, index, 
                                             keep_proportion=True)

                if self.params.margin:
                    page.draw_rect(rect, color=self.params.cut_color, 
                                    width=1, dashes="[4 2] 0", fill=None)
                else:
                    v_line = get_cords_vertical_line(col, self.params.cols, self.params.rows)
                    h_line = get_cords_horizontal_line(row, self.params.cols, self.params.rows)
                    page.draw_line(fitz.Point(*v_line[0]), fitz.Point(*v_line[1]),
                                    color=self.params.cut_color, width=1,
                                    dashes="[4 2] 0")
                    page.draw_line(fitz.Point(*h_line[0]), fitz.Point(*h_line[1]),
                                    color=self.params.cut_color, width=1,
                                    dashes="[4 2] 0")

            if is_vertical:
                if sheet_num % 2 == 0:
                    for col in range(self.params.cols):
                        for row in range(self.params.rows):
                            draw_page(row, col)
                else:
                    for col in range(self.params.cols)[::-1]:
                        for row in range(self.params.rows):
                            draw_page(row, col, rotate=True)
            else:      
                for row in range(self.params.rows):
                    for col in range(self.params.cols):
                        draw_page(row, col)
            sheet_num += 1

    def export_doc(self, path):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        self.output_doc.save(path)