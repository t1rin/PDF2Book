import numpy as np

from core.calculate import *


class PDFImposer():
    def __init__(self):
        self.input_doc = None
        self.output_doc = None
        self.quantity_page = None
        self.update_params()

    def __del__(self):
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

    def get_preview(self, page_num, scale=1):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        temp, q = calculate_doc(self.input_doc, self.params, page_num=page_num)
        self.quantity_page = q
        
        if temp is None or len(temp) == 0:
            return None, None
        
        try:
            page = temp[0]
            
            matrix = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=matrix, alpha=True)
            
            width, height = pix.width, pix.height
            
            img_array = np.frombuffer(pix.samples, dtype=np.uint8)
            img_array = img_array.reshape(height, width, pix.n)
            
            img_float = img_array.astype(np.float32) / 255.0
            
            if pix.n == 3:
                alpha = np.ones((height, width, 1), dtype=np.float32)
                img_float = np.concatenate([img_float, alpha], axis=2)
            
            texture_data = img_float.flatten().tolist()
            
            return texture_data, (width, height)
            
        finally:
            try: 
                if temp: temp.close()
            except: pass

    def update_doc(self):
        self.output_doc, q = calculate_doc(self.input_doc, self.params)
        self.quantity_page = q

    def export_doc(self, path):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        self.output_doc.save(path, garbage=4, deflate=True)