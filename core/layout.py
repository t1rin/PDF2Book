
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
                      cut_color=(0.5, 0.5, 0.5)):
        self.params = BookParams(rows, cols, margin, cut_lines, cut_color)

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

        pages_per_sheet = self.params.rows * self.params.cols
        if pages_per_sheet % 2 == 1:
            raise ValueError("Not found blocks of pages")

        is_vertical = bool(self.params.cols % 2)
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
        
            def draw_page(row, col, index):
                if index not in range(len(self.input_doc)):
                    return
                
                rect = fitz.Rect(
                    get_cords_rect(col, row, self.params.cols, 
                                    self.params.rows, self.params.margin)
                )
            
                page.show_pdf_page(rect, self.input_doc, index, 
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

            if self.params.cols % 2 == 0:
                for row in range(self.params.rows):
                    for col in range(self.params.cols):
                        if sheet_num % 2 == 0: 
                            if side0: draw_page(row, col, side0.pop(0))
                        elif side1: draw_page(row, col, side1.pop(0))
            else:
                for col in range(self.params.cols):
                    for row in range(self.params.rows):
                        if sheet_num % 2 == 0:
                            if side0: draw_page(row, col, side0.pop(0))
                        elif side1: draw_page(row, col, side1.pop(0))        
            sheet_num += 1

    def export_doc(self, path):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        self.output_doc.save(path)