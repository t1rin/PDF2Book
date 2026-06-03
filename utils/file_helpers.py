"""Работа с файлами и диалогами выбора"""

import os
from pathlib import Path
from tkinter import filedialog, Tk
import fitz

class FileDialogHelper:
    """Управление диалогами выбора файлов через tkinter"""
    
    @staticmethod
    def open_pdf_file():
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        filepath = filedialog.askopenfilename(
            title="Выберите PDF файл",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        root.destroy()
        return filepath if filepath else None
    
    @staticmethod
    def save_pdf_file(default_name="output.pdf"):
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        filepath = filedialog.asksaveasfilename(
            title="Сохранить PDF как",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_name
        )
        
        root.destroy()
        return filepath if filepath else None


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

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def is_type(path, type):
    return path.split(".")[-1] == type