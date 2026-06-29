"""Работа с файлами и диалогами выбора"""

import os
import sys
import glob
import platform
from pathlib import Path
from tkinter import filedialog, Tk
import pymupdf as fitz


class FileDialogHelper:
    _root = None
    
    @classmethod
    def _get_root(cls):
        if cls._root is None:
            cls._root = Tk()
            cls._root.withdraw()
            cls._root.attributes('-topmost', True)
        return cls._root
    
    @classmethod
    def open_pdf_file(cls):
        root = cls._get_root()
        root.lift()
        root.focus_force()
        
        filepath = filedialog.askopenfilename(
            title="Выберите PDF файл",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        return filepath if filepath else None
    
    @classmethod
    def save_pdf_file(cls, default_name="output.pdf"):
        root = cls._get_root()
        root.lift()
        root.focus_force()
        
        filepath = filedialog.asksaveasfilename(
            title="Сохранить PDF как",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_name
        )
        
        return filepath if filepath else None
    
    @classmethod
    def cleanup(cls):
        """Вызовите при завершении программы"""
        if cls._root:
            cls._root.destroy()
            cls._root = None

class PDFInfo:
    """Получение информации о PDF файле"""
    
    @staticmethod
    def get_page_count(pdf_path):
        try:
            doc = fitz.open(pdf_path)
            count = len(doc)
            doc.close()
            return count
        except Exception as e:
            print(f"Ошибка при чтении PDF: {e}")
            return 0
    
    @staticmethod
    def get_page_size(pdf_path, page_num=0):
        try:
            doc = fitz.open(pdf_path)
            page = doc[page_num]
            rect = page.rect
            doc.close()
            return rect.width, rect.height
        except Exception as e:
            print(f"Ошибка получения размера страницы: {e}")
            return 0, 0
    
    @staticmethod
    def get_pdf_metadata(pdf_path):
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            return metadata
        except Exception as e:
            print(f"Ошибка получения метаданных: {e}")
            return {}
    
    @staticmethod
    def validate_and_get_info(pdf_path):
        """Проверить PDF и вернуть информацию"""
        if not os.path.exists(pdf_path):
            return None, "Файл не существует"
        
        if not pdf_path.lower().endswith('.pdf'):
            return None, "Файл не является PDF"
        
        page_count = PDFInfo.get_page_count(pdf_path)
        if page_count == 0:
            return None, "Не удалось прочитать PDF или файл пуст"
        
        info = {
            'path': pdf_path,
            'pages': page_count,
            'filename': os.path.basename(pdf_path),
            'size_mb': os.path.getsize(pdf_path) / (1024 * 1024)
        }
        
        return info, None

def normalize_path(path):
    return path.replace('\\', os.sep).replace('/', os.sep)

def resource_path(relative_path):
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).resolve().parent.parent
        
    path = Path(normalize_path(relative_path))
    
    clean_parts = [part for part in path.parts if part not in ('.', '..', '')]
    clean_path = Path(*clean_parts)
    
    final_path = base_path / clean_path
    
    final_path = os.path.abspath(final_path)
    
    return str(final_path)

def get_fonts():
    paths2fonts = glob.glob(resource_path(os.path.join("assets", "fonts", "*.ttf")))
    fonts = [os.sep.join(font.split(os.sep)[-3::1]) for font in paths2fonts]
    print(fonts)
    return fonts

def os_type():
    return platform.system()

def is_type(path, type):
    return path.split(".")[-1] == type