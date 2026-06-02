
import fitz
from dataclasses import dataclass


PAGE_WIDTH = 595
PAGE_HEIGHT = 842

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

        cell_width = PAGE_WIDTH / self.params.cols
        cell_height = PAGE_HEIGHT / self.params.rows

        page = self.output_doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        page_counter = 0       

        for row in range(self.params.rows):
            for col in range(self.params.cols):
                if page_counter >= len(self.input_doc):
                    break
                
                x0 = col * cell_width + self.params.margin
                y0 = row * cell_height + self.params.margin
                x1 = (col + 1) * cell_width - self.params.margin
                y1 = (row + 1) * cell_height - self.params.margin
                
                rect = fitz.Rect(x0, y0, x1, y1)
            
                page.show_pdf_page(rect, self.input_doc, page_counter, 
                                       keep_proportion=True)

                if self.params.margin:
                    page.draw_rect(rect, color=self.params.cut_color, 
                                       width=1, dashes="[4 2] 0", fill=None)
                else:
                    page.draw_line(fitz.Point((col + 1) * cell_width, 0), 
                                   fitz.Point((col + 1) * cell_width, PAGE_HEIGHT),
                                    color=self.params.cut_color, width=1,
                                    dashes="[4 2] 0")
                    page.draw_line(fitz.Point(0, (row + 1) * cell_height), 
                                   fitz.Point(PAGE_WIDTH, (row + 1) * cell_height),
                                    color=self.params.cut_color, width=1,
                                    dashes="[4 2] 0")

                page_counter += 1

    def export_doc(self, path):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        self.output_doc.save(path)