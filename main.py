import dearpygui.dearpygui as dpg

from core import PDFImposer
from ui import *


class PDF2BookApp:
    def __init__(self):
        self.pdf_path = None
        self.pdf_imposer = PDFImposer()

        self.theme = conf.selected_theme
        self.font = conf.selected_font
        self.current_page = 1
        
    def log_message(self, msg=None):
        if msg: dpg.set_value("log_output", msg)
        else: dpg.set_value("log_output", "")

    def run(self):
        dpg.create_context()
        
        dpg.create_viewport(**conf.viewport_options)

        dpg.set_exit_callback(self.close)

        create_main_window(self)
        register_callbacks(self)
        register_keyboards(self)
        register_themes(self)
        
        dpg.set_primary_window("primary_window", True)
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
    
    def close(self):
        conf.selected_font = self.font
        conf.selected_theme = self.theme
        conf.save()
        print("Завершение...")
        
        del self.pdf_imposer
        dpg.stop_dearpygui()


if __name__ == "__main__":
    app = PDF2BookApp()
    app.run()