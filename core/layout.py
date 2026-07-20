import pymupdf as fitz

from typing import Callable, Any
from uuid import uuid4
import threading
import os

from core.calculate import *
import core.config as conf


class PDFImposer():
    def __init__(self) -> None:
        self.input_doc: fitz.Document | None = None
        self.output_doc: fitz.Document | None = None
        self.quantity_page: int | None = None

        self._current_task: threading.Thread | None = None
        self._cancel_flag: threading.Event = threading.Event()
        self._lock: threading.Lock = threading.Lock()
        self._current_task_id: str | None = None

        self.update_params()

    def __del__(self) -> None:
        if self.input_doc:
            self.input_doc.close()
            self.input_doc = None
        if self.output_doc:
            self.output_doc.close()
            self.output_doc = None

    def load_doc(self, path: str, 
                 callback: Callable[[Any], None] | None = None):
        self._cancel_async_task()
        
        if self.input_doc:
            self.input_doc.close()
        self.input_doc = fitz.open(path)
        self.update_doc_async(callback)

    def update_params(
            self, rows: int = 2, cols: int = 2, margin: int = 15, 
            format: str = "A4_portrait", show_cut_lines: bool = True, 
            show_margin_lines: bool = True, show_blocks_lines: bool = False, 
            thickness_lines: int = 1, color_lines: tuple[float, ...] = (0.5, 0.5, 0.5), 
            dashes_pattern: str = "[4 2] 0", blocks_are_vertical: bool = False, 
            quantity_pages_for_part: int = 0) -> None:
        
        if rows * cols % 2 == 1:
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

    def get_preview(self, page_num: int, scale: int = 1,
                    indexation_size: int | None = None) -> tuple[list, tuple[int]]:
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        if self.output_doc is None and self._current_task and self._current_task.is_alive():
            self._current_task.join()
        
        temp_doc, total_pages = calculate_doc(self.input_doc, self.params, 
                                              page_num=page_num,
                                              indexation_size=indexation_size)
        self.quantity_page = total_pages

        if temp_doc is None or len(temp_doc) == 0:
            return None, None
        
        try:
            return calculate_texture_data(temp_doc[0], scale, self.params.format)
        finally:
            try: 
                if temp_doc: temp_doc.close()
            except: pass

    def get_formatted_source_page(self, page_num: int | None, 
                                  scale: int = 1) -> tuple[list, tuple[int]]:
        if self.input_doc is None:
            raise ValueError("No PDF document loaded")
        
        if page_num >= len(self.input_doc):
            raise ValueError("page_num >= len(self.input_doc)!!!")
        
        page_size = conf.formats[self.params.format]
        page = fitz.open().new_page(width=page_size[0], height=page_size[1])
        draw_formatting_page(page, self.params, self.input_doc, page_num)
        return calculate_texture_data(page, scale, self.params.format)

    def update_doc(self) -> None:
        if self._current_task and self._current_task.is_alive():
            self._current_task.join()
            return
        
        self.output_doc, total_pages = calculate_doc(self.input_doc, self.params)
        self.quantity_page = total_pages

    def _get_split(self) -> tuple[fitz.Document, fitz.Document]:
        output_1 = fitz.open()
        output_2 = fitz.open()

        for i in range(0, self.quantity_page, 2):
            ind_1, ind_2 = i, self.quantity_page-i-1
            output_1.insert_pdf(self.output_doc, from_page=ind_1, to_page=ind_1)
            output_2.insert_pdf(self.output_doc, from_page=ind_2, to_page=ind_2)
        
        return output_1, output_2

    def export_doc(self, path, split=False) -> None:
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

    def get_preview_async(self, page_num: int, scale: int = 1, 
                          indexation: bool = False, 
                          callback: Callable[[Any], None] | None = None) -> None:
        def worker():
            try:
                result = self.get_preview(page_num, scale, indexation)
                if callback:
                    callback(result)
            except Exception as e:
                if callback:
                    callback(None)
        
        thread = threading.Thread(target=worker, daemon=False)
        thread.start()

    def update_doc_async(self, 
            callback: Callable[[bool, str | None], None] | None = None) -> None:
        """
        Асинхронное обновление. Заменяет предыдущую задачу.
        callback вызывается с (success: bool, error: str)
        """
        if self.input_doc is None:
            if callback:
                callback(False, "No PDF document loaded")
            return
        
        self._cancel_async_task()
        
        task_id = str(uuid4())
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

    def _cancel_async_task(self) -> None:
        if self._current_task and self._current_task.is_alive():
            self._cancel_flag.set()

    def wait_for_completion(self, timeout: float | None = None) -> bool:
        if self._current_task is None:
            return True
        
        if self._current_task.is_alive():
            self._current_task.join(timeout)
        
        if self._current_task is not None:
            return not self._current_task.is_alive()
        return True
    
    def is_processing(self) -> bool:
        return self._current_task is not None and self._current_task.is_alive()
    
    def get_formats(self) -> list[str]:
        return list(conf.formats.keys())
    