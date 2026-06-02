
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
        total_sheets = (len(self.input_doc) + pages_per_sheet - 1) // pages_per_sheet

        for sheet_num in range(total_sheets):
            page = self.output_doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        
            for row in range(self.params.rows):
                for col in range(self.params.cols):
                    index = sheet_num * pages_per_sheet + row * self.params.cols + col

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

    def export_doc(self, path):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        self.output_doc.save(path)