
import numpy as np
import threading
import uuid
import os

from core.calculate import *
import core.config as conf


class PDFImposer():
    def __init__(self):
        self.input_doc = None
        self.output_doc = None
        self.quantity_page = None

        self._current_task = None
        self._cancel_flag = threading.Event()
        self._lock = threading.Lock()
        self._current_task_id = None

        self.update_params()

    def __del__(self):
        if self.input_doc is None: 
            return
        self.input_doc.close()

        if self.output_doc:
            try:
                self.output_doc.close()
            except:
                pass

    def load_doc(self, path, callback=None):
        self._cancel_async_task()
        
        if self.input_doc:
            self.input_doc.close()
        self.input_doc = fitz.open(path)
        self.update_doc_async(callback)

    def update_params(self, rows=2, cols=2, margin=15, format="A4_portrait",
                      show_cut_lines=True, show_margin_lines=True, 
                      show_blocks_lines=False, thickness_lines=1, 
                      color_lines=(0.5, 0.5, 0.5), dashes_pattern="[4 2] 0", 
                      blocks_are_vertical=False, quantity_pages_for_part=0):
        if rows*cols % 2 == 1:
            raise ValueError("Not found blocks of pages")
        if (blocks_are_vertical and (rows % 2 == 1)) or \
            (not blocks_are_vertical and (cols % 2 == 1)):
            raise ValueError("Incorrectly specified blocks_are_vertical")
        q = quantity_pages_for_part
        if (q < 0) or (q % 4 != 0):
            raise ValueError("Incorrectly specified quantity_pages_for_part")
        self.params = BookParams(rows, cols, margin, format, show_cut_lines,
                                 show_margin_lines, show_blocks_lines,
                                 thickness_lines, color_lines, dashes_pattern,
                                 blocks_are_vertical, quantity_pages_for_part)

    def get_preview(self, page_num, scale=1):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        if self.output_doc is None and self._current_task and self._current_task.is_alive():
            self._current_task.join()
        
        temp_doc, total_pages = calculate_doc(self.input_doc, self.params, page_num=page_num)
        self.quantity_page = total_pages

        if temp_doc is None or len(temp_doc) == 0:
            return None, None
        
        try:
            page = temp_doc[0]

            right_width, right_height = conf.formats[self.params.format]
            right_width = int(right_width * scale)
            right_height = int(right_height * scale)
            
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
            
        finally:
            try: 
                if temp_doc: temp_doc.close()
            except: pass

    def update_doc(self):
        if self._current_task and self._current_task.is_alive():
            self._current_task.join()
            return
        
        self.output_doc, total_pages = calculate_doc(self.input_doc, self.params)
        self.quantity_page = total_pages

    def _get_split(self):
        output_1 = fitz.open()
        output_2 = fitz.open()

        for i in range(0, self.quantity_page, 2):
            ind_1, ind_2 = i, self.quantity_page-i-1
            output_1.insert_pdf(self.output_doc, from_page=ind_1, to_page=ind_1)
            output_2.insert_pdf(self.output_doc, from_page=ind_2, to_page=ind_2)
        
        return output_1, output_2

    def export_doc(self, path, split=False):
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        self.update_doc()
        if split:
            name = path.split(os.sep)[-1]
            if not os.path.exists(path): 
                os.mkdir(path)
            output_docs = self._get_split()
            for i, output in enumerate(output_docs):
                name_pdf = f"{name}_{i}.pdf"
                output.save(os.sep.join([path, name_pdf]), garbage=4, deflate=True)
                output.close()
        else:
            self.output_doc.save(path, garbage=4, deflate=True)

    def get_preview_async(self, page_num, scale=1, callback=None):
        def worker():
            try:
                result = self.get_preview(page_num, scale)
                if callback:
                    callback(result)
            except Exception as e:
                if callback:
                    callback(None)
        
        thread = threading.Thread(target=worker, daemon=False)
        thread.start()

    def update_doc_async(self, callback=None):
        """
        Асинхронное обновление. Заменяет предыдущую задачу.
        callback вызывается с (success: bool, error: str)
        """
        if self.input_doc is None:
            if callback:
                callback(False, "No PDF document loaded")
            return
        
        self._cancel_async_task()
        
        task_id = str(uuid.uuid4())
        self._current_task_id = task_id
        
        params_copy = self.params
        
        def worker():
            try:
                if self._cancel_flag.is_set() or task_id != self._current_task_id:
                    if callback: callback(False, "Task cancelled")
                    return
                
                output_doc, quantity = calculate_doc(self.input_doc, params_copy)
                
                with self._lock:
                    if task_id == self._current_task_id and not self._cancel_flag.is_set():
                        if self.output_doc:
                            try: self.output_doc.close()
                            except: pass
                        
                        self.output_doc = output_doc
                        self.quantity_page = quantity
                        
                        if callback: callback(True, None)
                    else: output_doc.close()
                        
            except Exception as e:
                if callback: callback(False, str(e))
            finally:
                with self._lock:
                    if task_id == self._current_task_id:
                        self._current_task = None
        
        self._cancel_flag.clear()
        self._current_task = threading.Thread(target=worker, daemon=False)
        self._current_task.start()

    def _cancel_async_task(self):
        if self._current_task and self._current_task.is_alive():
            self._cancel_flag.set()

    def wait_for_completion(self, timeout=None):
        if self._current_task is None:
            return True
        
        if self._current_task.is_alive():
            self._current_task.join(timeout=timeout)
        
        if self._current_task is not None:
            return not self._current_task.is_alive()
        return True
    
    def is_processing(self):
        return self._current_task is not None and self._current_task.is_alive()
    
    def get_formats(self):
        return list(conf.formats.keys())