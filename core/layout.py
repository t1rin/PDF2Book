from core.calculate import *

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

    def get_preview(self, page_num):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        temp = fitz.open()
        temp = calculate_doc(self.input_doc, temp, self.params, page_num=page_num)
        page = temp[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=True)
        img_data = pix.tobytes()
        temp.close()

        return img_data

    def update_doc(self):
        self.output_doc = calculate_doc(self.input_doc, self.output_doc, self.params, page_num=2)

    def export_doc(self, path):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        self.output_doc.save(path, garbage=4, deflate=True)